import pathlib


WORDLISTS = [
    'brutas-passwords-classics.txt',
    'brutas-passwords-patterns.txt',
    'brutas-passwords-top.txt',
    'brutas-passwords-unique.txt',
    'brutas-usernames-small.txt',
    'brutas-usernames.txt',
    'keywords/brutas-all-lang.txt',
    'keywords/brutas-lang-int-common.txt',
    'keywords/brutas-lang-int-less.txt',
]

RULES = [
    'repeat',
    'simple',
    'complex',
    'hax0r',
    'both',
]

BASE_DIR = str(pathlib.Path(__file__).parent.parent.absolute())

COMBINATOR_PATH = '/usr/lib/hashcat-utils/combinator.bin'
RLI2_PATH = '/usr/lib/hashcat-utils/rli2.bin'


try:
    from local_config import *  # noqa
except ImportError:
    pass
