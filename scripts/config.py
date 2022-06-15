import pathlib


WORDLISTS = {
    'passwords': [
        'brutas-passwords-classics.txt',
        'brutas-passwords-patterns.txt',
        'brutas-passwords-top.txt',
        'brutas-passwords-unique.txt',
        'brutas-usernames-small.txt',
        'brutas-usernames.txt',
        'keywords/brutas-all-lang.txt',
        'keywords/brutas-lang-int-common.txt',
        'keywords/brutas-lang-int-less.txt',
    ],
    'http-words': [
        'keywords/brutas-http-adj-adv-det-all.txt',
        'keywords/brutas-http-adj-adv-det-common.txt',
        'keywords/brutas-http-nouns-all.txt',
        'keywords/brutas-http-nouns-common.txt',
        'keywords/brutas-http-verbs-all.txt',
        'keywords/brutas-http-verbs-common.txt',
        'keywords/brutas-http-suffixes.txt',
    ],
    'custom': [
        'keywords/brutas-custom.txt',
    ]
}

RULES = {
    'passwords': [
        'both',
        'complex',
        'hax0r',
        'repeat',
        'simple',
    ],
    'custom': [
        'both',
        'complex',
        'hax0r',
        'repeat',
        'simple',
    ],
    'http-words': [
        'lowercase',
        'capitalize',
    ],
}

BASE_DIR = str(pathlib.Path(__file__).parent.parent.absolute())

HASHCAT_PATH = 'hashcat'
COMBINATOR_PATH = 'combinator.bin'
RLI2_PATH = 'rli2.bin'


try:
    from local_config import *  # noqa
except ImportError:
    pass
