#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import dirname, join
from .miner import Writer, User, Miner

# paths
_package_root = dirname(__file__)
_driver_path = join(_package_root, 'chromedriver.exe')
_history_path = join(_package_root, 'history')
_writer_csv_path = join(_package_root, 'writer.csv')
_block_image_plugin_path = join(_package_root, 'Block-image_v1.1.crx')

Writer.CSV_PATH = _writer_csv_path
User.HISTORY_PATH = _history_path
Miner.BLOCK_IMG_PLUG_PATH = _block_image_plugin_path


# expose functions
update_writer = Writer.update_writer

