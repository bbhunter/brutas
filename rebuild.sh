#!/bin/bash

hashcat -r ./brutas-passwords-years.rule --stdout ./brutas-passwords-3k.txt > brutas-passwords-3k-years.txt
hashcat -r ./brutas-passwords-years.rule --stdout ./brutas-passwords-10k.txt > brutas-passwords-10k-years.txt
hashcat -r ./brutas-passwords-hax0r.rule --stdout ./brutas-passwords-3k.txt | uniq > brutas-passwords-3k-hax0r.txt
hashcat -r ./brutas-passwords-hax0r.rule --stdout ./brutas-passwords-10k.txt | uniq > brutas-passwords-10k-hax0r.txt
hashcat -r ./brutas-passwords-years.rule --stdout ./brutas-usernames.txt > brutas-passwords-adminz.txt
hashcat -r ./brutas-passwords-hax0r.rule --stdout ./brutas-usernames.txt | uniq >> brutas-passwords-adminz.txt
