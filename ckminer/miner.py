#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ChromeOptions
import requests
from lxml import html
import json
import os
import datetime
import time


class Miner(object):

    TITLE = '卡提諾論壇'
    LOGIN_PAGE = 'https://ck101.com/member.php?mod=logging&action=login'
    TOPIC_REWORD_POINTS = 5
    TOPIC_REWORD_PAGES = 20

    BLOCK_IMG_PLUG_PATH = None

    def __init__(self, driver_path, plugin_path=None):
        self.driver = Miner.create_driver(driver_path, plugin_path=plugin_path)

    @staticmethod
    def create_driver(driver_path, **options):
        plugin_path = options.get('plugin_path', None)
        opt = ChromeOptions()
        if plugin_path:
            opt.add_extension(plugin_path)
        driver = webdriver.Chrome(driver_path, chrome_options=opt)
        return driver

    def login(self, user, password):
        print('User try login...')
        self.driver.get(Miner.LOGIN_PAGE)
        ipt_user = self.find('input[name="username"]')
        ipt_pwd = self.find('input[name="password"]')
        ipt_user.send_keys(user)
        ipt_pwd.send_keys(password)
        btn_submit = self.wait_click('button[name="loginsubmit"]')
        btn_submit.click()
        if not self.wait_url_change():
            print('Login Failed... Please retry...')
            return False
        return True

    def collect_space_rewards(self, limit):
        users = Quester.get_top_user()
        links = []
        visited = 0
        # start from most popular user
        self.driver.get(Quester.USER_PAGE % users[0])
        if self.wait_visible('visitor_content', by='id', wait=5):
            links += [(e.get_attribute('href'), e.get_attribute('title'))
                      for e in self.find('#visitor_content p>a', single=False)]
            while visited <= limit:
                if len(links) <= 10:
                    links += [(e.get_attribute('href'), e.get_attribute('title'))
                              for e in self.find('#visitor_content p>a', single=False)]
                for link in links:
                    print('Visiting %s...' % link[1])
                    self.driver.get(link[0])
                    time.sleep(1)
                    if self.wait_visible('visitor_content', by='id', wait=5):
                        visited += 1
                    links.remove(link)

    def collect_topic_rewards(self):
        links = []
        new_history = []
        history = User.load_history()
        rewards = 0
        full = rewards >= Miner.TOPIC_REWORD_PAGES * Miner.TOPIC_REWORD_POINTS

        # load popular writer from index
        names = Quester.get_writer_from_index()
        for writer in Writer.load_writer(names=names):
            print('Collecting latest post from %s...' % writer.username)
            links += Quester.get_top_post(writer.uid, count=10)

        while not full:
            if len(links) == 0:
                # load more ck-writer from writer.csv
                print('All posts drained... Loading more posts...')
                for writer in Writer.load_writer(ckwriter=True):
                    links += Quester.get_top_post(writer.uid, count=10)
                full = True
            for link in links:
                try:
                    if link in history or link in new_history:
                        continue
                    self.driver.get(link)
                    self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
                    if not self.wait_visible('div.topicReward5Progress'):
                        print('Not an active page.')
                        continue
                    locator = 'div.topicReward5Progress.getRewards'
                    if self.wait_visible(locator):
                        element = self.wait_click(locator)
                        element.click()
                    if self.wait_visible('div.popContent.popContent__2017activity'):
                        result = self.find('p.topTitle.topTitle__2017activity')
                        if u'＋5' in result.text:
                            rewards += Miner.TOPIC_REWORD_POINTS
                            print('+5 topic rewards! Now you have %s...' % rewards)
                        elif u'僅能領取一次' in result.text:
                            print('Post already drained...')
                        elif u'達到簽到上限' in result.text:
                            print('Pocket full today!')
                            full = True
                            break
                except:
                    pass
                finally:
                    new_history.append(link)
                    links.remove(link)
        User.create_history(new_history)

    def wait_url_change(self, wait=10):
        wait = WebDriverWait(self.driver, wait)
        return wait.until(EC.title_contains(Miner.TITLE))

    def wait_visible(self, locator, by='css', wait=10):
        wait = WebDriverWait(self.driver, wait)
        element = None
        try:
            if by == 'css':
                element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, locator)))
            if by == 'id':
                element = wait.until(EC.visibility_of_element_located((By.ID, locator)))
        except TimeoutException:
            return False
        finally:
            return element

    def wait_click(self, locator, by='css', wait=10):
        wait = WebDriverWait(self.driver, wait)
        element = None
        try:
            if by == 'css':
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, locator)))
            if by == 'id':
                element = wait.until(EC.element_to_be_clickable((By.ID, locator)))
        except TimeoutException:
            return False
        finally:
            return element

    def find(self, locator, by='css', single=True):
        element = None
        try:
            if by == 'css':
                if single:
                    element = self.driver.find_element_by_css_selector(locator)
                else:
                    element = self.driver.find_elements_by_css_selector(locator)
            if by == 'id':
                if single:
                    element = self.driver.find_element_by_id(locator)
                else:
                    element = self.driver.find_element_by_id(locator)
        except:
            return False
        finally:
            return element


class Quester(object):

    INDEX = 'https://ck101.com'
    HOME_PAGE = 'https://ck101.com/home.php'
    API_PAGE = 'http://ck101.com/api.php'
    USER_PAGE = 'https://ck101.com/space-username-%s.html'
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

    @staticmethod
    def get_top_user():
        res = requests.get(Quester.INDEX, headers=Quester.HEADERS)
        parsed_page = html.fromstring(res.content)
        users = parsed_page.xpath('//div[@class="rankBoardWrapper"]//a/@title')
        return users


class Writer(object):

    CSV_PATH = None

    def __init__(self, uid=None, icon=None, username=None):
        self.uid = uid
        self.icon = icon
        self.username = username

    @staticmethod
    def ckwriter_filter(writers, icon=True):
        for writer in writers:
            if writer.icon == (1 if icon else 0):
                yield writer

    @staticmethod
    def name_filter(writers, names):
        for writer in writers:
            if writer.username in names:
                yield writer

    @classmethod
    def load_writer(cls, **filters):
        ckwriter = filters.get('ckwriter', None)
        names = filters.get('names', None)
        with open(cls.CSV_PATH, 'r') as csv:
            writers = json.load(csv, object_hook=Writer.hook)
        if ckwriter is not None:
            writers = Writer.ckwriter_filter(writers, ckwriter)
        if names:
            writers = Writer.name_filter(writers, names)
        return writers

    @classmethod
    def update_writer(cls, from_page=1, to_page=3):
        writers = []
        for page in range(from_page, to_page + 1):
            writers += Quester.get_writer_from_api(page)
        with open(cls.CSV_PATH, 'w') as csv:
            csv.write(json.dumps([writer.__dict__ for writer in writers]))
        print('Done.')

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

    HISTORY_PATH = None

    @classmethod
    def create_history(cls, links):
        if not links:
            return
        print('Storing browser history...')
        file_name = datetime.datetime.today().strftime('%Y%m%d%H%M')
        with open('%s\history_%s.csv' % (cls.HISTORY_PATH, file_name), 'w') as file:
            file.write('\n'.join(links))

    @classmethod
    def load_history(cls):
        links = []
        for filename in os.listdir(cls.HISTORY_PATH):
            with open('%s\%s' % (cls.HISTORY_PATH, filename), 'r') as file:
                links += file.read().splitlines()
        return links











