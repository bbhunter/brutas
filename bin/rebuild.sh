#!/bin/bash

echo "Preparing keyword lists..."
sort -f keywords/brutas-en-common.txt > sorted1
sort -f keywords/brutas-en-less.txt > sorted2
comm -13 sorted1 sorted2 > keywords/brutas-en-less.txt
rm keywords/brutas-en-common.txt sorted2
mv sorted1 keywords/brutas-en-common.txt

echo "Generating sets based on usernames..."
hashcat -r rules/brutas-passwords-extra.rule --stdout brutas-usernames-small.txt | sort -f | uniq  > usernames-small-extra.tmp
hashcat -r rules/brutas-passwords-years.rule --stdout brutas-usernames-small.txt | sort -f | uniq  > usernames-small-years.tmp
hashcat -r rules/brutas-passwords-complex.rule --stdout brutas-usernames-small.txt | sort -f | uniq > usernames-small-complex.tmp
hashcat -r rules/brutas-passwords-hax0r.rule --stdout brutas-usernames-small.txt | sort -f | uniq > usernames-small-hax0r.tmp

echo "Parsing keywords with extra rules..."
hashcat -r rules/brutas-passwords-years.rule --stdout keywords/brutas-en-common.txt | sort -f | uniq  > more-common-years.tmp
hashcat -r rules/brutas-passwords-years.rule --stdout keywords/brutas-en-less.txt | sort -f | uniq  > less-common-years.tmp
hashcat -r rules/brutas-passwords-hax0r.rule --stdout keywords/brutas-en-common.txt | sort -f | uniq > more-common-hax0r.tmp
hashcat -r rules/brutas-passwords-hax0r.rule --stdout keywords/brutas-en-less.txt | sort -f | uniq > less-common-hax0r.tmp

# Change the order here:

echo "Building final lists..."
cat \
    brutas-usernames.txt \
    brutas-passwords-classics.txt \
    | sort -f | uniq > brutas-passwords-1k.txt
cat \
    brutas-passwords-1k.txt \
    brutas-passwords-closekeys.txt \
    | sort -f | uniq > brutas-passwords-5k.txt
cat \
    brutas-passwords-5k.txt \
    keywords/brutas-en-common.txt \
    usernames-small-extra.tmp \
    | sort -f | uniq > brutas-passwords-10k.txt
cat \
    brutas-passwords-10k.txt \
    brutas-passwords-unique.txt \
    keywords/brutas-en-less.txt \
    brutas-passwords-numbers.txt \
    usernames-small-complex.tmp \
    usernames-small-hax0r.tmp \
    more-common-hax0r.tmp \
    | sort -f | uniq > brutas-passwords-50k.txt
cat \
    brutas-passwords-50k.txt \
    less-common-hax0r.tmp \
    usernames-small-years.tmp \
    more-common-years.tmp \
    less-common-years.tmp \
    | sort -f | uniq > brutas-passwords-400k.txt

echo "Cleaning up..."
rm *.tmp

echo "Generating subdomains..."
cat keywords/brutas-subdomains.txt > brutas-subdomains-3k.txt
cat keywords/brutas-subdomains-extra.txt >> brutas-subdomains-3k.txt
cat brutas-subdomains-3k.txt > brutas-subdomains-250k.txt
hashcat -r rules/brutas-subdomains.rule --stdout keywords/brutas-subdomains.txt >> brutas-subdomains-250k.txt

echo "Done!"