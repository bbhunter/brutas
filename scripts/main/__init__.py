import datetime
import functools
import logging
import pathlib
import shutil
import subprocess
import sys


logger = logging.getLogger('brutas')
formatter = {
    logging.DEBUG: logging.Formatter('%(name)s %(levelname)s [%(asctime)s] %(message)s'),
    logging.INFO: logging.Formatter('[%(asctime)s] %(message)s')
}
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


def init_logger(loglevel):
    handler.setLevel(loglevel)
    logger.setLevel(loglevel)
    handler.setFormatter(formatter[loglevel])


__available__ = ('Subdomains', 'Extensions', 'BasicPasswords', 'ExtendedPasswords', 'BigPasswords', 'CustomPasswords', 'MergeAll', 'HttpWordsPlainCommon', 'HttpWordsSuffixesCommon', 'HttpWordsDoubleCommon', 'HttpWordsPlainAll', 'HttpWordsSuffixesAll', 'HttpWordsDoubleAll')


class Combinator:

    config_name = None

    LEFT = 1
    BOTH = 2
    RIGHT = 3

    class Wordlist:

        def __init__(self, name, path):
            self.name = name
            self.path = path

        def __str__(self):
            return str(self.path)

    def __init__(self, config, args):
        self.config = config
        self.temp_dir = str(pathlib.Path(args.temporary_dir).resolve())
        self.root_dir = self.config.BASE_DIR
        self.output_dir = str(pathlib.Path(args.output_dir).resolve())
        self.cores = '' if args.cores is None else '--parallel=' + args.cores
        self.memory = '-S ' + args.memory
        # NOTE: This is commented out as a decision rationale: it seems that
        #       sort's --compress-program ignores environment variables, leading to
        #       duplicates. To be resolved after looking into sort internals.
        # self.compress_program = '--compress-program=lzop' if self.run_shell('which lzop') else ''
        # self.sort_snippet = f'sort -f -T {self.temp_dir} {self.compress_program} {self.cores} {self.memory}'
        self.sort_snippet = f'sort -f -T {self.temp_dir} {self.cores} {self.memory}'
        self.args = args
        if pathlib.Path.exists(pathlib.Path(self.config.COMBINATOR_PATH)):
            self.combinator_path = self.config.COMBINATOR_PATH
        else:
            logger.error(f'Hashcat `combinator` not found at {self.config.COMBINATOR_PATH}')
            sys.exit(1)
        if pathlib.Path.exists(pathlib.Path(self.config.RLI2_PATH)):
            self.rli2_path = self.config.RLI2_PATH
        else:
            logger.error(f'Hashcat `rli2` not found at {self.config.RLI2_PATH}')
            sys.exit(1)

    def run_shell(self, cmd):
        logger.debug(cmd)
        return subprocess.run(f'(export LC_ALL=C; {cmd})', shell=True, stdout=subprocess.PIPE).stdout

    def wordlists_process(self):
        for rule in self.config.RULES[self.config_name]:
            logger.info(f'Processing wordlists with rules `{rule}`')
            for wordlist in self.config.WORDLISTS[self.config_name]:
                self.rule(str(pathlib.Path(self.root_dir, wordlist)), rule)

    def check_exist(self, *paths):
        for path in paths:
            if not pathlib.Path(path).is_file():
                logger.debug(f'Resource `{path}` not found, skipping')
                return False
        return True

    def rule(self, wordlist, rule):
        # NOTE: Casting str(wordlist) to keep consistency with Wordlist instances, might need better solution one day
        filename = rule + '-' + pathlib.Path(str(wordlist)).name
        if not pathlib.Path(self.temp_dir, filename).is_file():
            logger.info(f'Processing `{wordlist}` with rule `{rule}`')
            self.run_shell(f'hashcat --stdout -r {self.root_dir}/rules/{rule}.rule {wordlist} | {self.sort_snippet} | uniq > {self.temp_dir}/{filename}')
        return self.Wordlist(filename, f'{self.temp_dir}/{filename}')

    def sort(self, source, output=None, unique=False):
        extra_params = ''
        if output is None:
            output = source
        if unique:
            extra_params += ' -u'
        self.run_shell(f'{self.sort_snippet} {source.path} -o {output.path} {extra_params}')

    def copy(self, source, destination):
        logger.debug(f'Copying `{source.path}` to {destination.path}')
        shutil.copyfile(source.path, destination.path)

    def append(self, source, destination):
        if pathlib.Path(source.path).is_file():
            self.run_shell(f'cat {source.path} >> {destination.path}')
        else:
            logger.warning(f'`{source.path}` not found!')

    def move(self, source, destination):
        logger.debug(f'Moving `{source.path}` to {destination.path}')
        shutil.move(source.path, destination.path)

    def delete(self, destination):
        logger.debug(f'Deleting `{destination.path}`')
        pathlib.Path.unlink(destination.path)

    def compare(self, left, right, output, append=False):
        if append:
            redir = '>>'
        else:
            redir = '>'
        self.run_shell(f'comm -13 {left.path} {right.path} {redir} {output.path}')

    @functools.cache
    def temp(self, name):
        return self.Wordlist(name, pathlib.Path(self.temp_dir, name + '.txt'))
    
    @functools.cache
    def root(self, name):
        return self.Wordlist(name, pathlib.Path(self.root_dir, name + '.txt'))
        
    @functools.cache
    def bits(self, name):
        return self.Wordlist(name, pathlib.Path(self.root_dir, 'bits', name + '.txt'))
    
    @functools.cache
    def keywords(self, name):
        return self.Wordlist(name, pathlib.Path(self.root_dir, 'keywords', name + '.txt'))
        
    @functools.cache
    def output(self, name):
        return self.Wordlist(name, pathlib.Path(self.output_dir, name + '.txt'))
    
    @functools.cache
    def right(self, left, right):
        return self.combine(self.RIGHT, left, right)

    @functools.cache
    def left(self, left, right):
        return self.combine(self.LEFT, left, right)
        
    @functools.cache
    def both(self, left, right):
        return self.combine(self.BOTH, left, right)
        
    def combine(self, method, left, right):
        if self.check_exist(left.path, right.path):
            name = None
            if method is self.RIGHT:
                name = f'{left.name}+{right.name}'
                if not pathlib.Path(self.temp_dir, name + '.txt').is_file():
                    logger.info(f'Combining `{left.name}` with `{right.name}`')
                    self.run_shell(f'{self.combinator_path} {left.path} {right.path} > {self.temp_dir}/{name}.txt')
            elif method is self.LEFT:
                name = f'{right.name}+{left.name}'
                if not pathlib.Path(self.temp_dir, name + '.txt').is_file():
                    logger.info(f'Combining `{right.name}` with `{left.name}`')
                    self.run_shell(f'{self.combinator_path} {right.path} {left.path} > {self.temp_dir}/{right.name}+{left.name}.txt')
            elif method is self.BOTH:
                name = f'{right.name}+{left.name}+{right.name}'
                if not pathlib.Path(self.temp_dir, f'{right.name}+{left.name}', '.txt').is_file():
                    self.run_shell(f'{self.combinator_path} {right.path} {left.path} > {self.temp_dir}/{right.name}+{left.name}.txt')
                if not pathlib.Path(self.temp_dir, name + '.txt').is_file():
                    logger.info(f'Combining `{left.name}` with `{right.name}`')
                    self.run_shell(f'{self.combinator_path} {self.temp_dir}/{right.name}+{left.name}.txt {right.path} > {self.temp_dir}/{name}.txt')
            else:
                raise NotImplementedError
            logger.info(f'Combined `{name}`')
            return self.Wordlist(name, pathlib.Path(self.temp_dir, name + '.txt'))

    def merge(self, destination, wordlists, compare=None):
        logger.info(f'Merging: {destination.path}')
        output_temp = self.temp(destination.name)
        wordlists_arg = list()
        for wordlist in wordlists:
            if wordlist is None:
                continue
            wordlist_path = str(wordlist.path)
            if not pathlib.Path(wordlist_path).is_file():
                wordlist_path = str(pathlib.Path(self.root_dir, wordlist_path))
            wordlists_arg.append(wordlist_path)
        wordlists_arg = ' '.join(wordlists_arg)
        # NOTE: Passing too many big files to sort directly leads to random segfault.
        pathlib.Path.unlink(destination.path, missing_ok=True)
        sort_cmd = f'awk "length >= {self.args.min_length}" {wordlists_arg} | {self.sort_snippet} | uniq > '
        if compare:
            self.run_shell(f'{sort_cmd} {output_temp.path}')
            self.run_shell(f'{self.rli2_path} {output_temp.path} {compare.path} >> {destination.path}')
            self.append(destination, compare)
            self.sort(compare)
        else:
            self.run_shell(f'{sort_cmd} {destination.path}')

    def concat(self, destination, wordlists):
        logger.debug(f'Concatenating: {destination.path}')
        pathlib.Path.unlink(destination.path, missing_ok=True)
        for wordlist in wordlists:
            self.append(wordlist, destination)

    def sort_common_less(self, path_method, list_prefix):
        common = path_method(f'{list_prefix}-common')
        less = path_method(f'{list_prefix}-less')
        self.sort(common, self.temp(f'{list_prefix}-sorted1'))
        self.sort(less, self.temp(f'{list_prefix}-sorted2'))
        self.compare(self.temp(f'{list_prefix}-sorted1'), self.temp(f'{list_prefix}-sorted2'), less)
        self.delete(common)
        self.move(self.temp(f'{list_prefix}-sorted1'), common)
        self.concat(path_method(f'{list_prefix}-all'), [common, less])
        self.sort(path_method(f'{list_prefix}-all'))

    def run(self):
        time_start = datetime.datetime.now()
        logger.info(f'Processing with class: {self.__class__.__name__}')
        logger.info(f'Base directory: {self.root_dir}')
        logger.info(f'Temporary directory: {self.temp_dir}')
        logger.info(f'Output directory: {self.output_dir}')
        logger.info(f'Using {self.args.cores} cores')
        logger.info(f'Using {self.args.memory} of memory')
        self.process()
        time_total = datetime.datetime.now() - time_start
        logger.info(f'Total time: {time_total}')
        logger.info(f'Done! You may want to clean up the temporary directory yourself: {self.temp_dir}')

    def process(self):
        raise NotImplementedError()


class Subdomains(Combinator):

    def process(self):

        logger.info('Generating subdomains')
        self.sort(self.keywords('brutas-subdomains'), self.temp('brutas-subdomains'))
        self.sort(self.keywords('brutas-subdomains-extra'), self.temp('brutas-subdomains-extra'))
        self.copy(self.temp('brutas-subdomains'), self.root('brutas-subdomains-1-small'))
        self.compare(self.temp('brutas-subdomains'), self.temp('brutas-subdomains-extra'), self.root('brutas-subdomains-1-small'), append=True)
        self.copy(self.root('brutas-subdomains-1-small'), self.root('brutas-subdomains-2-large'))
        self.run_shell(f'hashcat --stdout -r {self.root_dir}/rules/subdomains.rule {self.temp_dir}/brutas-subdomains.txt >> {self.root_dir}/brutas-subdomains-2-large.txt')


class Extensions(Combinator):

    def process(self):

        self.sort_common_less(self.root, 'brutas-http-files-extensions')


class HttpWords(Combinator):

    config_name = 'http-words'

    def process(self):

        logger.info('Generating HTTP paths/params')

        # NOTE: Process keywords
        self.wordlists_process()

        for lst in ['brutas-http-adj-adv-det', 'brutas-http-nouns', 'brutas-http-verbs']:
            self.sort_common_less(self.keywords, lst)


class HttpWordsPlain(HttpWords):

    def process(self):

        super().process()

        lowercase_verbs = self.temp(f'lowercase-brutas-http-verbs-{self.group_name}')
        lowercase_nouns = self.temp(f'lowercase-brutas-http-nouns-{self.group_name}')
        lowercase_aads = self.temp(f'lowercase-brutas-http-adj-adv-det-{self.group_name}')

        # NOTE: lowercase paths
        self.merge(
            self.output(f'brutas-http-discovery-plain-lowercase-{self.group_name}'),
            (
                lowercase_verbs,
                lowercase_nouns,
                lowercase_aads,
                self.right(lowercase_verbs, lowercase_nouns),
                self.right(lowercase_nouns, lowercase_verbs),
                self.right(lowercase_aads, lowercase_nouns),
                self.right(lowercase_verbs, lowercase_aads),
                self.right(lowercase_nouns, lowercase_aads),
            )
        )

        verbs_sep = self.right(lowercase_verbs, self.bits('separators-dash'))
        nouns_sep = self.right(lowercase_nouns, self.bits('separators-dash'))
        aads_sep = self.right(lowercase_aads, self.bits('separators-dash'))

        # NOTE: dash-case paths
        self.merge(
            self.output(f'brutas-http-discovery-plain-dash-{self.group_name}'),
            (
                lowercase_verbs,
                lowercase_nouns,
                lowercase_aads,
                self.right(verbs_sep, lowercase_nouns),
                self.right(nouns_sep, lowercase_verbs),
                self.right(aads_sep, lowercase_nouns),
                self.right(verbs_sep, lowercase_aads),
                self.right(nouns_sep, lowercase_aads),
            )
        )

        verbs_sep = self.right(lowercase_verbs, self.bits('separators-underscore'))
        nouns_sep = self.right(lowercase_nouns, self.bits('separators-underscore'))
        aads_sep = self.right(lowercase_aads, self.bits('separators-underscore'))

        # NOTE: snake_case paths
        self.merge(
            self.output(f'brutas-http-discovery-plain-underscore-{self.group_name}'),
            (
                lowercase_verbs,
                lowercase_nouns,
                lowercase_aads,
                self.right(verbs_sep, lowercase_nouns),
                self.right(nouns_sep, lowercase_verbs),
                self.right(aads_sep, lowercase_nouns),
                self.right(verbs_sep, lowercase_aads),
                self.right(nouns_sep, lowercase_aads),
            )
        )

        capitalize_verbs = self.temp(f'capitalize-brutas-http-verbs-{self.group_name}')
        capitalize_nouns = self.temp(f'capitalize-brutas-http-nouns-{self.group_name}')
        capitalize_aads = self.temp(f'capitalize-brutas-http-adj-adv-det-{self.group_name}')

        # NOTE: CamelCase paths
        self.merge(
            self.output(f'brutas-http-discovery-plain-camelcase-{self.group_name}'),
            (
                capitalize_verbs,
                capitalize_nouns,
                capitalize_aads,
                self.right(capitalize_verbs, capitalize_nouns),
                self.right(capitalize_nouns, capitalize_verbs),
                self.right(capitalize_aads, capitalize_nouns),
                self.right(capitalize_verbs, capitalize_aads),
                self.right(capitalize_nouns, capitalize_aads),
            )
        )

        # NOTE: lowerCamelCase paths
        self.merge(
            self.output(f'brutas-http-discovery-plain-lowercamelcase-{self.group_name}'),
            (
                lowercase_verbs,
                lowercase_nouns,
                lowercase_aads,
                self.right(lowercase_verbs, capitalize_nouns),
                self.right(lowercase_nouns, capitalize_verbs),
                self.right(lowercase_aads, capitalize_nouns),
                self.right(lowercase_verbs, capitalize_aads),
                self.right(lowercase_nouns, capitalize_aads),
            )
        )


class HttpWordsSuffixes(HttpWords):

    def process(self):

        super().process()

        lowercase_nouns = self.temp(f'lowercase-brutas-http-nouns-{self.group_name}')
        lowercase_aads = self.temp(f'lowercase-brutas-http-adj-adv-det-{self.group_name}')
        lowercase_suffixes = self.temp('lowercase-brutas-http-suffixes')
        aads_nouns = self.right(lowercase_aads, lowercase_nouns)

        # NOTE: lowercase paths
        self.merge(
            self.output(f'brutas-http-discovery-suffixes-lowercase-{self.group_name}'),
            (
                self.right(aads_nouns, lowercase_suffixes),
            )
        )

        nouns_sep = self.right(lowercase_nouns, self.bits('separators-dash'))
        aads_sep = self.right(lowercase_aads, self.bits('separators-dash'))
        aads_nouns_sep = self.right(aads_sep, nouns_sep)

        # NOTE: dash-case paths
        self.merge(
            self.output(f'brutas-http-discovery-suffixes-dash-{self.group_name}'),
            (
                self.right(aads_nouns_sep, lowercase_suffixes),
            )
        )

        nouns_sep = self.right(lowercase_nouns, self.bits('separators-underscore'))
        aads_sep = self.right(lowercase_aads, self.bits('separators-underscore'))
        aads_nouns_sep = self.right(aads_sep, nouns_sep)

        # NOTE: snake_case paths
        self.merge(
            self.output(f'brutas-http-discovery-suffixes-underscore-{self.group_name}'),
            (
                self.right(aads_nouns_sep, lowercase_suffixes),
            )
        )

        capitalize_nouns = self.temp(f'capitalize-brutas-http-nouns-{self.group_name}')
        capitalize_aads = self.temp(f'capitalize-brutas-http-adj-adv-det-{self.group_name}')
        capitalize_suffixes = self.temp('capitalize-brutas-http-suffixes')
        aads_nouns = self.right(capitalize_aads, capitalize_nouns)

        # NOTE: CamelCase paths
        self.merge(
            self.output(f'brutas-http-discovery-suffixes-camelcase-{self.group_name}'),
            (
                self.right(aads_nouns, capitalize_suffixes),
            )
        )

        aads_nouns = self.right(lowercase_aads, capitalize_nouns)

        # NOTE: lowerCamelCase paths
        self.merge(
            self.output(f'brutas-http-discovery-suffixes-lowercamelcase-{self.group_name}'),
            (
                self.right(aads_nouns, capitalize_suffixes),
            )
        )


class HttpWordsDouble(HttpWords):

    def process(self):

        super().process()

        lowercase_verbs = self.temp(f'lowercase-brutas-http-verbs-{self.group_name}')
        lowercase_nouns = self.temp(f'lowercase-brutas-http-nouns-{self.group_name}')
        lowercase_aads = self.temp(f'lowercase-brutas-http-adj-adv-det-{self.group_name}')
        aads_nouns = self.right(lowercase_aads, lowercase_nouns)

        # NOTE: lowercase paths
        self.merge(
            self.output(f'brutas-http-discovery-double-lowercase-{self.group_name}'),
            (
                self.right(lowercase_verbs, aads_nouns),
            )
        )

        verbs_sep = self.right(lowercase_verbs, self.bits('separators-dash'))
        nouns_sep = self.right(lowercase_nouns, self.bits('separators-dash'))
        aads_sep = self.right(lowercase_aads, self.bits('separators-dash'))
        aads_nouns = self.right(aads_sep, lowercase_nouns)

        # NOTE: dash-case paths
        self.merge(
            self.output(f'brutas-http-discovery-double-dash-{self.group_name}'),
            (
                self.right(verbs_sep, aads_nouns),
            )
        )

        verbs_sep = self.right(lowercase_verbs, self.bits('separators-underscore'))
        nouns_sep = self.right(lowercase_nouns, self.bits('separators-underscore'))
        aads_sep = self.right(lowercase_aads, self.bits('separators-underscore'))
        aads_nouns = self.right(aads_sep, lowercase_nouns)

        # NOTE: snake_case paths
        self.merge(
            self.output(f'brutas-http-discovery-double-underscore-{self.group_name}'),
            (
                self.right(verbs_sep, aads_nouns),
            )
        )

        capitalize_verbs = self.temp(f'capitalize-brutas-http-verbs-{self.group_name}')
        capitalize_nouns = self.temp(f'capitalize-brutas-http-nouns-{self.group_name}')
        capitalize_aads = self.temp(f'capitalize-brutas-http-adj-adv-det-{self.group_name}')
        aads_nouns = self.right(capitalize_aads, capitalize_nouns)

        # NOTE: CamelCase paths
        self.merge(
            self.output(f'brutas-http-discovery-double-camelcase-{self.group_name}'),
            (
                self.right(capitalize_verbs, aads_nouns),
            )
        )

        # NOTE: lowerCamelCase paths
        self.merge(
            self.output(f'brutas-http-discovery-double-lowercamelcase-{self.group_name}'),
            (
                self.right(lowercase_verbs, aads_nouns),
            )
        )


class HttpWordsPlainCommon(HttpWordsPlain):

    group_name = 'common'


class HttpWordsSuffixesCommon(HttpWordsSuffixes):

    group_name = 'common'


class HttpWordsDoubleCommon(HttpWordsDouble):

    group_name = 'common'


class HttpWordsPlainAll(HttpWordsPlain):

    group_name = 'all'


class HttpWordsSuffixesAll(HttpWordsSuffixes):

    group_name = 'all'


class HttpWordsDoubleAll(HttpWordsDouble):

    group_name = 'all'


class Passwords(Combinator):

    config_name = 'passwords'
    passwords_all = 'brutas-passwords-all'

    def process(self):

        logger.info('Preparing bits')

        for lst in ['extra', 'numbers']:
            self.sort_common_less(self.bits, lst)

        logger.info('Preparing keyword lists')

        common = self.keywords('brutas-lang-int-common')
        less = self.keywords('brutas-lang-int-less')
        self.sort(common, self.temp('lowercase-brutas-lang-int-common'))
        self.sort(less, self.temp('lowercase-brutas-lang-int-less'))
        self.compare(self.temp('lowercase-brutas-lang-int-common'), self.temp('lowercase-brutas-lang-int-less'), less)
        self.delete(common)
        self.copy(self.temp('lowercase-brutas-lang-int-common'), common)

        # NOTE: Combine all languages
        self.sort(self.keywords('brutas-lang-*'), self.temp('lowercase-brutas-all-lang'), unique=True)
        self.delete(self.keywords('brutas-all-lang'))
        self.copy(self.temp('lowercase-brutas-all-lang'), self.keywords('brutas-all-lang'))

        # NOTE: Initialize lookup/compare set
        self.sort(self.root('brutas-passwords-1-xxs'), self.temp(self.passwords_all))

        # NOTE: Process keywords
        self.wordlists_process()

        # NOTE: Prepare some lists beforehand
        separators = self.bits('separators')
        self.left(self.temp('simple-brutas-usernames'), separators)
        self.left(self.temp('simple-brutas-usernames-small'), separators)
        self.right(self.temp('simple-brutas-usernames'), separators)
        self.right(self.temp('simple-brutas-usernames-small'), separators)
        self.right(self.temp('simple-brutas-passwords-patterns'), separators)


class BasicPasswords(Passwords):

    def process(self):

        super().process()

        # NOTE: Change the order here...
        self.merge(
            self.output('brutas-passwords-2-xs'),
            (
                self.root('brutas-passwords-classics'),
                self.root('brutas-passwords-patterns'),
                self.root('brutas-usernames'),
            ),
            compare=self.temp(self.passwords_all)
        )

        usernames = self.temp('simple-brutas-usernames-small')
        usernames_sep = self.temp('simple-brutas-usernames-small+separators')

        self.merge(
            self.output('brutas-passwords-3-s'),
            (
                self.root('brutas-passwords-top'),
                self.root('brutas-passwords-unique'),
                self.root('brutas-passwords-numbers'),
                self.left(usernames, self.bits('extra-common')),
                self.left(usernames, self.bits('functional')),
                self.right(usernames, self.bits('extra-common')),
                self.right(usernames, self.bits('numbers-common')),
                self.right(usernames, self.bits('years-current')),
                self.right(self.temp('simple-brutas-usernames-small+extra-common'), self.bits('years-current')),
                self.right(usernames_sep, self.bits('functional')),
                self.right(usernames_sep, self.bits('months')),
                self.right(usernames_sep, self.bits('years-current')),
                self.temp('simple-brutas-passwords-classics'),
                self.temp('simple-brutas-passwords-top'),
                self.temp('simple-brutas-usernames-small'),
            ),
            compare=self.temp(self.passwords_all)
        )

        self.merge(
            self.output('brutas-passwords-4-m'),
            (
                self.right(self.temp('simple-brutas-usernames-small'), self.bits('extra-less')),
                self.left(self.temp('separators+simple-brutas-usernames-small'), self.bits('functional')),
                self.left(self.temp('separators+simple-brutas-usernames-small'), self.bits('years-current')),
                self.right(self.temp('simple-brutas-passwords-patterns'), self.bits('months')),
                self.right(self.temp('simple-brutas-passwords-patterns'), self.bits('numbers-common')),
                self.right(self.temp('simple-brutas-passwords-patterns'), self.bits('years-current')),
                self.right(self.temp('simple-brutas-usernames-small'), self.bits('years-all')),
                self.right(self.temp('simple-brutas-usernames-small+extra-common'), self.bits('extra-common')),
                self.right(self.temp('simple-brutas-usernames-small+numbers-common'), self.bits('extra-common')),
                self.right(self.temp('simple-brutas-usernames-small+years-current'), self.bits('extra-common')),
                self.right(self.temp('simple-brutas-lang-int-common'), self.bits('extra-most-common')),
                self.temp('simple-brutas-lang-int-common'),
                self.temp('both-brutas-usernames-small'),
                self.temp('repeat-brutas-usernames-small'),
                self.temp('hax0r-brutas-usernames-small'),
                self.temp('hax0r-brutas-passwords-classics'),
                self.temp('hax0r-brutas-usernames'),
            ),
            compare=self.temp(self.passwords_all)
        )


class ExtendedPasswords(Passwords):

    def process(self):

        super().process()

        # NOTE: Generate here, don't include in merge
        self.right(self.temp('simple-brutas-lang-int-common'), self.bits('months'))
        self.right(self.temp('simple-brutas-lang-int-common'), self.bits('years-all'))
        self.right(self.temp('simple-brutas-lang-int-common'), self.bits('separators'))
        self.right(self.temp('simple-brutas-lang-int-common+months'), self.bits('separators'))
        self.right(self.temp('simple-brutas-lang-int-common+years-all'), self.bits('separators'))

        usernames = self.temp('simple-brutas-usernames')

        self.merge(
            self.output('brutas-passwords-5-l'),
            (
                self.left(usernames, self.bits('extra-common')),
                self.left(usernames, self.bits('functional')),
                self.left(usernames, self.bits('numbers-common')),
                self.right(self.temp('extra-common+simple-brutas-usernames'), self.bits('months')),
                self.right(self.temp('extra-common+simple-brutas-usernames'), self.bits('years-current')),
                self.right(self.temp('hax0r-brutas-usernames'), self.bits('extra-common')),
                self.right(self.temp('simple-brutas-lang-int-common'), self.bits('extra-common')),
                self.right(self.temp('simple-brutas-lang-int-common'), self.bits('months')),
                self.right(self.temp('simple-brutas-passwords-patterns'), self.bits('extra-common')),
                self.right(self.temp('simple-brutas-passwords-patterns'), self.bits('numbers-less')),
                self.right(self.temp('simple-brutas-passwords-patterns'), self.bits('years-all')),
                self.right(usernames, self.bits('extra-common')),
                self.right(usernames, self.bits('extra-less')),
                self.right(usernames, self.bits('numbers-common')),
                self.right(usernames, self.bits('years-all')),
                self.right(self.temp('simple-brutas-usernames+extra-common'), self.bits('years-current')),
                self.right(self.temp('simple-brutas-usernames+separators'), self.bits('months')),
                self.right(self.temp('simple-brutas-usernames+separators'), self.bits('years-current')),
                self.right(self.temp('simple-brutas-usernames+years-all'), self.bits('extra-common')),
                self.temp('simple-brutas-lang-int-less'),
                self.temp('both-brutas-usernames'),
                self.temp('complex-brutas-usernames-small'),
                self.temp('hax0r-brutas-passwords-top'),
                self.temp('hax0r-brutas-passwords-unique'),
            ),
            compare=self.temp(self.passwords_all)
        )

        self.merge(
            self.output('brutas-passwords-6-xl'),
            (
                self.both(self.temp('repeat-brutas-usernames'), self.bits('extra-common')),
                self.left(self.temp('simple-brutas-usernames'), self.bits('extra-less')),
                self.left(self.temp('simple-brutas-usernames'), self.bits('numbers-less')),
                self.right(self.temp('extra-common+simple-brutas-usernames'), self.bits('years-all')),
                self.right(self.temp('simple-brutas-lang-int-common'), self.bits('numbers-common')),
                self.right(self.temp('simple-brutas-lang-int-common'), self.bits('years-all')),
                self.right(self.temp('simple-brutas-lang-int-less'), self.bits('extra-common')),
                self.right(self.temp('simple-brutas-passwords-patterns+separators'), self.bits('numbers-common')),
                self.right(self.temp('simple-brutas-passwords-patterns+separators'), self.bits('numbers-less')),
                self.right(self.temp('simple-brutas-passwords-patterns+separators'), self.bits('years-all')),
                self.right(self.temp('simple-brutas-usernames'), self.bits('functional')),
                self.right(self.temp('simple-brutas-usernames'), self.bits('numbers-less')),
                self.right(self.temp('simple-brutas-usernames+extra-common'), self.bits('extra-common')),
                self.right(self.temp('simple-brutas-usernames+extra-common'), self.bits('years-all')),
                self.right(self.temp('simple-brutas-usernames+numbers-common'), self.bits('extra-common')),
                self.right(self.temp('simple-brutas-usernames+separators'), self.bits('functional')),
                self.right(self.temp('simple-brutas-usernames+separators'), self.bits('years-all')),
                self.right(self.temp('simple-brutas-usernames-small+separators+months'), self.bits('years-current')),
                self.right(self.temp('simple-brutas-usernames-small+years-all'), self.bits('extra-common')),
                self.temp('complex-brutas-all-lang'),
                self.temp('complex-brutas-passwords-classics'),
                self.temp('complex-brutas-passwords-unique'),
                self.temp('complex-brutas-usernames'),
                self.temp('hax0r-brutas-all-lang'),
                self.temp('repeat-brutas-usernames'),
                self.temp('simple-brutas-all-lang'),
            ),
            compare=self.temp(self.passwords_all)
        )


class BigPasswords(Passwords):

    def process(self):

        super().process()

        # NOTE: Generate here, don't include in merge
        self.right(self.temp('simple-brutas-lang-int-common'), self.bits('months'))
        self.right(self.temp('simple-brutas-lang-int-common'), self.bits('years-all'))
        self.right(self.temp('simple-brutas-lang-int-common'), self.bits('separators'))
        self.right(self.temp('simple-brutas-lang-int-common+months'), self.bits('separators'))
        self.right(self.temp('simple-brutas-lang-int-common+years-all'), self.bits('separators'))

        self.merge(
            self.output('brutas-passwords-7-xxl'),
            (
                self.both(self.temp('repeat-brutas-usernames'), self.bits('extra-less')),
                self.left(self.temp('simple-brutas-lang-int-common'), self.bits('extra-common')),
                self.left(self.temp('simple-brutas-lang-int-common'), self.bits('extra-less')),
                self.left(self.temp('simple-brutas-lang-int-common'), self.bits('numbers-common')),
                self.left(self.temp('simple-brutas-lang-int-common'), self.bits('numbers-less')),
                self.left(self.temp('simple-brutas-usernames+numbers-common'), self.bits('extra-common')),
                self.right(self.temp('hax0r-brutas-usernames'), self.bits('extra-less')),
                self.right(self.temp('numbers-common+simple-brutas-lang-int-common'), self.bits('extra-common')),
                self.right(self.temp('numbers-common+simple-brutas-lang-int-common'), self.bits('extra-less')),
                self.right(self.temp('numbers-common+simple-brutas-usernames'), self.bits('extra-common')),
                self.right(self.temp('numbers-common+simple-brutas-usernames'), self.bits('extra-less')),
                self.right(self.temp('numbers-less+simple-brutas-lang-int-common'), self.bits('extra-less')),
                self.right(self.temp('numbers-less+simple-brutas-usernames'), self.bits('extra-common')),
                self.right(self.temp('numbers-less+simple-brutas-usernames'), self.bits('extra-less')),
                self.right(self.temp('simple-brutas-lang-int-common'), self.bits('extra-less')),
                self.right(self.temp('simple-brutas-lang-int-common'), self.bits('numbers-less')),
                self.right(self.temp('simple-brutas-lang-int-common+extra-common'), self.bits('months')),
                self.right(self.temp('simple-brutas-lang-int-common+extra-common'), self.bits('years-all')),
                self.right(self.temp('simple-brutas-lang-int-common+extra-less'), self.bits('months')),
                self.right(self.temp('simple-brutas-lang-int-common+extra-less'), self.bits('years-all')),
                self.right(self.temp('simple-brutas-lang-int-common+months'), self.bits('extra-common')),
                self.right(self.temp('simple-brutas-lang-int-common+months'), self.bits('extra-less')),
                self.right(self.temp('simple-brutas-lang-int-common+months+separators'), self.bits('years-all')),
                self.right(self.temp('simple-brutas-lang-int-common+numbers-common'), self.bits('extra-common')),
                self.right(self.temp('simple-brutas-lang-int-common+numbers-common'), self.bits('extra-less')),
                self.right(self.temp('simple-brutas-lang-int-common+numbers-less'), self.bits('extra-common')),
                self.right(self.temp('simple-brutas-lang-int-common+numbers-less'), self.bits('extra-less')),
                self.right(self.temp('simple-brutas-lang-int-common+separators'), self.bits('functional')),
                self.right(self.temp('simple-brutas-lang-int-common+separators'), self.bits('months')),
                self.right(self.temp('simple-brutas-lang-int-common+separators'), self.bits('years-all')),
                self.right(self.temp('simple-brutas-lang-int-common+separators+months'), self.bits('years-all')),
                self.right(self.temp('simple-brutas-lang-int-common+separators+years-all'), self.bits('months')),
                self.right(self.temp('simple-brutas-lang-int-common+years-all'), self.bits('extra-common')),
                self.right(self.temp('simple-brutas-lang-int-common+years-all'), self.bits('months')),
                self.right(self.temp('simple-brutas-lang-int-common+years-all+separators'), self.bits('months')),
                self.right(self.temp('simple-brutas-usernames+numbers-common'), self.bits('extra-less')),
                self.right(self.temp('simple-brutas-usernames+numbers-less'), self.bits('extra-common')),
                self.right(self.temp('simple-brutas-usernames+numbers-less'), self.bits('extra-less')),
                self.right(self.temp('simple-brutas-usernames+separators'), self.bits('extra-common')),
                self.right(self.temp('simple-brutas-usernames+separators+months'), self.bits('separators')),
                self.right(self.temp('simple-brutas-usernames+separators+months'), self.bits('years-all')),
                self.right(self.temp('simple-brutas-usernames+separators+months+separators'), self.bits('years-all')),
                self.rule(self.temp('hax0r-brutas-usernames+extra-common'), 'complex'),
                self.rule(self.temp('hax0r-brutas-usernames+extra-less'), 'complex'),
                self.temp('both-brutas-lang-int-common'),
                self.temp('both-brutas-passwords-classics'),
                self.temp('both-brutas-passwords-top'),
                self.temp('both-brutas-passwords-unique'),
                self.temp('hax0r-brutas-lang-int-common'),
            ),
            compare=self.temp(self.passwords_all)
        )


class CustomPasswords(Passwords):

    config_name = 'custom'

    def process(self):

        super().process()

        self.wordlists_process()

        self.merge(
            self.output('brutas-passwords-custom'),
            (
                self.left(self.temp('hax0r-brutas-custom'), self.bits('extra-all')),
                self.left(self.temp('hax0r-brutas-custom'), self.bits('numbers-all')),
                self.left(self.temp('hax0r-brutas-custom'), self.bits('separators')),
                self.left(self.temp('hax0r-brutas-custom'), self.bits('months')),
                self.left(self.temp('hax0r-brutas-custom'), self.bits('years-current')),
                self.left(self.temp('repeat-brutas-custom'), self.bits('extra-all')),
                self.left(self.temp('repeat-brutas-custom'), self.bits('numbers-all')),
                self.left(self.temp('repeat-brutas-custom'), self.bits('separators')),
                self.left(self.temp('repeat-brutas-custom'), self.bits('months')),
                self.left(self.temp('repeat-brutas-custom'), self.bits('years-current')),
                self.left(self.temp('simple-brutas-custom'), self.bits('extra-all')),
                self.left(self.temp('simple-brutas-custom'), self.bits('numbers-all')),
                self.left(self.temp('simple-brutas-custom'), self.bits('separators')),
                self.left(self.temp('simple-brutas-custom'), self.bits('months')),
                self.left(self.temp('simple-brutas-custom'), self.bits('years-current')),
                self.left(self.temp('separators+hax0r-brutas-custom'), self.bits('functional')),
                self.left(self.temp('separators+hax0r-brutas-custom'), self.bits('months')),
                self.left(self.temp('separators+hax0r-brutas-custom'), self.bits('years-current')),
                self.left(self.temp('separators+repeat-brutas-custom'), self.bits('functional')),
                self.left(self.temp('separators+repeat-brutas-custom'), self.bits('months')),
                self.left(self.temp('separators+repeat-brutas-custom'), self.bits('years-current')),
                self.left(self.temp('separators+simple-brutas-custom'), self.bits('functional')),
                self.left(self.temp('separators+simple-brutas-custom'), self.bits('months')),
                self.left(self.temp('separators+simple-brutas-custom'), self.bits('years-current')),
                self.left(self.temp('years-current+hax0r-brutas-custom'), self.bits('extra-all')),
                self.left(self.temp('years-current+hax0r-brutas-custom'), self.bits('months')),
                self.left(self.temp('years-current+hax0r-brutas-custom'), self.bits('separators')),
                self.left(self.temp('years-current+repeat-brutas-custom'), self.bits('extra-all')),
                self.left(self.temp('years-current+repeat-brutas-custom'), self.bits('months')),
                self.left(self.temp('years-current+repeat-brutas-custom'), self.bits('separators')),
                self.left(self.temp('years-current+separators+hax0r-brutas-custom'), self.bits('months')),
                self.left(self.temp('years-current+separators+repeat-brutas-custom'), self.bits('months')),
                self.left(self.temp('years-current+separators+simple-brutas-custom'), self.bits('months')),
                self.left(self.temp('years-current+simple-brutas-custom'), self.bits('extra-all')),
                self.left(self.temp('years-current+simple-brutas-custom'), self.bits('months')),
                self.left(self.temp('years-current+simple-brutas-custom'), self.bits('separators')),
                self.right(self.temp('extra-all+hax0r-brutas-custom'), self.bits('months')),
                self.right(self.temp('extra-all+hax0r-brutas-custom'), self.bits('years-current')),
                self.right(self.temp('extra-all+repeat-brutas-custom'), self.bits('months')),
                self.right(self.temp('extra-all+repeat-brutas-custom'), self.bits('years-current')),
                self.right(self.temp('extra-all+simple-brutas-custom'), self.bits('months')),
                self.right(self.temp('extra-all+simple-brutas-custom'), self.bits('years-current')),
                self.right(self.temp('hax0r-brutas-custom'), self.bits('extra-all')),
                self.right(self.temp('hax0r-brutas-custom'), self.bits('months')),
                self.right(self.temp('hax0r-brutas-custom'), self.bits('numbers-common')),
                self.right(self.temp('hax0r-brutas-custom'), self.bits('separators')),
                self.right(self.temp('hax0r-brutas-custom'), self.bits('years-current')),
                self.right(self.temp('hax0r-brutas-custom+extra-all'), self.bits('months')),
                self.right(self.temp('hax0r-brutas-custom+extra-all'), self.bits('years-current')),
                self.right(self.temp('hax0r-brutas-custom+months'), self.bits('extra-all')),
                self.right(self.temp('hax0r-brutas-custom+months'), self.bits('separators')),
                self.right(self.temp('hax0r-brutas-custom+months+separators'), self.bits('years-current')),
                self.right(self.temp('hax0r-brutas-custom+numbers-common'), self.bits('extra-all')),
                self.right(self.temp('hax0r-brutas-custom+separators'), self.bits('functional')),
                self.right(self.temp('hax0r-brutas-custom+separators'), self.bits('months')),
                self.right(self.temp('hax0r-brutas-custom+separators'), self.bits('years-current')),
                self.right(self.temp('hax0r-brutas-custom+separators+months'), self.bits('years-current')),
                self.right(self.temp('hax0r-brutas-custom+separators+years-current'), self.bits('months')),
                self.right(self.temp('hax0r-brutas-custom+years-current'), self.bits('extra-all')),
                self.right(self.temp('hax0r-brutas-custom+years-current'), self.bits('months')),
                self.right(self.temp('hax0r-brutas-custom+years-current'), self.bits('separators')),
                self.right(self.temp('hax0r-brutas-custom+years-current+separators'), self.bits('months')),
                self.right(self.temp('months+hax0r-brutas-custom'), self.bits('extra-all')),
                self.right(self.temp('months+repeat-brutas-custom'), self.bits('extra-all')),
                self.right(self.temp('months+separators+simple-brutas-custom'), self.bits('extra-common')),
                self.right(self.temp('months+simple-brutas-custom'), self.bits('extra-all')),
                self.right(self.temp('numbers-all+hax0r-brutas-custom'), self.bits('extra-all')),
                self.right(self.temp('numbers-all+repeat-brutas-custom'), self.bits('extra-all')),
                self.right(self.temp('numbers-all+simple-brutas-custom'), self.bits('extra-all')),
                self.right(self.temp('repeat-brutas-custom'), self.bits('extra-all')),
                self.right(self.temp('repeat-brutas-custom'), self.bits('numbers-all')),
                self.right(self.temp('repeat-brutas-custom+numbers-all'), self.bits('extra-all')),
                self.right(self.temp('simple-brutas-custom'), self.bits('extra-all')),
                self.right(self.temp('simple-brutas-custom'), self.bits('months')),
                self.right(self.temp('simple-brutas-custom'), self.bits('numbers-all')),
                self.right(self.temp('simple-brutas-custom'), self.bits('separators')),
                self.right(self.temp('simple-brutas-custom'), self.bits('years-current')),
                self.right(self.temp('simple-brutas-custom+extra-all'), self.bits('months')),
                self.right(self.temp('simple-brutas-custom+extra-all'), self.bits('years-current')),
                self.right(self.temp('simple-brutas-custom+months'), self.bits('extra-all')),
                self.right(self.temp('simple-brutas-custom+months'), self.bits('separators')),
                self.right(self.temp('simple-brutas-custom+months+separators'), self.bits('years-current')),
                self.right(self.temp('simple-brutas-custom+numbers-all'), self.bits('extra-all')),
                self.right(self.temp('simple-brutas-custom+separators'), self.bits('functional')),
                self.right(self.temp('simple-brutas-custom+separators'), self.bits('months')),
                self.right(self.temp('simple-brutas-custom+separators'), self.bits('years-current')),
                self.right(self.temp('simple-brutas-custom+separators+months'), self.bits('years-current')),
                self.right(self.temp('simple-brutas-custom+separators+years-current'), self.bits('months')),
                self.right(self.temp('simple-brutas-custom+years-current'), self.bits('extra-all')),
                self.right(self.temp('simple-brutas-custom+years-current'), self.bits('months')),
                self.right(self.temp('simple-brutas-custom+years-current'), self.bits('separators')),
                self.right(self.temp('simple-brutas-custom+years-current+separators'), self.bits('months')),
                self.right(self.temp('years-current+separators+hax0r-brutas-custom'), self.bits('extra-common')),
                self.right(self.temp('years-current+separators+repeat-brutas-custom'), self.bits('extra-common')),
                self.right(self.temp('years-current+separators+simple-brutas-custom'), self.bits('extra-common')),
                self.rule(self.temp('extra-all+hax0r-brutas-custom'), 'complex'),
                self.rule(self.temp('extra-all+repeat-brutas-custom'), 'complex'),
                self.rule(self.temp('extra-all+simple-brutas-custom'), 'complex'),
                self.rule(self.temp('hax0r-brutas-custom+extra-all'), 'complex'),
                self.rule(self.temp('hax0r-brutas-custom+numbers-common'), 'complex'),
                self.rule(self.temp('numbers-all+hax0r-brutas-custom'), 'complex'),
                self.rule(self.temp('numbers-all+repeat-brutas-custom'), 'complex'),
                self.rule(self.temp('numbers-all+simple-brutas-custom'), 'complex'),
                self.rule(self.temp('repeat-brutas-custom+extra-all'), 'complex'),
                self.rule(self.temp('repeat-brutas-custom+numbers-all'), 'complex'),
                self.rule(self.temp('simple-brutas-custom+numbers-all'), 'complex'),
                self.temp('simple-brutas-custom'),
                self.temp('hax0r-brutas-custom'),
                self.temp('repeat-brutas-custom'),
            )
        )


class MergeAll(Combinator):

    def process(self):

        self.concat(
            self.output('brutas-passwords-all'),
            (
                self.root('brutas-passwords-1-xxs'),
                self.root('brutas-passwords-2-xs'),
                self.root('brutas-passwords-3-s'),
                self.root('brutas-passwords-4-m'),
                self.root('brutas-passwords-5-l'),
                self.root('brutas-passwords-6-xl'),
                self.root('brutas-passwords-7-xxl'),
            )
        )
