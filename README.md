# brutas

    ░▒▓ brutas ▓▒░ Wordlists and passwords handcrafted with ♥

**A pretty comprehensive set of password dictionaries and wordlists (and a framework) designed for quick wins in realistic scenarios.**

## Downloads

You can download the latest releases of the "big" set from the following URLs:

* `brutas-passwords-4-7.tar.gz` - https://mega.nz/file/VCQ2HJCT#c59lQ4rqddJnbz_oRlMmQsEfLEmDQX3k9t2aSc0uIEc (pending upload)

## Passwords

A brief introduction to `brutas-passwords-#` lists:
* the number of passwords grows with the consecutive file number;
* passwords are not sorted according to the probability, they are combined into groups of probability instead;
* each consecutive file **does not** contain passwords from the previous set;
* `brutas-passwords-7-all.txt` is a merge of all sets, sorted by groups, so the most probable ones are at the beginning.

**NOTE: Due to Github limits, only `xxs`, `x` and `s` lists are precompiled.** You need to run `./scripts/build.py` locally to generate the whole set, or you can download from the link above.

### Details

The `brutas-passwords-2-xs.txt` list seems to be most effective for general purpose and reasonably fast password bruteforcing, while `brutas-passwords-1-xxs.txt` is designed for a quick win in large networks.

However, I recommend experimenting on your own and rebuilding these sets depending on the target. You may want to incorporate your native language keywords, too. For example, file or a domain name combined with `brutas-passwords-numbers.txt` turns out to be pretty effective on encrypted archives and wireless networks. As with everything, a little social engineering comes handy to understand the local approach to the "password policy".

* `brutas-passwords-1-xxs.txt` - a low profile list useful for attacking administrator and service accounts
* `brutas-passwords-2-xs.txt` - general purpose, could crack admin or regular user accounts, a mix of most popular passwords with some pseudo-complex combinations
* `brutas-passwords-3-s.txt` - probably the biggest one still reasonable for online bruteforcing
* `brutas-passwords-4-m.txt` - apart from smallers lists contains more complex combinations of words parsed with leetspeak, dates and mixed case
* `brutas-passwords-5-l.txt` - most rules applied, includes i.a. words from all supported languages
* `brutas-passwords-6-xl.txt` - everything above plus words from all supported languages parsed with all rules
* `brutas-passwords-7-all.txt` - all sets combined, happy cracking
* `brutas-passwords-classics.txt` - typical admin passwords based on roles (test, admin), words (password, secret) or "funny" ones (like `letmein` or `trustno1`)
* `brutas-passwords-closekeys.txt` - close key combinations or easy phrases (e.g. `abcd`) combined with capitalization, numbers, repetitions etc.
* `brutas-passwords-top.txt` - currently 2k list composed of most popular user passwords found in leaks, doesn't contain close keys or any more sophisticated combinations than adding a number or two
* `brutas-passwords-unique.txt` - passwords which are complex enough to be used as independent passwords and are rarely mixed with any extra characters, usually related to pop-culture or sports (e.g. `apollo13`, `9inchnails`, `ronaldo7`)
* `brutas-passwords-numbers.txt` - a small list of numbers used in passwords (e.g. dates, math constants)

## Other lists

* `brutas-extensions.txt` - extensions especially useful when combined with `brutas-http-paths.txt`
* `brutas-http-params.txt` - simplistic and realistic approach to HTTP parameters
* `brutas-http-paths.txt` - no path traversal or pseudo exploits to keep low profile, no subs (use recursion instead) - paths only
* `brutas-usernames.txt` - most common usernames
* `brutas-usernames-small.txt` - a short list of usernames
* `brutas-ports-tcp-http.txt` - common and not that obvious HTTP ports
* `brutas-ports-tcp-internal.txt` - list of TCP services that may come up internally
* `brutas-ports-tcp-public.txt` - list of public TCP ports, useful for host discovery

## Subdomains

* `brutas-subdomains-1-small.txt` - a fairly reasonable list for host discovery composed of common conventions, self-hosted software etc.
* `brutas-subdomains-2-large.txt` - extended list with some extra pre-/postfixes like `host-srv`, `f.host` or `host10`

## Keywords

* `keywords/brutas-lang-int-common.txt` - set of most frequent English (and not only) words used in passwords internationally (also from literature, pop culture etc)
* `keywords/brutas-lang-int-less.txt` - less frequent English words used in passwords by native speakers
* `keywords/brutas-lang-*` - other languages, keywords not present in English lists, based mostly on leaks
* `keywords/brutas-all-lang.txt` - all languages combined
* `keywords/brutas-subdomains.txt` - keywords and rules used to generate lists for subdomains
* `keywords/brutas-subdomains-extra.txt` - additional prefixes for subdomain discovery
* `keywords/brutas-wifi.txt` - bits and pieces useful in generating passwords for wireless networks

## Building

The build process is automated and handled by the script located in `./scripts/build.py`. Check it out to understand what are the blocks and how I set the priorities (or in other words what is most probable in my opinion).

### Arguments

```
usage: build.py [-h] [-p PATH] [-c COMBINATOR_PATH] [-t TEMPORARY_DIR] [--debug]

Brutas build script

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Class path
  -c COMBINATOR_PATH, --combinator-path COMBINATOR_PATH
                        Hashcat combinator.bin path
  -t TEMPORARY_DIR, --temporary-dir TEMPORARY_DIR
                        Temporary directory path
  --debug               Enable debug level logging
```

#### Class path options

* **`main.Basic`** - builds everything _and_ password lists 1-3
* **`main.Extended`** - builds everything _and_ password lists 1-6 (**NOTE**: requires proper resources)
* **`main.MergeAll`** - merges passwords lists 1-6 into a single `brutas-passwords-7-all.txt` file

### Typical log output

```
[2021-01-01 20:51:38,216] Processing with class: Basic
[2021-01-01 20:51:38,216] Using temporary directory: /tmp/tmpojpa7d2m
[2021-01-01 20:51:38,216] Generating subdomains
[2021-01-01 20:52:01,729] Preparing keyword lists
[2021-01-01 20:52:01,928] Processing wordlists with rules "repeat"
[2021-01-01 20:52:01,929] Processing wordlists with rules "simple"
[2021-01-01 20:52:01,929] Processing wordlists with rules "complex"
[2021-01-01 20:52:01,929] Processing wordlists with rules "hax0r"
[2021-01-01 20:52:01,930] Processing wordlists with rules "both"
[2021-01-01 20:52:01,930] Merging: brutas-passwords-1-xxs.txt
[2021-01-01 20:52:01,955] Merging: brutas-passwords-2-xs.txt
[2021-01-01 20:52:02,031] Merging: brutas-passwords-3-s.txt
[2021-01-01 20:52:03,089] Done! You may want to clean up the temporary directory yourself: /tmp/tmpojpa7d2m
```