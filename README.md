# brutas

> Wordlists and passwords handcrafted with ♥

A pretty comprehensive set of password dictionaries and wordlists designed for quick wins in red teaming scenarios. Why is it different? The goal here is not to crack every password possible, it is to move forward inside a network. And if cracking is really needed then the bigger lists can be used, however, the assumption here is that it will be done in a reasonable time span and with limited resources (like a VM, hijacked host etc).

A few facts:
* The rulesets, keywords and password combinations are based on analysis of roughly 400GB of pure data and dozens of peer-reviewed scientific articles.
* It is not an ordinary dump of all things available. All wordlists and rules were processed manually.

## Introduction

A brief introduction to `brutas-passwords-#` lists:
* the number of passwords grows with the consecutive file number;
* passwords are not sorted according to the probability, they are combined into groups of probability instead;
* each consecutive file **does not** contain passwords from any of the previous sets.

**NOTE: Due to Github limits not all lists are precompiled.** You need to run `main.ExtendedPasswords`, `main.BigPasswords` and `main.HttpWordsSuffixes` yourself to generate the complete set (see the tutorial below). The compiled sets are also hosted here (may not be up to date):
- [brutas-passwords-5-l.txt.zip](https://www.dropbox.com/s/uaiw78vhw3ss0qw/brutas-passwords-5-l.txt.zip?dl=0)
- [brutas-passwords-6-xl.txt.zip](https://www.dropbox.com/s/m774fiz5id7ob4r/brutas-passwords-6-xl.txt.zip?dl=0)
- [brutas-passwords-7-xxl.txt.zip](https://www.dropbox.com/s/28at76rfcjyylog/brutas-passwords-7-xxl.txt.zip?dl=0)
- [brutas-http-words-suffixes.zip](https://www.dropbox.com/s/26j38e9my274xaf/brutas-http-words-suffixes.zip?dl=0)

## Basic usage

The combined lists `brutas-passwords-{1,2,3,4}-*.txt` seem to be most effective for general purpose and reasonably fast password cracking. Start with the smallest one and move forward. The lists `brutas-passwords-{1,2}-*.txt` are designed for a quick win in large networks. If you need something really minimalistic, try using `brutas-passwords-1-xxs.txt` solely - my highly opinionated view of the top 100. 

However, I recommend experimenting on your own and rebuilding these sets depending on the target. You may want to incorporate your native language keywords, too. For example, file or a domain name combined with `brutas-passwords-numbers.txt` turns out to be pretty effective on encrypted archives and wireless networks. As with everything, a little social engineering comes handy to understand the local approach to the "password policy".

### Password lists

* `brutas-passwords-*.txt` - wordlists combined with passwords generated using keywords, hashcat rules and string partials (see `brutas/scripts/main/__init__.py` for details)
* `brutas-passwords-classics.txt` - typical admin passwords based on roles (test, admin), words (password, secret) or "funny" ones (like `letmein` or `trustno1`)
* `brutas-passwords-patterns.txt` - close key combinations or simple phrases (e.g. `abcd`) combined with capitalization, numbers, repetitions etc.
* `brutas-passwords-top.txt` - is a list composed of most popular user passwords found in leaks, doesn't contain close keys or any more sophisticated combinations
* `brutas-passwords-unique.txt` - passwords which are complex enough to be used as independent passwords and are rarely mixed with any extra characters, usually related to pop-culture or sports (e.g. `apollo13`, `9inchnails`, `ronaldo7`)
* `brutas-passwords-numbers.txt` - a small list of numbers used in passwords (e.g. dates, math constants)
* `brutas-passwords-custom.txt` - example of running `main.CustomPasswords` with keyword `love`, the result of parsing `keywords/brutas-custom.txt` with all available rules plus some extra combinations, ordering etc.

### Other lists

* `brutas-http-files-extensions-common.txt` - common file extensions
* `brutas-http-files-extensions-less.txt` - less common extensions
* `brutas-http-words-*.txt` - HTTP paths/params useful in fuzzing Web applications, generated with `main.HttpWords` *)
* `brutas-http-words-suffixes-*.txt` - HTTP paths/params double words extended with common suffixes (e.g. `VisibleContentId`, `hidden-content-ref`) *)
* `brutas-ports-tcp-http.txt` - common and not that obvious HTTP ports
* `brutas-ports-tcp-internal.txt` - list of TCP services that may come up internally
* `brutas-ports-tcp-public.txt` - list of public TCP ports, useful for host discovery
* `brutas-subdomains-1-small.txt` - a fairly reasonable list for host discovery composed of common conventions, self-hosted software etc.
* `brutas-subdomains-2-large.txt` - extended list with some extra pre-/postfixes like `host-srv`, `f.host` or `host10`
* `brutas-usernames.txt` - most common usernames
* `brutas-usernames-small.txt` - a short list of usernames

*) Some of the pairs in these lists are duplicates or make no sense (e.g. `postsPosts` or `syndication-editor`, although you never know...) This is an expected trade-off. Considering the number of requests usually sent, this is acceptable for now.

### Keywords

* `keywords/brutas-lang-int-common.txt` - set of most frequent English (and not only) words used in passwords internationally (also from literature, pop culture etc)
* `keywords/brutas-lang-int-less.txt` - less frequent English words used in passwords by native speakers
* `keywords/brutas-lang-*` - other languages based mostly on leaks
* `keywords/brutas-all-lang.txt` - all languages combined
* `keywords/brutas-subdomains.txt` - keywords and rules used to generate lists for subdomains
* `keywords/brutas-subdomains-extra.txt` - additional prefixes for subdomain discovery
* `keywords/brutas-wifi.txt` - bits and pieces useful in generating passwords for wireless networks
* `keywords/brutas-custom.txt` - file used with `main.Custom` generator
* `keywords/brutas-http-{words, verbs}.txt` - files used with `main.HttpWords` and `main.HttpWordsSuffixes` generators, might be used standalone

### Bits

* There are various "parts" in the `bits` directory which you may find helpful in building your own sets.

## Building

The build process is automated and handled by the script located in `./scripts/build.py`:

```
usage: build.py [-h] -p PATH [-t TEMPORARY_DIR] [-o OUTPUT_DIR] [--min-length MIN_LENGTH] [--cores CORES] [--memory MEMORY] [--debug]

Brutas build script

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Class path. [Choices: main.Subdomains, main.HttpWords, main.HttpWordsSuffixes, main.BasicPasswords, main.ExtendedPasswords, main.BigPasswords, main.CustomPasswords, main.MergeAll]
  -t TEMPORARY_DIR, --temporary-dir TEMPORARY_DIR
                        Temporary directory path. [Default: auto]
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output directory path. [Default: .]
  --min-length MIN_LENGTH
                        Minimal length for a password when merging lists. [Default: 4]
  --cores CORES         Number of cores to be used for sorting. [Default: auto]
  --memory MEMORY       Percentage of memory to be used for sorting. [Default: 80%]
  --debug               Enable debug level logging
```

### Requirements

* Python 3.10 (tested)
* hashcat
* hashcat-utils
* GNU tools: cat, awk, comm, sort, uniq

### Configuration

You can store your local configuration in `scripts/local_config.py`. For example, you may want to disable some rules (or add your own?), or change paths to `hashcat-utils` binaries.

### Rebuilding the basic lists

`% ./scripts/build.py -p main.BasicPasswords`

### Building all password lists using external drive for temporary files and output

`% ./scripts/build.py -p main.BasicPasswords -t /media/user/External/tmp -o /media/user/External`
`% ./scripts/build.py -p main.ExtendedPasswords -t /media/user/External/tmp -o /media/user/External`
`% ./scripts/build.py -p main.BigPasswords -t /media/user/External/tmp -o /media/user/External`

### Generating password list using custom keywords

`% ./scripts/build.py -p main.CustomPasswords`

### Using specific language

There are two options:
1) either overwrite `brutas-lang-int-*.txt` files;
2) or use the `main.CustomPasswords` class with keywords copied to `keywords/brutas-custom.txt`.

The first one would cause the build to use the specific language as the base, while other languages would still be used (starting with `brutas-passwords-6-xl.txt` list). The second option would ignore the normal build process and use the full set of rules on the `keywords/brutas-custom.txt` file. You should expect a massive output in that case.

### Some stats and hints

Setup:
- 2.6 GHz Intel Core i7
- 16GB of RAM
- SSD drive
- Temporary directory shared between builds

`main.BasicPasswords`
- generates `brutas-passwords-{2,3,4}-*.txt`
- Total time: 3 minutes
- Temporary directory size: ~190MB
- Output files size: ~10MB
- Total output size: ~10MB

`main.ExtendedPasswords`
- generates `brutas-passwords-{5,6}-*.txt`
- Total time: 9 minutes
- Temporary directory size: ~6,4GB
- Output files size: ~2,64GB
- Total output size: ~2,65GB

`main.BigPasswords`
- generates `brutas-passwords-7-xxl.txt`
- Total time: 19 hours
- Temporary directory size: ~300GB
- Output files size: ~132GB
- Total output size: ~134,7GB

`main.CustomPasswords`
- Building password list with `main.CustomPasswords` and `keywords/brutas-custom.txt` containing 5.5k of lines generates approx. 560GB of data and requires around 680GB for temporary files (an extra drive is recommended due to heavy I/O).