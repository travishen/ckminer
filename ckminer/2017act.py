#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from . import _driver_path, _writer_csv_path, _history_path
from .miner import Miner
import sys


def parse_args(args):
    parser = ArgumentParser()
    parser.add_argument('--user', help='ck user name here.', required=True)
    parser.add_argument('--password', help='cd user password here', required=True)
    return parser.parse_args()


def main(args=None):
    args = parse_args(args)
    if args.user and args.password:
        run(args.user, args.password)


def run(user, password):
    brief = '''
            Welcome to 2017 CK101\'s activity, check rules at this link:
            https://ck101.com/thread-4133697-1-1.html
            '''
    print(brief)
    miner = Miner(_driver_path, _writer_csv_path, _history_path)
    miner.login(user, password)
    miner.collect_topic_rewards()
    miner.driver.quit()


if __name__ == '__main__':
    main(sys.argv[1:])
