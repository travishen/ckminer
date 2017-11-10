#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from . import _driver_path
from .miner import Miner
import sys


def parse_args(args):
    parser = ArgumentParser()
    parser.add_argument('--user', help='ck user name here.', required=True)
    parser.add_argument('--pwd', help='ck user password here.', required=True)
    parser.add_argument('--act2017', help='present to join 2017 activity.', action='store_true')
    parser.add_argument('--space', help='set numbers to visit user spaces.', nargs='?', const=5, type=int)
    return parser.parse_args()


def main(args=None):
    args = parse_args(args)
    if args.user and args.pwd:
        run(args)


def run(args):
    miner = Miner(_driver_path, Miner.BLOCK_IMG_PLUG_PATH)
    if miner.login(args.user, args.pwd):
        if args.space:
            brief = '''          
            -----------------------------------------------------------
            Randomly visiting user spaces for collecting rewards. 
            You can set the limit you want to browsing after
            "--space" argument.
            -----------------------------------------------------------

            '''
            print(brief)
            miner.collect_space_rewards(args.space)

        if args.act2017:
            brief = '''          
            -----------------------------------------------------------
            Welcome to 2017 CK101\'s activity, check rules at this link:
            https://ck101.com/thread-4133697-1-1.html
            -----------------------------------------------------------
            
            '''
            print(brief)
            miner.collect_topic_rewards()
    miner.driver.quit()


if __name__ == '__main__':
    main(sys.argv[1:])
