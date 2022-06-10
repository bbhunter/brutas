#!/bin/sh

scripts/build.py -p main.BasicPasswords -t ./tmp
scripts/build.py -p main.ExtendedPasswords -t ./tmp
scripts/build.py -p main.Subdomains -t ./tmp
scripts/build.py -p main.Extensions -t ./tmp
scripts/build.py -p main.HttpWordsPlainCommon -t ./tmp
scripts/build.py -p main.HttpWordsSuffixesCommon -t ./tmp
scripts/build.py -p main.HttpWordsDoubleCommon -t ./tmp
scripts/build.py -p main.HttpWordsPlainAll -t ./tmp
scripts/build.py -p main.HttpWordsSuffixesAll -t ./tmp
scripts/build.py -p main.HttpWordsDoubleAll -t ./tmp
