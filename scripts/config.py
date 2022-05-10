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
        'keywords/brutas-http-verbs.txt',
        'keywords/brutas-http-words.txt',
        'keywords/brutas-http-suffixes.txt',
    ],
    'custom': [
        'keywords/brutas-custom.txt',
    ]
}

RULES = {
    'passwords': [
        'repeat',
        'simple',
        'complex',
        'hax0r',
        'both',
    ],
    'custom': [
        'repeat',
        'simple',
        'complex',
        'hax0r',
        'both',
    ],
    'http-words': [
        'capitalize',
        'pass',
    ],
}

BASE_DIR = str(pathlib.Path(__file__).parent.parent.absolute())

COMBINATOR_PATH = '/usr/lib/hashcat-utils/combinator.bin'
RLI2_PATH = '/usr/lib/hashcat-utils/rli2.bin'


try:
    from local_config import *  # noqa
except ImportError:
    pass
