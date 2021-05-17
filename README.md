# brutas

    ░▒▓ brutas ▓▒░ Wordlists and passwords handcrafted with ♥

**A pretty comprehensive set of password dictionaries and wordlists designed for quick wins in realistic scenarios.**

## Passwords

A brief introduction to `brutas-passwords-#` lists:
* the number of passwords grows with the consecutive file number;
* passwords are not sorted according to the probability, they are combined into groups of probability represented by separate files instead;
* each list begins with passwords from the previous file.

**NOTE: Due to Github limits, only `xxs`, `x` and `s` lists are precompiled.** You need to run `./scripts/build.py` locally to generate the whole set.

### Details

The `brutas-passwords-2-xs.txt` list seems to be most effective for general purpose and reasonably fast password bruteforcing, while `brutas-passwords-1-xxs.txt` is designed for a quick win in large networks.

However, I recommend experimenting on your own and rebuilding these sets depending on the target. You may want to incorporate your native language keywords, too. For example, file or a domain name combined with `brutas-passwords-numbers.txt` turns out to be pretty effective on encrypted archives and wireless networks. As with everything, a little social engineering comes handy to understand the local approach to the "password policy".

* `brutas-passwords-1-xxs.txt` - a low profile list useful for attacking administrator and service accounts
* `brutas-passwords-2-xs.txt` - general purpose, could crack admin or regular user accounts, a mix of most popular passwords with some pseudo-complex combinations
* `brutas-passwords-3-s.txt` - probably the biggest one still reasonable for online bruteforcing
* `brutas-passwords-4-m.txt` - apart from smallers lists contains more complex combinations of words parsed with leetspeak, dates and mixed case
* `brutas-passwords-5-l.txt` - most rules applied, includes i.a. words from all supported languages
* `brutas-passwords-6-xl.txt` - everything above plus words from all supported languages parsed with all rules
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
* `keywords/brutas-*` - other languages, keywords not present in English lists, based mostly on leaks
* `keywords/brutas-all-lang.txt` - all languages combined
* `keywords/brutas-subdomains.txt` - keywords and rules used to generate lists for subdomains
* `keywords/brutas-subdomains-extra.txt` - additional prefixes for subdomain discovery
* `keywords/brutas-wifi.txt` - bits and pieces useful in generating passwords for wireless networks

## Building

The build process is automated and handled by the script located in `./scripts/build.py`. Check it out to understand what are the blocks and how I set the priorities (or in other words what is most probable in my opinion).

### Typical log output

```
Using temporary directory: /tmp/tmpmzpy1bcn
Generating subdomains
Preparing keyword lists
Processing wordlists with rules "repeat"
     - repeat-brutas-passwords-classics.txt
     - repeat-brutas-passwords-unique.txt
     - repeat-brutas-usernames-small.txt
     - repeat-brutas-usernames.txt
     - repeat-brutas-all-lang.txt
     - repeat-brutas-lang-int-common.txt
     - repeat-brutas-lang-int-less.txt
Processing wordlists with rules "simple"
     - simple-brutas-passwords-classics.txt
     - simple-brutas-passwords-unique.txt
     - simple-brutas-usernames-small.txt
     - simple-brutas-usernames.txt
     - simple-brutas-all-lang.txt
     - simple-brutas-lang-int-common.txt
     - simple-brutas-lang-int-less.txt
Processing wordlists with rules "complex"
     - complex-brutas-passwords-classics.txt
     - complex-brutas-passwords-unique.txt
     - complex-brutas-usernames-small.txt
     - complex-brutas-usernames.txt
     - complex-brutas-all-lang.txt
     - complex-brutas-lang-int-common.txt
     - complex-brutas-lang-int-less.txt
Processing wordlists with rules "hax0r"
     - hax0r-brutas-passwords-classics.txt
     - hax0r-brutas-passwords-unique.txt
     - hax0r-brutas-usernames-small.txt
     - hax0r-brutas-usernames.txt
     - hax0r-brutas-all-lang.txt
     - hax0r-brutas-lang-int-common.txt
     - hax0r-brutas-lang-int-less.txt
Processing wordlists with rules "both"
     - both-brutas-passwords-classics.txt
     - both-brutas-passwords-unique.txt
     - both-brutas-usernames-small.txt
     - both-brutas-usernames.txt
     - both-brutas-all-lang.txt
     - both-brutas-lang-int-common.txt
     - both-brutas-lang-int-less.txt
Combining simple-brutas-usernames with separators
Combining simple-brutas-usernames-small with separators
Combining simple-brutas-usernames with separators
Combining simple-brutas-usernames-small with separators
Combining simple-brutas-usernames with numbers-less
Combining simple-brutas-usernames-small with extra-common
Combining simple-brutas-usernames-small+separators with years-current
Merging: brutas-passwords-1-xxs.txt
Combining simple-brutas-usernames-small with extra-common
Combining simple-brutas-usernames-small with numbers-common
Combining simple-brutas-usernames-small with functional
Combining simple-brutas-usernames-small with numbers-common
Combining simple-brutas-usernames-small+separators with functional
Merging: brutas-passwords-2-xs.txt
Combining simple-brutas-usernames with extra-common
Combining simple-brutas-usernames with numbers-common
Combining simple-brutas-usernames-small with extra-less
Combining hax0r-brutas-usernames-small with extra-common
Combining simple-brutas-usernames with functional
Combining simple-brutas-usernames with numbers-common
Combining simple-brutas-usernames+separators with functional
Combining simple-brutas-usernames-small+numbers-common with extra-common
Combining simple-brutas-usernames-small+separators with months
Merging: brutas-passwords-3-s.txt
Combining separators+simple-brutas-usernames-small with functional
Combining separators+simple-brutas-usernames-small with years-current
Combining simple-brutas-usernames with extra-less
Combining simple-brutas-usernames with functional
Combining simple-brutas-usernames with numbers-less
Combining hax0r-brutas-usernames with extra-common
Combining hax0r-brutas-usernames with extra-less
Combining numbers-common+simple-brutas-usernames with extra-common
Combining simple-brutas-usernames with extra-common
Combining simple-brutas-usernames+numbers-common with extra-common
Combining simple-brutas-usernames+separators with months
Combining simple-brutas-usernames+separators with years-all
Combining simple-brutas-usernames-small+separators+months with years-current
Merging: brutas-passwords-4-m.txt
Combining repeat-brutas-usernames with extra-common
Combining numbers-less+simple-brutas-usernames with extra-common
Combining simple-brutas-usernames+numbers-less with extra-common
Merging: brutas-passwords-5-l.txt
Combining repeat-brutas-usernames with extra-less
Combining simple-brutas-usernames+separators+months with years-all
Merging: brutas-passwords-6-xl.txt
Cleaning up...
Done!
```