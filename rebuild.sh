#!/bin/bash

hashcat -r ./brutas-passwords-years.rule --stdout ./brutas-passwords-1.txt > brutas-passwords-1-years.txt
hashcat -r ./brutas-passwords-years.rule --stdout ./brutas-passwords-2.txt > brutas-passwords-2-years.txt
hashcat -r ./brutas-passwords-hax0r.rule --stdout ./brutas-passwords-1.txt | uniq > brutas-passwords-1-hax0r.txt
hashcat -r ./brutas-passwords-hax0r.rule --stdout ./brutas-passwords-2.txt | uniq > brutas-passwords-2-hax0r.txt
hashcat -r ./brutas-passwords-years.rule --stdout ./brutas-usernames.txt > brutas-passwords-3.txt
hashcat -r ./brutas-passwords-hax0r.rule --stdout ./brutas-usernames.txt | uniq >> brutas-passwords-3.txt
