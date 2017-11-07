#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import dirname, join
from .miner import Miner

# paths
_package_root = dirname(__file__)
_driver_path = join(_package_root, 'chromedriver.exe')
_history_path = join(_package_root, 'history')
_writer_csv_path = join(_package_root, 'writer.csv')