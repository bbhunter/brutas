# brutas

    ░▒▓ brutas ▓▒░ Wordlists and passwords handcrafted with ♥

## Passwords

The `brutas-passwords-2-small.txt` list seems to be most effective for general purpose and reasonably fast password bruteforcing, while `brutas-passwords-1-x-small.txt` is designed for a quick win in large networks.

However, I recommend experimenting on your own and rebuilding these sets depending on the target. You may want to incorporate your native language keywords, too. For example, file or a domain name combined with `brutas-passwords-numbers.txt` turns out to be pretty effective on encrypted archives and wireless networks. As with everything, a little social engineering comes handy to understand the local approach to the "password policy".

* `brutas-passwords-1-x-small.txt` - a low profile list useful for attacking administrator and service accounts
* `brutas-passwords-2-small.txt` - general purpose, could crack admin or regular user accounts, a mix of most popular passwords with some pseudo-complex combinations
* `brutas-passwords-3-medium.txt` - probably the biggest one still reasonable for online bruteforcing
* `brutas-passwords-4-large.txt` - apart from smallers lists contains common English words and variations of leetspeak coded usernames
* `brutas-passwords-5-x-large.txt` - all rules applied, includes less common English words
* `brutas-passwords-classics.txt` - typical admin passwords based on roles (test, admin), words (password, secret) or "funny" ones (like still beloved `letmein` or `trustno1`)
* `brutas-passwords-closekeys.txt` - close key combinations or easy phrases (e.g. `abcd`) combined with capitalization, numbers, repetitions etc.
* `brutas-passwords-top.txt` - currently 2k list composed of most popular user passwords found in leaks, doesn't contain close keys or any more sophisticated combinations than adding a number or two
* `brutas-passwords-unique.txt` - passwords which are complex enough to be used as independent passwords and are rarely mixed with any extra characters, usually related to pop-culture or sports (e.g. `apollo13`, `9inchnails`, `ronaldo7`)
* `brutas-passwords-numbers.txt` - a small list of numbers used in passwords (e.g. dates, math constants)
* `brutas-passwords-tomcat.txt` - as the name suggests

## Other lists

* `brutas-extensions.txt` - extensions especially useful when combined with `brutas-http-paths.txt`
* `brutas-http-params.txt` - simplistic and realistic approach to HTTP parameters
* `brutas-http-paths.txt` - no path traversal or pseudo exploits to keep low profile, no subs (use recursion instead) - paths only
* `brutas-usernames.txt` - most common usernames
* `brutas-usernames-small.txt` - a short list of usernames
* `brutas-usernames-tomcat.txt` - as the name suggests
* `brutas-ports-tcp-http.txt` - common and not that obvious HTTP ports
* `brutas-ports-tcp-internal.txt` - list of TCP services that may come up internally
* `brutas-ports-tcp-public.txt` - list of public TCP ports, useful for host discovery

## Subdomains

* `brutas-subdomains-1-small.txt` - a fairly reasonable list for host discovery composed of common conventions, self-hosted software etc.
* `brutas-subdomains-2-large.txt` - extended list with some extra pre-/postfixes like `host-srv`, `f.host` or `host10`

## Keywords

* `keywords/brutas-en-common.txt` - set of most frequent English words used in passwords internationally (also from literature, pop culture etc)
* `keywords/brutas-en-less.txt` - less frequent English words used in passwords by native speakers
* `keywords/brutas-*` - other languages, keywords not present in English lists, based mostly on leaks
* `keywords/brutas-subdomains.txt` - keywords and rules used to generate lists for subdomains
* `keywords/brutas-subdomains-extra.txt` - additional prefixes for subdomain discovery
* `keywords/brutas-wifi.txt` - bits and pieces useful in generating passwords for wireless networks

## Building

The build process is automated and handled by the script located in `./bin/rebuild.sh`. Check it out to understand what are the blocks and how I set the priorities (or in other words what is most probable in my opinion).
