# brutas

    ░▒▓ brutas ▓▒░ Wordlists and passwords handcrafted with ♥

## Passwords

The `brutas-passwords-10k.txt` list seems to be most effective for general purpose and reasonably fast password bruteforcing, while `brutas-passwords-1k.txt` is designed for a quick win in large networks.

However, I recommend experimenting on your own and rebuilding these sets depending on the target. You may want to incorporate your native language keywords, too. For example, file or a domain name combined with `brutas-passwords-numbers.txt` turns out to be pretty effective on encrypted archives and wireless networks. As with everything, a little social engineering comes handy to understand the local approach to the "password policy".

* `brutas-passwords-1k.txt`
* `brutas-passwords-10k.txt`
* `brutas-passwords-60k.txt`
* `brutas-passwords-750k.txt`
* `brutas-passwords-classics.txt`
* `brutas-passwords-closekeys.txt`
* `brutas-passwords-numbers.txt`
* `brutas-passwords-tomcat.txt`
* `brutas-passwords-unique.txt`

## Other lists

* `brutas-extensions.txt` - extensions especially useful when combined with `brutas-http-paths.txt`
* `brutas-http-params.txt` - simplistic and realistic approach to HTTP parameters
* `brutas-http-paths.txt` - no path traversal or pseudo exploits to keep low profile, no subs (use recursion instead) - paths only
* `brutas-usernames.txt` - most common usernames
* `brutas-usernames-small.txt` - a short list of usernames
* `brutas-usernames-tomcat.txt` - ...guess ;)

## Subdomains

* `brutas-subdomains-3k.txt` - a fairly reasonable list for host discovery composed of common conventions, self-hosted software etc.
* `brutas-subdomains-250k.txt` - extended list with some extra pre-/postfixes like `host-srv`, `f.host` or `host10`

## Keywords

* `keywords/brutas-en-common.txt` - set of most frequent English words used in passwords internationally (also from literature, pop culture etc)
* `keywords/brutas-en-less.txt` - less frequent English words used in passwords by native speakers
* `keywords/brutas-*` - other languages, keywords not present in English lists, based mostly on leaks
* `keywords/brutas-subdomains.txt` - keywords and rules used to generate lists for subdomains
* `keywords/brutas-subdomains-extra.txt` - additional prefixes for subdomain discovery
* `keywords/brutas-wifi.txt` - bits and pieces useful in generating passwords for wireless networks

## Building

The build process is automated and handled by the script located in `./bin/rebuild.sh`. Check it out to understand what are the blocks and how I set the priorities (or in other words what is most probable in my opinion).
