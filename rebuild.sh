#!/bin/bash

hashcat -r ./brutas-passwords-years.rule --stdout ./brutas-passwords-1.txt > brutas-passwords-1-years.txt
hashcat -r ./brutas-passwords-years.rule --stdout ./brutas-passwords-2.txt > brutas-passwords-2-years.txt
hashcat -r ./brutas-passwords-hax0r.rule --stdout ./brutas-passwords-1.txt | sort | uniq > brutas-passwords-1-hax0r.txt
hashcat -r ./brutas-passwords-hax0r.rule --stdout ./brutas-passwords-2.txt | sort | uniq > brutas-passwords-2-hax0r.txt
hashcat -r ./brutas-passwords-years.rule --stdout ./brutas-usernames.txt > brutas-passwords-usernames-years.txt
hashcat -r ./brutas-passwords-hax0r.rule --stdout ./brutas-usernames.txt > brutas-passwords-usernames-hax0r.txt
cat brutas-passwords-usernames-years.txt \
    brutas-passwords-usernames-hax0r.txt | sort | uniq >> brutas-passwords-3.txt
rm brutas-passwords-usernames-*
cat brutas-passwords-1-hax0r.txt \
    brutas-passwords-1-years.txt \
    brutas-passwords-1.txt \
    brutas-passwords-2-hax0r.txt \
    brutas-passwords-2-years.txt \
    brutas-passwords-2.txt \
    brutas-passwords-3.txt | sort | uniq > brutas-passwords-combined.txt