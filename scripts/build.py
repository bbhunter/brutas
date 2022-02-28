#!/usr/bin/env python3

import argparse
import multiprocessing
import os
import pathlib
import tempfile
import sys

import config
import logging
import main
from main import imports


sys.path.insert(0, str(pathlib.Path(__file__).parent.absolute()))


def entry_point():
    parser = argparse.ArgumentParser(description='Brutas build script')
    parser.add_argument('-p', '--path', default='main.Basic', help='Class path. [Default: main.Basic]')
    parser.add_argument('-t', '--temporary-dir', default=None, help='Temporary directory path. [Default: auto]')
    parser.add_argument('-o', '--output-dir', default='.', help='Output directory path. [Default: .]')
    parser.add_argument('--cores', default=None, help='Number of cores to be used for sorting. [Default: auto]')
    parser.add_argument('--memory', default='80%', help='Percentage of memory to be used for sorting. [Default: 80%%]')
    parser.add_argument('--debug', action='store_const', dest='loglevel', const=logging.DEBUG, default=logging.INFO, help='Enable debug level logging')
    args = parser.parse_args()
    clss = imports.class_import(args.path)
    main.init_logger(args.loglevel)
    if args.temporary_dir is None:
        if 'TMP_DIR' in os.environ:
            args.temporary_dir = os.environ['TMP_DIR']
        else:
            args.temporary_dir = tempfile.mkdtemp()
    if args.cores is None:
        cpu_count = multiprocessing.cpu_count()
        if cpu_count > 1:
            args.cores = str(cpu_count - 1)
    combinator = clss(config, args)
    combinator.run()


if __name__ == '__main__':
    entry_point()
