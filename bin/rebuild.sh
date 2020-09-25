#!/bin/bash

echo "Preparing keyword lists..."
sort -f brutas-passwords-keywords-en-more-common.txt > sorted1
sort -f brutas-passwords-keywords-en-less-common.txt > sorted2
comm -13 sorted1 sorted2 > brutas-passwords-keywords-en-less-common.txt
rm brutas-passwords-keywords-en-more-common.txt sorted2
mv sorted1 brutas-passwords-keywords-en-more-common.txt

echo "Generating sets based on usernames..."
hashcat -r src/brutas-passwords-extra.rule --stdout brutas-usernames-small.txt | sort -f | uniq  > usernames-small-extra.tmp
hashcat -r src/brutas-passwords-years.rule --stdout brutas-usernames-small.txt | sort -f | uniq  > usernames-small-years.tmp
hashcat -r src/brutas-passwords-complex.rule --stdout brutas-usernames-small.txt | sort -f | uniq > usernames-small-complex.tmp
hashcat -r src/brutas-passwords-hax0r.rule --stdout brutas-usernames-small.txt | sort -f | uniq > usernames-small-hax0r.tmp

echo "Parsing keywords with extra rules..."
hashcat -r src/brutas-passwords-years.rule --stdout brutas-passwords-keywords-en-more-common.txt | sort -f | uniq  > more-common-years.tmp
hashcat -r src/brutas-passwords-years.rule --stdout brutas-passwords-keywords-en-less-common.txt | sort -f | uniq  > less-common-years.tmp
hashcat -r src/brutas-passwords-hax0r.rule --stdout brutas-passwords-keywords-en-more-common.txt | sort -f | uniq > more-common-hax0r.tmp
hashcat -r src/brutas-passwords-hax0r.rule --stdout brutas-passwords-keywords-en-less-common.txt | sort -f | uniq > less-common-hax0r.tmp

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
    brutas-passwords-keywords-en-more-common.txt \
    usernames-small-extra.tmp \
    | sort -f | uniq > brutas-passwords-10k.txt
cat \
    brutas-passwords-10k.txt \
    brutas-passwords-unique.txt \
    brutas-passwords-keywords-en-less-common.txt \
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
cat brutas-subdomains-keywords.txt > brutas-subdomains-3k.txt
cat brutas-subdomains-extra.txt >> brutas-subdomains-3k.txt
cat brutas-subdomains-3k.txt > brutas-subdomains-250k.txt
hashcat -r src/brutas-subdomains-keywords.rule --stdout brutas-subdomains-keywords.txt >> brutas-subdomains-250k.txt

echo "Done!"