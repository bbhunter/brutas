#!/bin/bash

echo "Preparing keyword lists..."
sort -f brutas-passwords-keywords-more-common.txt > sorted1
sort -f brutas-passwords-keywords-less-common.txt > sorted2
comm -13 sorted1 sorted2 > brutas-passwords-keywords-less-common.txt
rm brutas-passwords-keywords-more-common.txt sorted2
mv sorted1 brutas-passwords-keywords-more-common.txt

echo "Sorting basic lists..."
sort -f brutas-passwords-classics.txt | sort -f > a1.tmp
cat brutas-passwords-keywords-more-common.txt | sort -f > a2.tmp
sort -f brutas-passwords-unique.txt | sort -f > a3.tmp
sort -f brutas-passwords-closekeys.txt | sort -f > a4.tmp
cat brutas-passwords-keywords-less-common.txt | sort -f > a5.tmp
sort -f brutas-passwords-numbers.txt | sort -f > a6.tmp

echo "Generating sets based on usernames..."
hashcat -r ./src/brutas-passwords-extra.rule --stdout ./brutas-usernames-small.txt | sort -f | uniq  > a7.tmp
hashcat -r ./src/brutas-passwords-years.rule --stdout ./brutas-usernames-small.txt | sort -f | uniq  > a8.tmp
hashcat -r ./src/brutas-passwords-complex.rule --stdout ./brutas-usernames-small.txt | sort -f | uniq > a9.tmp
hashcat -r ./src/brutas-passwords-hax0r.rule --stdout ./brutas-usernames-small.txt | sort -f | uniq > a10.tmp

echo "Parsing keywords with extra rules..."
hashcat -r ./src/brutas-passwords-years.rule --stdout ./brutas-passwords-keywords-more-common.txt | sort -f | uniq  > a11.tmp
hashcat -r ./src/brutas-passwords-years.rule --stdout ./brutas-passwords-keywords-less-common.txt | sort -f | uniq  > a12.tmp
hashcat -r ./src/brutas-passwords-hax0r.rule --stdout ./brutas-passwords-keywords-more-common.txt | sort -f | uniq > a13.tmp
hashcat -r ./src/brutas-passwords-hax0r.rule --stdout ./brutas-passwords-keywords-less-common.txt | sort -f | uniq > a14.tmp

echo "Removing duplicates..."
cp a1.tmp dict.tmp
cp a1.tmp b1.tmp

for i in $(seq 2 14); do
    comm -13 dict.tmp a$i.tmp > b$i.tmp
    cat b$i.tmp >> dict.tmp
    sort -f -o dict.tmp dict.tmp
done

# Change the order here:

echo "Building final lists..."
cat b1.tmp b2.tmp b3.tmp > brutas-passwords-5k.txt
cat brutas-passwords-5k.txt b4.tmp b7.tmp > brutas-passwords-10k.txt
cat brutas-passwords-10k.txt b5.tmp b6.tmp b9.tmp b10.tmp b13.tmp > brutas-passwords-40k.txt
cat brutas-passwords-40k.txt b14.tmp b8.tmp b11.tmp b12.tmp > brutas-passwords-400k.txt

echo "Cleaning up..."
rm *.tmp

echo "Generating subdomains..."
cat brutas-subdomains-keywords.txt > brutas-subdomains-3k.txt
cat brutas-subdomains-extra.txt >> brutas-subdomains-3k.txt
cat brutas-subdomains-3k.txt > brutas-subdomains-250k.txt
hashcat -r ./src/brutas-subdomains-keywords.rule --stdout ./brutas-subdomains-keywords.txt >> brutas-subdomains-250k.txt

echo "Done!"