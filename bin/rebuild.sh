#!/bin/bash

TEMP_DIR=$(mktemp -d)

echo "Preparing keyword lists..."
sort -f keywords/brutas-en-common.txt > sorted1
sort -f keywords/brutas-en-less.txt > sorted2
comm -13 sorted1 sorted2 > keywords/brutas-en-less.txt
rm keywords/brutas-en-common.txt sorted2
mv sorted1 keywords/brutas-en-common.txt

echo "Generating sets based on usernames..."
hashcat --stdout -r rules/brutas-passwords-multi.rule -r rules/brutas-passwords-extra.rule brutas-usernames-small.txt | sort -f | uniq > $TEMP_DIR/.usernames-small-extra.tmp
hashcat --stdout -r rules/brutas-passwords-multi.rule -r rules/brutas-passwords-hax0r.rule brutas-usernames-small.txt | sort -f | uniq > $TEMP_DIR/.usernames-small-hax0r.tmp
hashcat --stdout -r rules/brutas-passwords-multi.rule -r rules/brutas-passwords-years.rule brutas-usernames.txt | sort -f | uniq > $TEMP_DIR/.usernames-years.tmp
hashcat --stdout -r rules/brutas-passwords-multi.rule -r rules/brutas-passwords-extra.rule brutas-usernames.txt | sort -f | uniq > $TEMP_DIR/.usernames-extra.tmp
hashcat --stdout -r rules/brutas-passwords-multi.rule -r rules/brutas-passwords-hax0r.rule brutas-usernames.txt | sort -f | uniq > $TEMP_DIR/.usernames-hax0r.tmp

echo "Parsing keywords with extra rules..."
hashcat --stdout -r rules/brutas-passwords-multi.rule -r rules/brutas-passwords-years.rule keywords/brutas-en-common.txt | sort -f | uniq > $TEMP_DIR/.more-common-years.tmp
hashcat --stdout -r rules/brutas-passwords-multi.rule -r rules/brutas-passwords-years.rule keywords/brutas-en-less.txt | sort -f | uniq > $TEMP_DIR/.less-common-years.tmp
hashcat --stdout -r rules/brutas-passwords-multi.rule -r rules/brutas-passwords-extra.rule keywords/brutas-en-common.txt | sort -f | uniq > $TEMP_DIR/.more-common-extra.tmp
hashcat --stdout -r rules/brutas-passwords-multi.rule -r rules/brutas-passwords-extra.rule keywords/brutas-en-less.txt | sort -f | uniq > $TEMP_DIR/.less-common-extra.tmp
hashcat --stdout -r rules/brutas-passwords-multi.rule -r rules/brutas-passwords-hax0r.rule keywords/brutas-en-common.txt | sort -f | uniq > $TEMP_DIR/.more-common-hax0r.tmp
hashcat --stdout -r rules/brutas-passwords-multi.rule -r rules/brutas-passwords-hax0r.rule keywords/brutas-en-less.txt | sort -f | uniq > $TEMP_DIR/.less-common-hax0r.tmp

# Change the order here:

echo "Building final lists..."
cat \
    brutas-usernames.txt \
    brutas-passwords-classics.txt \
    brutas-passwords-closekeys.txt \
    | sort -f | uniq > brutas-passwords-1-x-small.txt
cat \
    brutas-passwords-1-x-small.txt \
    brutas-passwords-top.txt \
    brutas-passwords-unique.txt \
    | sort -f | uniq > brutas-passwords-2-small.txt
cat \
    brutas-passwords-2-small.txt \
    brutas-passwords-numbers.txt \
    $TEMP_DIR/.usernames-years.tmp \
    $TEMP_DIR/.usernames-small-extra.tmp \
    $TEMP_DIR/.usernames-small-hax0r.tmp \
    | sort -f | uniq > brutas-passwords-3-medium.txt
cat \
    brutas-passwords-3-medium.txt \
    keywords/brutas-en-common.txt \
    $TEMP_DIR/.usernames-extra.tmp \
    $TEMP_DIR/.usernames-hax0r.tmp \
    | sort -f | uniq > brutas-passwords-4-large.txt
cat \
    brutas-passwords-4-large.txt \
    keywords/brutas-en-less.txt \
    $TEMP_DIR/.less-common-extra.tmp \
    $TEMP_DIR/.less-common-hax0r.tmp \
    $TEMP_DIR/.less-common-years.tmp \
    $TEMP_DIR/.more-common-extra.tmp \
    $TEMP_DIR/.more-common-hax0r.tmp \
    $TEMP_DIR/.more-common-years.tmp \
    | sort -f | uniq > brutas-passwords-5-x-large.txt

echo "Generating subdomains..."
cat keywords/brutas-subdomains.txt > brutas-subdomains-1-small.txt
cat keywords/brutas-subdomains-extra.txt >> brutas-subdomains-1-small.txt
cat brutas-subdomains-1-small.txt > brutas-subdomains-2-large.txt
hashcat --stdout -r rules/brutas-subdomains.rule keywords/brutas-subdomains.txt >> brutas-subdomains-2-large.txt

echo "Cleaning up..."
rm -rf $TEMP_DIR

echo "Done!"