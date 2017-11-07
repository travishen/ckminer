#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from .selenium import webdriver
from .selenium.webdriver.common.by import By
from .selenium.webdriver.support.ui import WebDriverWait
from .selenium.webdriver.support import expected_conditions as EC
from .selenium.common.exceptions import TimeoutException
import requests
from lxml import html
import json
import os
import datetime


class Miner(object):

    LOGIN_PAGE = 'https://ck101.com/member.php?mod=logging&action=login'
    TOPIC_REWORD_POINTS = 5

    def __init__(self, driver_path, writer_csv_path, history_path):
        self.driver = Miner.create_driver(driver_path)
        self.writer_csv_path = writer_csv_path
        self.history_path = history_path

    @staticmethod
    def create_driver(driver_path):
        driver = webdriver.Chrome(driver_path)
        return driver

    def login(self, user, password):
        self.driver.get(Miner.LOGIN_PAGE)
        ipt_user = self.find('input[name="username"]')
        ipt_pwd = self.find('input[name="password"]')
        ipt_user.send_keys(user)
        ipt_pwd.send_keys(password)
        btn_submit = self.wait_click('button[name="loginsubmit"]')
        btn_submit.click()

    def collect_topic_rewards(self):
        links = []
        new_history = []
        history = User.load_history(self.history_path)
        rewards = 0
        names = Quester.get_writer_from_index()
        for writer in Writer.load_writer(self.writer_csv_path, names=names):
            print('Collecting latest post from {}...'.format(writer.username))
            links += Quester.get_top_post(writer.uid, count=5)
        for link in links:
            if link in history:
                continue
            self.driver.get(link)
            self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
            try:
                if not self.wait_visible('div.topicReward5Progress'):
                    print('Not an active page.')
                    continue
                locator = 'div.topicReward5Progress.getRewards'
                if self.wait_visible(locator):
                    element = self.wait_click(locator)
                    element.click()
                if self.wait_visible('div.popContent.popContent__2017activity'):
                    result = self.find('p.topTitle.topTitle__2017activity')
                    if '＋5' in result.text:
                        rewards += Miner.TOPIC_REWORD_POINTS
                        print('+5 topic rewards! Now you have {}...'.format(rewards))
                    elif '僅能領取一次' in result.text:
                        print('Post already drained...')
                    elif '已達到簽到上限' in result.text:
                        print('Pocket full today!')
                        break
            except:
                pass
            finally:
                new_history.append(link)
        User.create_history(self.history_path, new_history)

    def wait_visible(self, locator, by='css'):
        wait = WebDriverWait(self.driver, 10)
        element = None
        try:
            if by == 'css':
                element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, locator)))
            elif by == 'id':
                element = wait.until(EC.visibility_of_element_located((By.ID, locator)))
        except TimeoutException:
            return False
        finally:
            return element

    def wait_click(self, locator, by='css'):
        wait = WebDriverWait(self.driver, 10)
        element = None
        try:
            if by == 'css':
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, locator)))
            elif by == 'id':
                element = wait.until(EC.element_to_be_clickable((By.ID, locator)))
        except TimeoutException:
            return False
        finally:
            return element

    def find(self, locator, by='css'):
        element = None
        try:
            if by == 'css':
                element = self.driver.find_element_by_css_selector(locator)
            elif by == 'id':
                element = self.driver.find_element_by_id(locator)
        except:
            return False
        finally:
            return element


class Quester(object):
    INDEX = 'https://ck101.com'
    HOME_PAGE = 'https://ck101.com/home.php'
    API_PAGE = 'http://ck101.com/api.php'
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    @staticmethod
    def get_writer_from_index():
        res = requests.get(Quester.INDEX, headers=Quester.HEADERS)
        parsed_page = html.fromstring(res.content)
        names = parsed_page.xpath('//p[@class="postInfo-author"]/a//text()')
        return names

    @staticmethod
    def get_writer_from_api(page):
        params = {
            'mod': 'loadwriter',
            'api': 'loadMore',
            'page': page
        }
        res = requests.get(Quester.API_PAGE, params=params, headers=Quester.HEADERS)
        dic = json.loads(res.content, object_hook=Writer.hook)
        return dic['data']

    @staticmethod
    def update_writer(csv, from_page=1, to_page=3):
        writers = []
        for page in range(from_page, to_page + 1):
            writers += Quester.get_writer_from_api(page)
        with open(csv, 'w') as csv:
            csv.write(json.dumps([writer.__dict__ for writer in writers]))
        print('Done.')

    @staticmethod
    def get_top_post(uid, count=1):
        params = {
            'mod': 'space',
            'do': 'thread',
            'uid': uid
        }
        res = requests.get(Quester.HOME_PAGE, params=params, headers=Quester.HEADERS)
        parsed_page = html.fromstring(res.content)
        links = parsed_page.xpath('//a[@class="title-spaceauthor "]/@href')
        return links[:count]


class Writer(object):
    def __init__(self, uid=None, icon=None, username=None):
        self.uid = uid
        self.icon = icon
        self.username = username

    @staticmethod
    def ckwriter_filter(writers, icon=True):
        for writer in writers:
            if writer.icon == 1 if icon else 0:
                yield writer

    @staticmethod
    def name_filter(writers, names):
        for writer in writers:
            if writer.username in names:
                yield writer

    @staticmethod
    def load_writer(csv, ckwriter=None, names=None):
        with open(csv, 'rb') as csv:
            writers = json.load(csv, object_hook=Writer.hook)
        if ckwriter is not None:
            return Writer.ckwriter_filter(writers, ckwriter)
        if names:
            return Writer.name_filter(writers, names)
        return writers

    @classmethod
    def hook(cls, dic):
        obj = cls()
        if dic.get('uid'):
            dic = {key: dic[key] for key in obj.__dict__}
            obj.__dict__.update(dic)
            return obj
        else:
            return dic


class User(object):

    @staticmethod
    def create_history(path, links):
        with open('{}\history_{}.csv'.format(path, datetime.datetime.today().strftime('%Y%m%d%H%M')), 'w') as file:
            file.write('\n'.join(links))

    @staticmethod
    def load_history(path):
        links = []
        for filename in os.listdir(path):
            with open('{}\{}'.format(path, filename), 'r') as file:
                links += file.read().splitlines()
        return links











