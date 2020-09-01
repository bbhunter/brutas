# brutas

    ░▒▓ brutas ▓▒░ Wordlists and passwords handcrafted with ♥

## Descriptions

These dictionaries are based on real-life pentesting engagements both in small business and corporate network environments, leaks monitoring, honeypots, some friendly wargames etc. The build process is automated and handled by the script located in `./bin/rebuild.sh`. Check it out to understand what are the blocks and how I set the priorities (or in other words what is most probable in my opinion). You may want to *change that order depending on your target*.

### Passwords

You can use the "top passwords" lists if you prefer and `brutas-passwords-10k.txt` seems to be most effective for general purpose and reasonably fast password bruteforcing. However, I recommend combining these lists, depending on the use case. For example, I'd use `brutas-passwords-closekeys.txt` combined with `brutas-passwords-classics.txt` for attacking local network services and accounts, and `brutas-passwords-keywords-*.txt` for normal user accounts (perhaps with an extra rule or two). On the other hand, company, file or domain name combined with `brutas-passwords-numbers.txt` turns out to be pretty effective on encrypted archives and wireless networks. As with everything, a little social engineering comes handy to understand the local approach to the password "policy".

* `brutas-passwords-5k.txt`
* `brutas-passwords-10k.txt`
* `brutas-passwords-50k.txt`
* `brutas-passwords-400k.txt`
* `brutas-passwords-classics.txt`
* `brutas-passwords-closekeys.txt`
* `brutas-passwords-keywords-less-common.txt`
* `brutas-passwords-keywords-more-common.txt`
* `brutas-passwords-numbers.txt`
* `brutas-passwords-tomcat.txt`
* `brutas-passwords-unique.txt`

### Other lists

* `brutas-usernames.txt` - most common usernames
* `brutas-usernames-small.txt` - a short list of usernames
* `brutas-*-tomcat.txt` - ...guess ;)
* `brutas-extensions.txt` - extensions especially useful when combined with `brutas-http-paths.txt`
* `brutas-http-paths.txt` - no path traversal or pseudo exploits to keep low profile, no subs (use recursion instead) - paths only

### Subdomains

* `brutas-subdomains-3k.txt` - a fairly reasonable list for host discovery composed of common conventions, self-hosted software etc.
* `brutas-subdomains-250k.txt` - extended list with some extra pre-/postfixes like `host-srv`, `f.host` or `host10`
* `brutas-subdomains-keywords.*` - keywords and rules used to generate lists for subdomains
* `brutas-subdomains-extra.txt` - additional prefixes for subdomain discovery