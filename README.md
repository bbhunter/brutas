# brutas

> Wordlists handcrafted with ♥

## Introduction

### `wordlists/passwords`

* `{1-7}-*.txt` - passwords generated using international keywords, hashcat rules and string partials
* `classics.txt` - typical admin passwords based on roles (test, admin), words (password, secret) or "funny" ones (like `letmein` or `trustno1`)
* `patterns.txt` - close key combinations or simple phrases (e.g. `abcd`) combined with capitalization, numbers, repetitions etc.
* `top.txt` - is a list composed of most popular user passwords found in leaks, doesn't contain close keys or any more sophisticated combinations
* `unique.txt` - passwords which are complex enough to be used as independent passwords and are rarely mixed with any extra characters, usually related to pop-culture or sports (e.g. `apollo13`, `9inchnails`, `ronaldo7`)
* `numbers.txt` - a small list of numbers used in passwords (e.g. dates, math constants)
* `custom.txt` - put your custom keywords here and generate the wordlist using `custom.sh`, the result will be in `wordlists/passwords/custom.txt`

### Other lists

* `wordlists/dns` - a fairly reasonable list for host discovery composed of common conventions, self-hosted software etc.
* `wordlists/http/paths` - HTTP paths/params useful in fuzzing Web applications, generated with subclasses of `HttpWords` *)
* `wordlists/http/files/extensions` - file extensions useful in HTTP discovery
* `wordlists/http/files/biggquery/github` - file names that might be helpful e.g. in IIS short name enumeration, cleaned up of obvious uniques and garbage to reduce file size, in case of JSON, YML and XML at least two occurrences, otherwise untouched
* `wordlists/ports` - personal choice of ports used both for scanning internal networks and public services, used instead of nmap's top list
* `wordlists/usernames` - most common usernames, the short, and the long version

*) Some of the pairs in these lists are duplicates or make no sense (e.g. `postsPosts` or `syndication-editor`, although you never know...) This is an expected trade-off. Considering the number of requests usually sent, this is acceptable for now.

## Building

**NOTE: Due to Github limits not all lists are precompiled.** You need to run the build scripts yourself to generate the complete set (`compile.sh` and `huge.sh`).

The compiled sets are also hosted here (may not be up to date):
- [brutas-passwords-5-l.zip](https://drive.proton.me/urls/5ESDFTKQVC#pTokh18bYyfN) [updated 2022/07/16]
- [brutas-passwords-6-xl.zip](https://drive.proton.me/urls/Z586VGA1BW#k2mwYceQIJYA) [updated 2022/07/16]
- [brutas-passwords-7-xxl.zip](https://drive.proton.me/urls/HP5SGW9YEC#ZfdCr6PItCyP) [updated 2022/07/16]
- [brutas-http-paths-all.zip](https://drive.proton.me/urls/FKQVMNNQK0#uofhr9x4pDlA) [updated 2022/07/16]

Requirements:
* Python 3.9, 3.10
* `hashcat`
* `hashcat-utils`
* GNU tools: `cat`, `awk`, `comm`, `sort`, `uniq`
* `wordz` (pypi)

You need to install `wordz` first (what used to be the `scripts` part of this project):

```
% pip install wordz
```

The build process is automated and handled by the script located in the root of the project. The following will produce `1-6-*.txt` passwords, as well as subdomains and basic HTTP lists:

```
~/brutas:% ./compile.sh
```

For the rest (`7-xxl.txt` and all HTTP paths) run:

```
~/brutas:% ./huge.sh
```

If you want to generate a custom wordlist (`wordlists/passwords/custom.txt`) based on keywords in `src/keywords/custom.txt`, use the following:

```
~/brutas:% ./custom.sh
```

Be aware that building a custom list with 5.5k of lines generates approx. 560GB of data and requires around 680GB for temporary files (an extra drive is recommended due to heavy I/O).

### Using specific language

There are two options:
1) either overwrite `lang-int-*.txt` files;
2) or use the `CustomPasswords` class with keywords copied to `src/keywords/custom.txt`.

The first one would cause the build to use the specific language as the base, while other languages would still be used (starting with `wordlists/passwords/6-xl.txt` list). The second option would ignore the normal build process and use the full set of rules on the `src/keywords/custom.txt` file. You should expect a massive output in that case.

## Passwords

Why these password lists are different? The goal here is not to crack every password possible, it is to move forward inside a network. And if cracking is really needed then the bigger lists can be used, however, the assumption here is that it will be done in a reasonable time span and with limited resources (like a VM, hijacked host etc).

A brief introduction to password lists:
* the number of passwords grows with the consecutive file number;
* passwords are not sorted according to the probability, they are combined into groups of probability instead;
* each consecutive file **does not** contain passwords from any of the previous sets.

### Basic usage

The combined lists `{1,2,3,4}-*.txt` seem to be most effective for general purpose and reasonably fast password cracking. Start with the smallest one and move forward. The lists `{1,2}-*.txt` are designed for a quick win in large networks. If you need something really minimalistic, try using `1-xxs.txt` solely - my highly opinionated view of the top 100.

However, I recommend experimenting on your own and rebuilding these sets depending on the target. You may want to incorporate your native language keywords, too. For example, file or a domain name combined with `numbers.txt` turns out to be pretty effective on encrypted archives and wireless networks. As with everything, a little social engineering comes handy to understand the local approach to the "password policy".

### Statistics

Based on leaks in two categories (social networks and technical forums), the current (2022/05/20) effectiveness is:

|                                      | No. of passwords | Social networks (~1M) | Technical forums (~450K) |
| ------------------------------------ | ---------------- | --------------------- | ------------------------ |
| brutas-passwords-1-xxs.txt (*)       |             100  |       2.16%           |          2.75%           |
| brutas-passwords-2-xs.txt (*)        |           6,549  |       3.05%           |          3.63%           |
| brutas-passwords-3-s.txt (*)         |          24,805  |       3.99%           |          4.32%           |
| brutas-passwords-4-m.txt             |         922,624  |       3.59%           |          5.05%           |
| brutas-passwords-5-l.txt             |      33,278,126  |      13.91%           |         17.10%           |
| brutas-passwords-6-xl.txt            |     162,843,765  |       6.93%           |          9.24%           |
| brutas-passwords-7-xxl.txt           |  10,051,549,134  |      26.08%           |         34.21%           |
| Suitable for online bruteforcing (*) |                  |       9.20% (99,197)  |         10.70% (48,885)  |
| To be used for offline cracking      |                  |      50.51% (544,617) |         65.64% (299,699) |
| TOTAL                                |                  |      59.71% (643,891) |         76.34% (348,757) |


So, the basic three lists (~31K passwords) provide 10% success on average with these fairly diverse and big samples. From my experience, password spraying with the top 100 is guaranteed to yield interesting results. And most often a couple accounts is enough to move forward in almost any network.

### How does it compare to `rockyou.txt`?

The famous `rockyou.txt` dictionary contains 14,344,392 passwords (at least in the Kali Linux "edition"). Against the same sets the results are:

|                                      | No. of passwords | Social networks (~1M) | Technical forums (~450K) |
| ------------------------------------ | ---------------- | --------------------- | ------------------------ |
| rockyou.txt                          |      14,344,392  |      34.99% (377384)  |         39.55% (180665)  |

It seems that with half of the passwords from the first five groups the `rockyou.txt` dictionary is much more effective. How come? Let's see what happens if we mix them:

|                                      | No. of passwords | Social networks (~1M) | Technical forums (~450K) |
| ------------------------------------ | ---------------- | --------------------- | ------------------------ |
| rockyou.txt + brutas-1-3.txt         |      14,375,845  |      44.19% (476578)  |         50.25% (229550)  |
| rockyou.txt + brutas-1-5.txt         |      48,576,595  |      61.90% (667459)  |         72.94% (333231)  |

* 44.19% (social networks) - 34.99% (rockyou) = 9.20% (= 9.20%, brutas-1-3)
* 50.25% (technical forums) - 39.55% (rockyou) = 10.70% (= 10.70%, brutas-1-3)
* 61.90% (social networks) - 34.99% (rockyou) = 26.91% (~= 26.70%, brutas-1-5)
* 72.94% (technical forums) - 39.55% (rockyou) = 33.39% (~= 32.85%, brutas-1-5)

The answer is clear: these sets are somewhat complementary, or rather `brutas` was designed with a different goal in mind than what you would find in the leaks from popular sites. For example, `rockyou.txt` is missing 23,246 passwords from the `brutas-1-3.txt` combo (which is 31,453 in total). To name just a few: `P$SSW)RD`, `Admin123!` or `!root!`. So, if you want to bruteforce or spray in a more corporate environment (i.e. with password policies in place), use `brutas`. For best results in general cracking, combine it with typical leaks. And with the bigger `brutas` lists the "predictable sophistication" grows significantly.
