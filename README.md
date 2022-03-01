# brutas

> Wordlists and passwords handcrafted with ♥

A pretty comprehensive set of password dictionaries and wordlists (and a framework) designed for quick wins in realistic scenarios.

A few facts:
* The rulesets, keywords and password combinations are based on analysis of roughly 400GB of pure data.
* It is not an ordinary dump of all things available. All wordlists and rules were processed manually.
* The HTTP paths and files dictionaries are designed to avoid alerting WAFs, there are no payloads that can be easily detected as it is the case with many popular lists.

## Introduction

A brief introduction to `brutas-passwords-#` lists:
* the number of passwords grows with the consecutive file number;
* passwords are not sorted according to the probability, they are combined into groups of probability instead;
* each consecutive file **does not** contain passwords from the previous set.

**NOTE: Due to Github limits, only lists 1-3 are precompiled.** You need to run `./scripts/build.py -p main.Extended` to generate the complete set (see the tutorial below):
* brutas-passwords-4-m.txt (400MB)
* brutas-passwords-5-l.txt (2.5GB)
* brutas-passwords-6-xl.txt (126GB)

The whole operation takes roughly six hours on a 2,6 GHz Intel Core i7 with 16GB of RAM and currently requires 160GB of free disk space to store the final results plus roughly 280GB for temporary files, SSD highly recommended.

## Tutorial

### Rebuilding the basic lists

`% ./scripts/build.py`

### Building the extended lists using external drive for temporary files and output

`% ./scripts/build.py -p main.Extended -t /media/user/External/tmp -o /media/user/External`

### Generating password list using custom keywords

`% ./scripts/build.py -p main.Custom -t /media/user/External/tmp/custom -o /media/user/External/custom`

### Using specific language

There are two options:
1) either overwrite `brutas-lang-int-*.txt` files;
2) or use the `main.Custom` class with keywords copied to `keywords/brutas-custom.txt`.

The first one would cause the build to use the specific language as the base, while other languages would still be used (starting with `brutas-passwords-5-l.txt` list). The second option would ignore the normal build process and use the full set of rules on the `keywords/brutas-custom.txt` file. You should expect a massive output in that case.

### Configuration

You can store your local configuration in `scripts/local_config.py`. For example, you may want to disable some rules (or add your own?), or change paths to `hashcat-utils` binaries.

## Requirements

* Python 3.x
* hashcat-utils
* lzop (recommended)
* Bash

## Detailed description

The `brutas-passwords-2-xs.txt` list seems to be most effective for general purpose and reasonably fast password bruteforcing, while `brutas-passwords-1-xxs.txt` is designed for a quick win in large networks.

However, I recommend experimenting on your own and rebuilding these sets depending on the target. You may want to incorporate your native language keywords, too. For example, file or a domain name combined with `brutas-passwords-numbers.txt` turns out to be pretty effective on encrypted archives and wireless networks. As with everything, a little social engineering comes handy to understand the local approach to the "password policy".

* `brutas-passwords-{1,2,3,4,5,6}-*.txt` - wordlists combined with passwords generated using keywords, hashcat rules and string partials (see `brutas/scripts/main/__init__.py` for details)
* `brutas-passwords-classics.txt` - typical admin passwords based on roles (test, admin), words (password, secret) or "funny" ones (like `letmein` or `trustno1`)
* `brutas-passwords-closekeys.txt` - close key combinations or easy phrases (e.g. `abcd`) combined with capitalization, numbers, repetitions etc.
* `brutas-passwords-top.txt` - is a list composed of most popular user passwords found in leaks, doesn't contain close keys or any more sophisticated combinations
* `brutas-passwords-unique.txt` - passwords which are complex enough to be used as independent passwords and are rarely mixed with any extra characters, usually related to pop-culture or sports (e.g. `apollo13`, `9inchnails`, `ronaldo7`)
* `brutas-passwords-numbers.txt` - a small list of numbers used in passwords (e.g. dates, math constants)

### Other lists

* `brutas-extensions.txt` - extensions especially useful when combined with `brutas-http-paths.txt`
* `brutas-http-params.txt` - simplistic and realistic approach to HTTP parameters
* `brutas-http-paths.txt` - no path traversal or pseudo exploits to keep low profile, no subs (use recursion instead) - paths only
* `brutas-usernames.txt` - most common usernames
* `brutas-usernames-small.txt` - a short list of usernames
* `brutas-ports-tcp-http.txt` - common and not that obvious HTTP ports
* `brutas-ports-tcp-internal.txt` - list of TCP services that may come up internally
* `brutas-ports-tcp-public.txt` - list of public TCP ports, useful for host discovery

### Subdomains

* `brutas-subdomains-1-small.txt` - a fairly reasonable list for host discovery composed of common conventions, self-hosted software etc.
* `brutas-subdomains-2-large.txt` - extended list with some extra pre-/postfixes like `host-srv`, `f.host` or `host10`

### Keywords

* `keywords/brutas-lang-int-common.txt` - set of most frequent English (and not only) words used in passwords internationally (also from literature, pop culture etc)
* `keywords/brutas-lang-int-less.txt` - less frequent English words used in passwords by native speakers
* `keywords/brutas-lang-*` - other languages based mostly on leaks
* `keywords/brutas-all-lang.txt` - all languages combined
* `keywords/brutas-subdomains.txt` - keywords and rules used to generate lists for subdomains
* `keywords/brutas-subdomains-extra.txt` - additional prefixes for subdomain discovery
* `keywords/brutas-wifi.txt` - bits and pieces useful in generating passwords for wireless networks

## Building

The build process is automated and handled by the script located in `./scripts/build.py`. Check it out to understand what are the blocks and how I set the priorities (or in other words what is most probable in my opinion).

### Arguments

```
usage: build.py [-h] [-p PATH] [-t TEMPORARY_DIR] [-o OUTPUT_DIR] [--cores CORES] [--memory MEMORY] [--debug]

Brutas build script

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Class path. [Default: main.Basic]
  -t TEMPORARY_DIR, --temporary-dir TEMPORARY_DIR
                        Temporary directory path. [Default: auto]
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output directory path. [Default: .]
  --cores CORES         Number of cores to be used for sorting. [Default: auto]
  --memory MEMORY       Percentage of memory to be used for sorting. [Default: 80%]
  --debug               Enable debug level logging
```

### Class path options

* **`main.Basic`** - builds everything _and_ password lists 1-3
* **`main.Extended`** - extends `main.Basic` with lists 4-6
* **`main.Custom`** - takes the keywords listed in `keywords/brutas-custom.txt` and parses with all available rules plus some extra combinations, ordering etc. Warning: 2-3 keywords will produce several gigabytes of data
* **`main.MergeAll`** - concatenates lists 1-6 into a single file `brutas-passwords-all.txt`

## Typical log output

```
% ./scripts/build.py
[1911-01-01 26:00:35,314] Processing with class: Basic
[1911-01-01 26:00:35,314] Using temporary directory: /tmp/tmpojpa7d2m
[1911-01-01 26:00:35,314] Generating subdomains
[1911-01-01 26:00:40,215] Preparing keyword lists
[1911-01-01 26:00:40,407] Processing wordlists with rules "repeat"
[1911-01-01 26:00:40,407]    - repeat-brutas-passwords-classics.txt
[1911-01-01 26:00:43,904]    - repeat-brutas-passwords-closekeys.txt
[1911-01-01 26:00:47,445]    - repeat-brutas-passwords-top.txt
[1911-01-01 26:00:50,931]    - repeat-brutas-passwords-unique.txt
[1911-01-01 26:00:54,503]    - repeat-brutas-usernames-small.txt
[1911-01-01 26:00:58,067]    - repeat-brutas-usernames.txt
[1911-01-01 26:00:01,347]    - repeat-brutas-all-lang.txt
[1911-01-01 26:00:04,956]    - repeat-brutas-lang-int-common.txt
[1911-01-01 26:00:08,560]    - repeat-brutas-lang-int-less.txt
[1911-01-01 26:00:12,215] Processing wordlists with rules "simple"
[1911-01-01 26:00:12,215]    - simple-brutas-passwords-classics.txt
[1911-01-01 26:00:15,860]    - simple-brutas-passwords-closekeys.txt
[1911-01-01 26:00:19,461]    - simple-brutas-passwords-top.txt
[1911-01-01 26:00:22,832]    - simple-brutas-passwords-unique.txt
[1911-01-01 26:00:26,665]    - simple-brutas-usernames-small.txt
[1911-01-01 26:00:30,516]    - simple-brutas-usernames.txt
[1911-01-01 26:00:34,200]    - simple-brutas-all-lang.txt
[1911-01-01 26:00:37,865]    - simple-brutas-lang-int-common.txt
[1911-01-01 26:00:41,870]    - simple-brutas-lang-int-less.txt
[1911-01-01 26:00:46,893] Processing wordlists with rules "complex"
[1911-01-01 26:00:46,893]    - complex-brutas-passwords-classics.txt
[1911-01-01 26:00:52,209]    - complex-brutas-passwords-closekeys.txt
[1911-01-01 26:00:57,195]    - complex-brutas-passwords-top.txt
[1911-01-01 26:00:01,055]    - complex-brutas-passwords-unique.txt
[1911-01-01 26:00:04,807]    - complex-brutas-usernames-small.txt
[1911-01-01 26:00:08,705]    - complex-brutas-usernames.txt
[1911-01-01 26:00:12,507]    - complex-brutas-all-lang.txt
[1911-01-01 26:00:16,608]    - complex-brutas-lang-int-common.txt
[1911-01-01 26:00:20,584]    - complex-brutas-lang-int-less.txt
[1911-01-01 26:00:24,785] Processing wordlists with rules "hax0r"
[1911-01-01 26:00:24,786]    - hax0r-brutas-passwords-classics.txt
[1911-01-01 26:00:28,836]    - hax0r-brutas-passwords-closekeys.txt
[1911-01-01 26:00:33,075]    - hax0r-brutas-passwords-top.txt
[1911-01-01 26:00:37,330]    - hax0r-brutas-passwords-unique.txt
[1911-01-01 26:00:41,496]    - hax0r-brutas-usernames-small.txt
[1911-01-01 26:00:45,923]    - hax0r-brutas-usernames.txt
[1911-01-01 26:00:50,519]    - hax0r-brutas-all-lang.txt
[1911-01-01 26:00:55,995]    - hax0r-brutas-lang-int-common.txt
[1911-01-01 26:00:01,100]    - hax0r-brutas-lang-int-less.txt
[1911-01-01 26:00:07,421] Processing wordlists with rules "both"
[1911-01-01 26:00:07,421]    - both-brutas-passwords-classics.txt
[1911-01-01 26:00:12,316]    - both-brutas-passwords-closekeys.txt
[1911-01-01 26:00:18,391]    - both-brutas-passwords-top.txt
[1911-01-01 26:00:22,593]    - both-brutas-passwords-unique.txt
[1911-01-01 26:00:26,589]    - both-brutas-usernames-small.txt
[1911-01-01 26:00:29,995]    - both-brutas-usernames.txt
[1911-01-01 26:00:33,404]    - both-brutas-all-lang.txt
[1911-01-01 26:00:37,141]    - both-brutas-lang-int-common.txt
[1911-01-01 26:00:40,999]    - both-brutas-lang-int-less.txt
[1911-01-01 26:00:44,805] Combining simple-brutas-usernames with separators
[1911-01-01 26:00:44,820] Combining simple-brutas-usernames-small with separators
[1911-01-01 26:00:44,828] Combining simple-brutas-usernames with separators
[1911-01-01 26:00:44,837] Combining simple-brutas-usernames-small with separators
[1911-01-01 26:00:44,844] Merging: brutas-passwords-1-xxs.txt
[1911-01-01 26:00:44,870] Combining simple-brutas-usernames-small with extra-common
[1911-01-01 26:00:44,878] Combining simple-brutas-usernames-small with functional
[1911-01-01 26:00:44,887] Combining simple-brutas-usernames-small with extra-common
[1911-01-01 26:00:44,895] Combining simple-brutas-usernames-small with extra-less
[1911-01-01 26:00:44,903] Combining simple-brutas-usernames-small with numbers-common
[1911-01-01 26:00:44,911] Combining simple-brutas-usernames-small with years-current
[1911-01-01 26:00:44,919] Combining simple-brutas-usernames-small+extra-common with years-current
[1911-01-01 26:00:44,931] Combining simple-brutas-usernames-small+separators with functional
[1911-01-01 26:00:44,939] Combining simple-brutas-usernames-small+separators with months
[1911-01-01 26:00:44,947] Combining simple-brutas-usernames-small+separators with years-current
[1911-01-01 26:00:44,955] Merging: brutas-passwords-2-xs.txt
[1911-01-01 26:00:45,000] Combining separators+simple-brutas-usernames-small with functional
[1911-01-01 26:00:45,008] Combining separators+simple-brutas-usernames-small with years-current
[1911-01-01 26:00:45,016] Combining simple-brutas-passwords-closekeys with months
[1911-01-01 26:00:45,061] Combining simple-brutas-passwords-closekeys with numbers-common
[1911-01-01 26:00:45,123] Combining simple-brutas-passwords-closekeys with years-current
[1911-01-01 26:00:45,153] Combining simple-brutas-usernames-small with years-all
[1911-01-01 26:00:45,161] Combining simple-brutas-usernames-small+extra-common with extra-common
[1911-01-01 26:00:45,184] Combining simple-brutas-usernames-small+numbers-common with extra-common
[1911-01-01 26:00:45,198] Combining simple-brutas-usernames-small+years-current with extra-common
[1911-01-01 26:00:45,207] Merging: brutas-passwords-3-s.txt
[1911-01-01 26:00:00,360] Done! You may want to clean up the temporary directory yourself: /tmp/tmpojpa7d2m
```