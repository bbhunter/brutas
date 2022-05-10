import datetime
import logging
import pathlib
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


class Combinator:

    rules = None
    wordlists = None

    def __init__(self, config, args):
        if self.rules is None:
            self.rules = config.RULES
        if self.wordlists is None:
            self.wordlists = config.WORDLISTS
        self.tmp_dir = str(pathlib.Path(args.temporary_dir).resolve())
        self.base_dir = config.BASE_DIR
        self.output_dir = str(pathlib.Path(args.output_dir).resolve())
        self.cores = '' if args.cores is None else '--parallel=' + args.cores
        self.memory = '-S ' + args.memory
        # NOTE: This is commented out as a decision rationale: it seems that
        #       sort's --compress-program ignores environment variables, leading to
        #       duplicates. To be resolved after looking into sort internals.
        # self.compress_program = '--compress-program=lzop' if self.run_shell('which lzop') else ''
        # self.sort_snippet = f'sort -T {self.tmp_dir} {self.compress_program} {self.cores} {self.memory}'
        self.sort_snippet = f'sort -T {self.tmp_dir} {self.cores} {self.memory}'
        self.args = args
        if pathlib.Path.exists(pathlib.Path(config.COMBINATOR_PATH)):
            self.combinator_path = config.COMBINATOR_PATH
        else:
            logger.error(f'Hashcat `combinator` not found at {config.COMBINATOR_PATH}')
            sys.exit(1)
        if pathlib.Path.exists(pathlib.Path(config.RLI2_PATH)):
            self.rli2_path = config.RLI2_PATH
        else:
            logger.error(f'Hashcat `rli2` not found at {config.RLI2_PATH}')
            sys.exit(1)

    def run_shell(self, cmd):
        logger.debug(cmd)
        return subprocess.run(f'(export LC_ALL=C; {cmd})', shell=True, stdout=subprocess.PIPE).stdout

    def wordlists_process(self):
        for rule in self.rules:
            logger.info(f'Processing wordlists with rules `{rule}`')
            for wordlist in self.wordlists:
                self.rule_process(str(pathlib.Path(self.base_dir, wordlist)), rule)

    def check_exist(self, *paths):
        for path in paths:
            if not pathlib.Path(path).is_file():
                logger.debug(f'Resource `{path}` not found, skipping')
                return False
        return True

    def rule_process(self, wordlist, rule):
        idx = wordlist.find('/')
        filename = rule + '-' + pathlib.Path(wordlist).name
        if not pathlib.Path(f'{self.tmp_dir}/{filename}').is_file():
            logger.info(f'Processing `{wordlist}` with rule `{rule}`')
            self.run_shell(f'hashcat --stdout -r {self.base_dir}/rules/{rule}.rule {wordlist} | {self.sort_snippet} | uniq > {self.tmp_dir}/{filename}')
        return f'{self.tmp_dir}/{filename}'

    def combine_right(self, wordlist, bits):
        if self.check_exist(f'{self.base_dir}/bits/{bits}.txt', f'{self.tmp_dir}/{wordlist}.txt'):
            if not pathlib.Path(f'{self.tmp_dir}/{wordlist}+{bits}.txt').is_file():
                logger.info(f'Combining `{wordlist}` with `{bits}`')
                self.run_shell(f'{self.combinator_path} {self.tmp_dir}/{wordlist}.txt {self.base_dir}/bits/{bits}.txt > {self.tmp_dir}/{wordlist}+{bits}.txt')
            return f'{self.tmp_dir}/{wordlist}+{bits}.txt'

    def combine_left(self, wordlist, bits):
        if self.check_exist(f'{self.base_dir}/bits/{bits}.txt', f'{self.tmp_dir}/{wordlist}.txt'):
            if not pathlib.Path(f'{self.tmp_dir}/{bits}+{wordlist}.txt').is_file():
                logger.info(f'Combining `{wordlist}` with `{bits}`')
                self.run_shell(f'{self.combinator_path} {self.base_dir}/bits/{bits}.txt {self.tmp_dir}/{wordlist}.txt > {self.tmp_dir}/{bits}+{wordlist}.txt')
            return f'{self.tmp_dir}/{bits}+{wordlist}.txt'

    def combine_both(self, wordlist, bits):
        if self.check_exist(f'{self.base_dir}/bits/{bits}.txt', f'{self.tmp_dir}/{wordlist}.txt'):
            if not pathlib.Path(f'{self.tmp_dir}/{bits}+{wordlist}.txt').is_file():
                self.run_shell(f'{self.combinator_path} {self.base_dir}/bits/{bits}.txt {self.tmp_dir}/{wordlist}.txt > {self.tmp_dir}/{bits}+{wordlist}.txt')
            if not pathlib.Path(f'{self.tmp_dir}/{bits}+{wordlist}+{bits}.txt').is_file():
                logger.info(f'Combining `{wordlist}` with `{bits}`')
                self.run_shell(f'{self.combinator_path} {self.tmp_dir}/{bits}+{wordlist}.txt {self.base_dir}/bits/{bits}.txt > {self.tmp_dir}/{bits}+{wordlist}+{bits}.txt')
            return f'{self.tmp_dir}/{bits}+{wordlist}+{bits}.txt'

    def get_output_file(self, output):
        return pathlib.Path(self.output_dir, output)

    def get_output_temp(self, output):
        return pathlib.Path(self.tmp_dir, output)

    def merge(self, output, wordlists, compare=None):
        output_file = self.get_output_file(output)
        output_temp = self.get_output_temp(output)
        logger.info(f'Merging: {output_file}')
        wordlists_arg = list()        
        for wordlist in wordlists:
            if wordlist is None:
                continue
            if not pathlib.Path(wordlist).is_file():
                wordlist = str(pathlib.Path(self.base_dir, wordlist))
            wordlists_arg.append(wordlist)
        wordlists_arg = ' '.join(wordlists_arg)
        # NOTE: Passing too many big files to sort directly leads to random segfault.
        pathlib.Path.unlink(output_file, missing_ok=True)
        sort_cmd = f'awk "length >= {self.args.min_length}" {wordlists_arg} | {self.sort_snippet} | uniq > '
        if compare:
            self.run_shell(f'{sort_cmd} {output_temp}')
            self.run_shell(f'{self.rli2_path} {output_temp} {self.tmp_dir}/brutas-passwords-compare.txt >> {output_file}')
            self.run_shell(f'cat {output_file} >> {self.tmp_dir}/brutas-passwords-compare.txt')
            self.run_shell(f'{self.sort_snippet} -o {self.tmp_dir}/brutas-passwords-compare.txt {self.tmp_dir}/brutas-passwords-compare.txt')
        else:
            self.run_shell(f'{sort_cmd} {output_file}')

    def concat(self, output, wordlists):
        output_file = self.get_output_file(output)
        output_temp = self.get_output_temp(output)
        logger.info(f'Concatenating: {output}')
        pathlib.Path.unlink(output_temp, missing_ok=True)
        for wordlist in wordlists:
            self.run_shell(f'cat {wordlist} >> {output_temp}')
        self.run_shell(f'mv {output_temp} {output_file}')

    def run(self):
        time_start = datetime.datetime.now()
        logger.info(f'Processing with class: {self.__class__.__name__}')
        logger.info(f'Base directory: {self.base_dir}')
        logger.info(f'Temporary directory: {self.tmp_dir}')
        logger.info(f'Output directory: {self.output_dir}')
        logger.info(f'Using {self.args.cores} cores')
        logger.info(f'Using {self.args.memory} of memory')
        self.process()
        time_total = datetime.datetime.now() - time_start
        logger.info(f'Total time: {time_total}')
        logger.info(f'Done! You may want to clean up the temporary directory yourself: {self.tmp_dir}')

    def process(self):
        raise NotImplementedError()


class Prepare(Combinator):

    def process(self):

        logger.info('Preparing bits')

        self.run_shell(f'{self.sort_snippet} {self.base_dir}/bits/extra-common.txt -o {self.tmp_dir}/extra-sorted1')
        self.run_shell(f'{self.sort_snippet} {self.base_dir}/bits/extra-less.txt -o {self.tmp_dir}/extra-sorted2')
        self.run_shell(f'comm -13 {self.tmp_dir}/extra-sorted1 {self.tmp_dir}/extra-sorted2 > {self.base_dir}/bits/extra-less.txt')
        self.run_shell(f'rm {self.base_dir}/bits/extra-common.txt')
        self.run_shell(f'mv {self.tmp_dir}/extra-sorted1 {self.base_dir}/bits/extra-common.txt')
        self.run_shell(f'cat {self.base_dir}/bits/extra-common.txt {self.base_dir}/bits/extra-less.txt > {self.base_dir}/bits/extra-all.txt')

        self.run_shell(f'{self.sort_snippet} {self.base_dir}/bits/numbers-common.txt -o {self.tmp_dir}/numbers-sorted1')
        self.run_shell(f'{self.sort_snippet} {self.base_dir}/bits/numbers-less.txt -o {self.tmp_dir}/numbers-sorted2')
        self.run_shell(f'comm -13 {self.tmp_dir}/numbers-sorted1 {self.tmp_dir}/numbers-sorted2 > {self.base_dir}/bits/numbers-less.txt')
        self.run_shell(f'rm {self.base_dir}/bits/numbers-common.txt')
        self.run_shell(f'mv {self.tmp_dir}/numbers-sorted1 {self.base_dir}/bits/numbers-common.txt')
        self.run_shell(f'cat {self.base_dir}/bits/numbers-common.txt {self.base_dir}/bits/numbers-less.txt > {self.base_dir}/bits/numbers-all.txt')


class Basic(Prepare):

    def process(self):

        super().process()

        logger.info('Generating subdomains')
        self.run_shell(f'{self.sort_snippet} {self.base_dir}/keywords/brutas-subdomains.txt -o {self.tmp_dir}/brutas-subdomains.txt')
        self.run_shell(f'{self.sort_snippet} {self.base_dir}/keywords/brutas-subdomains-extra.txt -o {self.tmp_dir}/brutas-subdomains-extra.txt')
        self.run_shell(f'cp {self.tmp_dir}/brutas-subdomains.txt {self.base_dir}/brutas-subdomains-1-small.txt')
        self.run_shell(f'comm -13 {self.tmp_dir}/brutas-subdomains.txt {self.tmp_dir}/brutas-subdomains-extra.txt >> {self.base_dir}/brutas-subdomains-1-small.txt')
        self.run_shell(f'cp {self.base_dir}/brutas-subdomains-1-small.txt {self.base_dir}/brutas-subdomains-2-large.txt')
        self.run_shell(f'hashcat --stdout -r {self.base_dir}/rules/subdomains.rule {self.tmp_dir}/brutas-subdomains.txt >> {self.base_dir}/brutas-subdomains-2-large.txt')

        logger.info('Preparing keyword lists')
        self.run_shell(f'{self.sort_snippet} {self.base_dir}/keywords/brutas-lang-int-common.txt -o {self.tmp_dir}/brutas-lang-int-common.txt')
        self.run_shell(f'{self.sort_snippet} {self.base_dir}/keywords/brutas-lang-int-less.txt -o {self.tmp_dir}/brutas-lang-int-less.txt')
        self.run_shell(f'comm -13 {self.tmp_dir}/brutas-lang-int-common.txt {self.tmp_dir}/brutas-lang-int-less.txt > {self.base_dir}/keywords/brutas-lang-int-less.txt')
        self.run_shell(f'rm {self.base_dir}/keywords/brutas-lang-int-common.txt')
        self.run_shell(f'cp {self.tmp_dir}/brutas-lang-int-common.txt {self.base_dir}/keywords/brutas-lang-int-common.txt')

        # NOTE: Combine all languages
        self.run_shell(f'{self.sort_snippet} -u {self.base_dir}/keywords/brutas-lang-*.txt -o {self.tmp_dir}/brutas-all-lang.txt')
        self.run_shell(f'rm {self.base_dir}/keywords/brutas-all-lang.txt')
        self.run_shell(f'cp {self.tmp_dir}/brutas-all-lang.txt {self.base_dir}/keywords/brutas-all-lang.txt')

        # NOTE: Initialize lookup/compare set
        self.run_shell(f'{self.sort_snippet} {self.base_dir}/brutas-passwords-1-xxs.txt > {self.tmp_dir}/brutas-passwords-compare.txt')

        # NOTE: Process keywords
        self.wordlists_process()

        # NOTE: Prepare some lists beforehand
        self.combine_left('simple-brutas-usernames', 'separators')
        self.combine_left('simple-brutas-usernames-small', 'separators')
        self.combine_right('simple-brutas-usernames', 'separators')
        self.combine_right('simple-brutas-usernames-small', 'separators')
        self.combine_right('simple-brutas-passwords-patterns', 'separators')

        # NOTE: Change the order here...
        self.merge(
            'brutas-passwords-2-xs.txt',
            (
                'brutas-passwords-classics.txt',
                'brutas-passwords-patterns.txt',
                'brutas-usernames.txt',
            ),
            compare=True
        )

        self.merge(
            'brutas-passwords-3-s.txt',
            (
                'brutas-passwords-top.txt',
                'brutas-passwords-unique.txt',
                'brutas-passwords-numbers.txt',
                self.combine_left('simple-brutas-usernames-small', 'extra-common'),
                self.combine_left('simple-brutas-usernames-small', 'functional'),
                self.combine_right('simple-brutas-usernames-small', 'extra-common'),
                self.combine_right('simple-brutas-usernames-small', 'numbers-common'),
                self.combine_right('simple-brutas-usernames-small', 'years-current'),
                self.combine_right('simple-brutas-usernames-small+extra-common', 'years-current'),
                self.combine_right('simple-brutas-usernames-small+separators', 'functional'),
                self.combine_right('simple-brutas-usernames-small+separators', 'months'),
                self.combine_right('simple-brutas-usernames-small+separators', 'years-current'),
                f'{self.tmp_dir}/simple-brutas-passwords-classics.txt',
                f'{self.tmp_dir}/simple-brutas-passwords-top.txt',
                f'{self.tmp_dir}/simple-brutas-usernames-small.txt',
            ),
            compare=True
        )

        self.merge(
            'brutas-passwords-4-m.txt',
            (
                self.combine_right('simple-brutas-usernames-small', 'extra-less'),
                self.combine_left('separators+simple-brutas-usernames-small', 'functional'),
                self.combine_left('separators+simple-brutas-usernames-small', 'years-current'),
                self.combine_right('simple-brutas-passwords-patterns', 'months'),
                self.combine_right('simple-brutas-passwords-patterns', 'numbers-common'),
                self.combine_right('simple-brutas-passwords-patterns', 'years-current'),
                self.combine_right('simple-brutas-usernames-small', 'years-all'),
                self.combine_right('simple-brutas-usernames-small+extra-common', 'extra-common'),
                self.combine_right('simple-brutas-usernames-small+numbers-common', 'extra-common'),
                self.combine_right('simple-brutas-usernames-small+years-current', 'extra-common'),
                self.combine_right('simple-brutas-lang-int-common', 'extra-most-common'),
                f'{self.tmp_dir}/simple-brutas-lang-int-common.txt',
                f'{self.tmp_dir}/both-brutas-usernames-small.txt',
                f'{self.tmp_dir}/repeat-brutas-usernames-small.txt',
                f'{self.tmp_dir}/hax0r-brutas-usernames-small.txt',
                f'{self.tmp_dir}/hax0r-brutas-passwords-classics.txt',
                f'{self.tmp_dir}/hax0r-brutas-usernames.txt',
            ),
            compare=True
        )


class Extended(Basic):

    def process(self):

        super().process()

        # NOTE: Generate here, don't include in merge
        self.combine_right('simple-brutas-lang-int-common', 'months')
        self.combine_right('simple-brutas-lang-int-common', 'years-all')
        self.combine_right('simple-brutas-lang-int-common', 'separators')
        self.combine_right('simple-brutas-lang-int-common+months', 'separators')
        self.combine_right('simple-brutas-lang-int-common+years-all', 'separators')

        self.merge(
            'brutas-passwords-5-l.txt',
            (
                self.combine_left('simple-brutas-usernames', 'extra-common'),
                self.combine_left('simple-brutas-usernames', 'functional'),
                self.combine_left('simple-brutas-usernames', 'numbers-common'),
                self.combine_right('extra-common+simple-brutas-usernames', 'months'),
                self.combine_right('extra-common+simple-brutas-usernames', 'years-current'),
                self.combine_right('hax0r-brutas-usernames', 'extra-common'),
                self.combine_right('simple-brutas-lang-int-common', 'extra-common'),
                self.combine_right('simple-brutas-lang-int-common', 'months'),
                self.combine_right('simple-brutas-passwords-patterns', 'extra-common'),
                self.combine_right('simple-brutas-passwords-patterns', 'numbers-less'),
                self.combine_right('simple-brutas-passwords-patterns', 'years-all'),
                self.combine_right('simple-brutas-usernames', 'extra-common'),
                self.combine_right('simple-brutas-usernames', 'extra-less'),
                self.combine_right('simple-brutas-usernames', 'numbers-common'),
                self.combine_right('simple-brutas-usernames', 'years-all'),
                self.combine_right('simple-brutas-usernames+extra-common', 'years-current'),
                self.combine_right('simple-brutas-usernames+separators', 'months'),
                self.combine_right('simple-brutas-usernames+separators', 'years-current'),
                self.combine_right('simple-brutas-usernames+years-all', 'extra-common'),
                f'{self.tmp_dir}/simple-brutas-lang-int-less.txt',
                f'{self.tmp_dir}/both-brutas-usernames.txt',
                f'{self.tmp_dir}/complex-brutas-usernames-small.txt',
                f'{self.tmp_dir}/hax0r-brutas-passwords-top.txt',
                f'{self.tmp_dir}/hax0r-brutas-passwords-unique.txt',
            ),
            compare=True
        )

        self.merge(
            'brutas-passwords-6-xl.txt',
            (
                self.combine_both('repeat-brutas-usernames', 'extra-common'),
                self.combine_left('simple-brutas-usernames', 'extra-less'),
                self.combine_left('simple-brutas-usernames', 'numbers-less'),
                self.combine_right('extra-common+simple-brutas-usernames', 'years-all'),
                self.combine_right('simple-brutas-lang-int-common', 'numbers-common'),
                self.combine_right('simple-brutas-lang-int-common', 'years-all'),
                self.combine_right('simple-brutas-lang-int-less', 'extra-common'),
                self.combine_right('simple-brutas-passwords-patterns+separators', 'numbers-common'),
                self.combine_right('simple-brutas-passwords-patterns+separators', 'numbers-less'),
                self.combine_right('simple-brutas-passwords-patterns+separators', 'years-all'),
                self.combine_right('simple-brutas-usernames', 'functional'),
                self.combine_right('simple-brutas-usernames', 'numbers-less'),
                self.combine_right('simple-brutas-usernames+extra-common', 'extra-common'),
                self.combine_right('simple-brutas-usernames+extra-common', 'years-all'),
                self.combine_right('simple-brutas-usernames+numbers-common', 'extra-common'),
                self.combine_right('simple-brutas-usernames+separators', 'functional'),
                self.combine_right('simple-brutas-usernames+separators', 'years-all'),
                self.combine_right('simple-brutas-usernames-small+separators+months', 'years-current'),
                self.combine_right('simple-brutas-usernames-small+years-all', 'extra-common'),
                f'{self.tmp_dir}/complex-brutas-all-lang.txt',
                f'{self.tmp_dir}/complex-brutas-passwords-classics.txt',
                f'{self.tmp_dir}/complex-brutas-passwords-unique.txt',
                f'{self.tmp_dir}/complex-brutas-usernames.txt',
                f'{self.tmp_dir}/hax0r-brutas-all-lang.txt',
                f'{self.tmp_dir}/repeat-brutas-usernames.txt',
                f'{self.tmp_dir}/simple-brutas-all-lang.txt',
            ),
            compare=True
        )

        self.merge(
            'brutas-passwords-7-xxl.txt',
            (
                self.combine_both('repeat-brutas-usernames', 'extra-less'),
                self.combine_left('simple-brutas-lang-int-common', 'extra-common'),
                self.combine_left('simple-brutas-lang-int-common', 'extra-less'),
                self.combine_left('simple-brutas-lang-int-common', 'numbers-common'),
                self.combine_left('simple-brutas-lang-int-common', 'numbers-less'),
                self.combine_left('simple-brutas-usernames+numbers-common', 'extra-common'),
                self.combine_right('hax0r-brutas-usernames', 'extra-less'),
                self.combine_right('numbers-common+simple-brutas-lang-int-common', 'extra-common'),
                self.combine_right('numbers-common+simple-brutas-lang-int-common', 'extra-less'),
                self.combine_right('numbers-common+simple-brutas-usernames', 'extra-common'),
                self.combine_right('numbers-common+simple-brutas-usernames', 'extra-less'),
                self.combine_right('numbers-less+simple-brutas-lang-int-common', 'extra-less'),
                self.combine_right('numbers-less+simple-brutas-usernames', 'extra-common'),
                self.combine_right('numbers-less+simple-brutas-usernames', 'extra-less'),
                self.combine_right('simple-brutas-lang-int-common', 'extra-less'),
                self.combine_right('simple-brutas-lang-int-common', 'numbers-less'),
                self.combine_right('simple-brutas-lang-int-common+extra-common', 'months'),
                self.combine_right('simple-brutas-lang-int-common+extra-common', 'years-all'),
                self.combine_right('simple-brutas-lang-int-common+extra-less', 'months'),
                self.combine_right('simple-brutas-lang-int-common+extra-less', 'years-all'),
                self.combine_right('simple-brutas-lang-int-common+months', 'extra-common'),
                self.combine_right('simple-brutas-lang-int-common+months', 'extra-less'),
                self.combine_right('simple-brutas-lang-int-common+months+separators', 'years-all'),
                self.combine_right('simple-brutas-lang-int-common+numbers-common', 'extra-common'),
                self.combine_right('simple-brutas-lang-int-common+numbers-common', 'extra-less'),
                self.combine_right('simple-brutas-lang-int-common+numbers-less', 'extra-common'),
                self.combine_right('simple-brutas-lang-int-common+numbers-less', 'extra-less'),
                self.combine_right('simple-brutas-lang-int-common+separators', 'functional'),
                self.combine_right('simple-brutas-lang-int-common+separators', 'months'),
                self.combine_right('simple-brutas-lang-int-common+separators', 'years-all'),
                self.combine_right('simple-brutas-lang-int-common+separators+months', 'years-all'),
                self.combine_right('simple-brutas-lang-int-common+separators+years-all', 'months'),
                self.combine_right('simple-brutas-lang-int-common+years-all', 'extra-common'),
                self.combine_right('simple-brutas-lang-int-common+years-all', 'months'),
                self.combine_right('simple-brutas-lang-int-common+years-all+separators', 'months'),
                self.combine_right('simple-brutas-usernames+numbers-common', 'extra-less'),
                self.combine_right('simple-brutas-usernames+numbers-less', 'extra-common'),
                self.combine_right('simple-brutas-usernames+numbers-less', 'extra-less'),
                self.combine_right('simple-brutas-usernames+separators', 'extra-common'),
                self.combine_right('simple-brutas-usernames+separators+months', 'separators'),
                self.combine_right('simple-brutas-usernames+separators+months', 'years-all'),
                self.combine_right('simple-brutas-usernames+separators+months+separators', 'years-all'),
                self.rule_process(f'{self.tmp_dir}/hax0r-brutas-usernames+extra-common.txt', 'complex'),
                self.rule_process(f'{self.tmp_dir}/hax0r-brutas-usernames+extra-less.txt', 'complex'),
                f'{self.tmp_dir}/both-brutas-lang-int-common.txt',
                f'{self.tmp_dir}/both-brutas-passwords-classics.txt',
                f'{self.tmp_dir}/both-brutas-passwords-top.txt',
                f'{self.tmp_dir}/both-brutas-passwords-unique.txt',
                f'{self.tmp_dir}/hax0r-brutas-lang-int-common.txt',
            ),
            compare=True
        )


class Custom(Prepare):

    wordlists = [
        'keywords/brutas-custom.txt',
    ]

    def process(self):

        super().process()

        self.wordlists_process()

        self.merge(
            'brutas-passwords-custom.txt',
            (
                self.combine_left('hax0r-brutas-custom', 'extra-all'),
                self.combine_left('hax0r-brutas-custom', 'numbers-all'),
                self.combine_left('hax0r-brutas-custom', 'separators'),
                self.combine_left('hax0r-brutas-custom', 'months'),
                self.combine_left('hax0r-brutas-custom', 'years-current'),
                self.combine_left('repeat-brutas-custom', 'extra-all'),
                self.combine_left('repeat-brutas-custom', 'numbers-all'),
                self.combine_left('repeat-brutas-custom', 'separators'),
                self.combine_left('repeat-brutas-custom', 'months'),
                self.combine_left('repeat-brutas-custom', 'years-current'),
                self.combine_left('simple-brutas-custom', 'extra-all'),
                self.combine_left('simple-brutas-custom', 'numbers-all'),
                self.combine_left('simple-brutas-custom', 'separators'),
                self.combine_left('simple-brutas-custom', 'months'),
                self.combine_left('simple-brutas-custom', 'years-current'),
                self.combine_left('separators+hax0r-brutas-custom', 'functional'),
                self.combine_left('separators+hax0r-brutas-custom', 'months'),
                self.combine_left('separators+hax0r-brutas-custom', 'years-current'),
                self.combine_left('separators+repeat-brutas-custom', 'functional'),
                self.combine_left('separators+repeat-brutas-custom', 'months'),
                self.combine_left('separators+repeat-brutas-custom', 'years-current'),
                self.combine_left('separators+simple-brutas-custom', 'functional'),
                self.combine_left('separators+simple-brutas-custom', 'months'),
                self.combine_left('separators+simple-brutas-custom', 'years-current'),
                self.combine_left('years-current+hax0r-brutas-custom', 'extra-all'),
                self.combine_left('years-current+hax0r-brutas-custom', 'months'),
                self.combine_left('years-current+hax0r-brutas-custom', 'separators'),
                self.combine_left('years-current+repeat-brutas-custom', 'extra-all'),
                self.combine_left('years-current+repeat-brutas-custom', 'months'),
                self.combine_left('years-current+repeat-brutas-custom', 'separators'),
                self.combine_left('years-current+separators+hax0r-brutas-custom', 'months'),
                self.combine_left('years-current+separators+repeat-brutas-custom', 'months'),
                self.combine_left('years-current+separators+simple-brutas-custom', 'months'),
                self.combine_left('years-current+simple-brutas-custom', 'extra-all'),
                self.combine_left('years-current+simple-brutas-custom', 'months'),
                self.combine_left('years-current+simple-brutas-custom', 'separators'),
                self.combine_right('extra-all+hax0r-brutas-custom', 'months'),
                self.combine_right('extra-all+hax0r-brutas-custom', 'years-current'),
                self.combine_right('extra-all+repeat-brutas-custom', 'months'),
                self.combine_right('extra-all+repeat-brutas-custom', 'years-current'),
                self.combine_right('extra-all+simple-brutas-custom', 'months'),
                self.combine_right('extra-all+simple-brutas-custom', 'years-current'),
                self.combine_right('hax0r-brutas-custom', 'extra-all'),
                self.combine_right('hax0r-brutas-custom', 'months'),
                self.combine_right('hax0r-brutas-custom', 'numbers-common'),
                self.combine_right('hax0r-brutas-custom', 'separators'),
                self.combine_right('hax0r-brutas-custom', 'years-current'),
                self.combine_right('hax0r-brutas-custom+extra-all', 'months'),
                self.combine_right('hax0r-brutas-custom+extra-all', 'years-current'),
                self.combine_right('hax0r-brutas-custom+months', 'extra-all'),
                self.combine_right('hax0r-brutas-custom+months', 'separators'),
                self.combine_right('hax0r-brutas-custom+months+separators', 'years-current'),
                self.combine_right('hax0r-brutas-custom+numbers-common', 'extra-all'),
                self.combine_right('hax0r-brutas-custom+separators', 'functional'),
                self.combine_right('hax0r-brutas-custom+separators', 'months'),
                self.combine_right('hax0r-brutas-custom+separators', 'years-current'),
                self.combine_right('hax0r-brutas-custom+separators+months', 'years-current'),
                self.combine_right('hax0r-brutas-custom+separators+years-current', 'months'),
                self.combine_right('hax0r-brutas-custom+years-current', 'extra-all'),
                self.combine_right('hax0r-brutas-custom+years-current', 'months'),
                self.combine_right('hax0r-brutas-custom+years-current', 'separators'),
                self.combine_right('hax0r-brutas-custom+years-current+separators', 'months'),
                self.combine_right('months+hax0r-brutas-custom', 'extra-all'),
                self.combine_right('months+repeat-brutas-custom', 'extra-all'),
                self.combine_right('months+separators+simple-brutas-custom', 'extra-common'),
                self.combine_right('months+simple-brutas-custom', 'extra-all'),
                self.combine_right('numbers-all+hax0r-brutas-custom', 'extra-all'),
                self.combine_right('numbers-all+repeat-brutas-custom', 'extra-all'),
                self.combine_right('numbers-all+simple-brutas-custom', 'extra-all'),
                self.combine_right('repeat-brutas-custom', 'extra-all'),
                self.combine_right('repeat-brutas-custom', 'numbers-all'),
                self.combine_right('repeat-brutas-custom+numbers-all', 'extra-all'),
                self.combine_right('simple-brutas-custom', 'extra-all'),
                self.combine_right('simple-brutas-custom', 'months'),
                self.combine_right('simple-brutas-custom', 'numbers-all'),
                self.combine_right('simple-brutas-custom', 'separators'),
                self.combine_right('simple-brutas-custom', 'years-current'),
                self.combine_right('simple-brutas-custom+extra-all', 'months'),
                self.combine_right('simple-brutas-custom+extra-all', 'years-current'),
                self.combine_right('simple-brutas-custom+months', 'extra-all'),
                self.combine_right('simple-brutas-custom+months', 'separators'),
                self.combine_right('simple-brutas-custom+months+separators', 'years-current'),
                self.combine_right('simple-brutas-custom+numbers-all', 'extra-all'),
                self.combine_right('simple-brutas-custom+separators', 'functional'),
                self.combine_right('simple-brutas-custom+separators', 'months'),
                self.combine_right('simple-brutas-custom+separators', 'years-current'),
                self.combine_right('simple-brutas-custom+separators+months', 'years-current'),
                self.combine_right('simple-brutas-custom+separators+years-current', 'months'),
                self.combine_right('simple-brutas-custom+years-current', 'extra-all'),
                self.combine_right('simple-brutas-custom+years-current', 'months'),
                self.combine_right('simple-brutas-custom+years-current', 'separators'),
                self.combine_right('simple-brutas-custom+years-current+separators', 'months'),
                self.combine_right('years-current+separators+hax0r-brutas-custom', 'extra-common'),
                self.combine_right('years-current+separators+repeat-brutas-custom', 'extra-common'),
                self.combine_right('years-current+separators+simple-brutas-custom', 'extra-common'),
                self.rule_process(f'{self.tmp_dir}/extra-all+hax0r-brutas-custom.txt', 'complex'),
                self.rule_process(f'{self.tmp_dir}/extra-all+repeat-brutas-custom.txt', 'complex'),
                self.rule_process(f'{self.tmp_dir}/extra-all+simple-brutas-custom.txt', 'complex'),
                self.rule_process(f'{self.tmp_dir}/hax0r-brutas-custom+extra-all.txt', 'complex'),
                self.rule_process(f'{self.tmp_dir}/hax0r-brutas-custom+numbers-common.txt', 'complex'),
                self.rule_process(f'{self.tmp_dir}/numbers-all+hax0r-brutas-custom.txt', 'complex'),
                self.rule_process(f'{self.tmp_dir}/numbers-all+repeat-brutas-custom.txt', 'complex'),
                self.rule_process(f'{self.tmp_dir}/numbers-all+simple-brutas-custom.txt', 'complex'),
                self.rule_process(f'{self.tmp_dir}/repeat-brutas-custom+extra-all.txt', 'complex'),
                self.rule_process(f'{self.tmp_dir}/repeat-brutas-custom+numbers-all.txt', 'complex'),
                self.rule_process(f'{self.tmp_dir}/simple-brutas-custom+numbers-all.txt', 'complex'),
                f'{self.tmp_dir}/simple-brutas-custom.txt',
                f'{self.tmp_dir}/hax0r-brutas-custom.txt',
                f'{self.tmp_dir}/repeat-brutas-custom.txt',
            )
        )


class MergeAll(Combinator):

    def process(self):

        self.concat(
            'brutas-passwords-all.txt',
            (
                'brutas-passwords-1-xxs.txt',
                'brutas-passwords-2-xs.txt',
                'brutas-passwords-3-s.txt',
                'brutas-passwords-4-m.txt',
                'brutas-passwords-5-l.txt',
                'brutas-passwords-6-xl.txt',
                'brutas-passwords-7-xxl.txt',
            )
        )
