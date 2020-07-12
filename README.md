# brutas

    ░▒▓ brutas ▓▒░ Wordlists and passwords handcrafted with ♥

## Descriptions

**NOTE** These dictionaries are not sorted by probability. They are grouped instead.

### Passwords

The order is also suggested workflow (approx. size):

1. `brutas-passwords-1.txt` - stage one - collection of most common passwords, typical close-keys combinations, bands, brands, games and movies characters etc. (7k)
2. `brutas-passwords-2.txt` - second shot after the 1st stage dictionary, contains data from leaks and some top passwords from other lists (9k)
3. `brutas-passwords-3.txt` - suitable for internal services, `brutas-usernames.txt` parsed with hax0r and years rules (12k)
4. `brutas-passwords-1-years.txt` - try appending 2000-2024 before anything else, keep things simple (175k)
5. `brutas-passwords-1-hax0r.txt` - hax0r/1337 style applied to the 1st stage list (350k)
6. `brutas-passwords-2-years.txt` - applied to 2nd stage (215k)
7. `brutas-passwords-2-hax0r.txt` - applied to 2nd stage (445k)
7. `brutas-passwords-combined.txt` - all password lists combined, probably to be used offline only (1200k)

### Lists

* `brutas-usernames.txt` - most common usernames
* `brutas-extensions.txt` - extensions especially useful when combined with `brutas-http-paths.txt`
* `brutas-http-paths.txt` - no path traversal or pseudo exploits to keep low profile, no subs (use recursion instead) - paths only

### Subdomains

* `brutas-subdomains-3k.txt` - a fairly reasonable list for host discovery composed of common conventions, self-hosted software etc.
* `brutas-subdomains-250k.txt` - extended list with some extra pre-/postfixes like `host-srv`, `f.host` or `host10`
* `brutas-subdomains-keywords.*` - keywords and rules used to generate lists for subdomains