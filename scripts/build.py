#!/usr/bin/env python3

import argparse
import os
import pathlib
import tempfile
import sys

import config
import logging
import main
from main import imports


if 'TMP_DIR' in os.environ:
    TMP_DIR = os.environ['TMP_DIR']
else:
    TMP_DIR = tempfile.mkdtemp()


sys.path.insert(0, str(pathlib.Path(__file__).parent.absolute()))


def entry_point():
    parser = argparse.ArgumentParser(description='Brutas build script')
    parser.add_argument('-p', '--path', default='main.Basic', help='Class path')
    parser.add_argument('-t', '--temporary-dir', default=TMP_DIR, help='Temporary directory path')
    parser.add_argument('--debug', action='store_const', dest='loglevel', const=logging.DEBUG, default=logging.INFO, help='Enable debug level logging')
    args = parser.parse_args()
    clss = imports.class_import(args.path)
    main.init_logger(args.loglevel)
    top_dir = str(pathlib.Path(__file__).parent.parent.absolute())
    combinator = clss(config.RULES, config.WORDLISTS, config.COMBINATOR_PATH, config.RLI2_PATH, args.temporary_dir, top_dir)
    combinator.run()


if __name__ == '__main__':
    entry_point()
