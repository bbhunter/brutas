#!/usr/bin/env bash

TMP_DIR=tmp

show_help() {
    echo -e "usage: $(basename "$0") [-h] [-t]\n\nOptional arguments:\n\t-h\t\tShow this help message and exit\n\t-t\t\tTemporary directory path [Default: $TMP_DIR]"
}

while getopts "t:h" opt; do
    case "$opt" in
        t) TMP_DIR=$OPTARG;;
        h) show_help; exit 0;;
        ?) show_help; exit 1;;
    esac
done

mkdir -p $TMP_DIR
wordz -p src/classes/passwords.py::CustomPasswords -t $TMP_DIR
