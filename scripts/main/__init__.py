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

    def __init__(self, rules, wordlists, combinator_path, rli2_path, tmp_dir, top_dir):
        self.rules = rules
        self.wordlists = wordlists
        self.tmp_dir = tmp_dir
        self.top_dir = top_dir
        self.compress_program = '--compress-program=lzop' if self.run_shell('which lzop') else ''
        if pathlib.Path.exists(pathlib.Path(combinator_path)):
            self.combinator_path = combinator_path
        else:
            logger.error(f'Hashcat `combinator` not found at {combinator_path}')
            sys.exit(1)
        if pathlib.Path.exists(pathlib.Path(rli2_path)):
            self.rli2_path = rli2_path
        else:
            logger.error(f'Hashcat `rli2` not found at {rli2_path}')
            sys.exit(1)
        self.cores_no = int(self.run_shell('nproc --all'))

    def run_shell(self, cmd):
        return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, cwd=self.top_dir).stdout

    def wordlists_process(self):
        for rule in self.rules:
            logger.info(f'Processing wordlists with rules "{rule}"')
            for wordlist in self.wordlists:
                idx = wordlist.find('/')
                filename = rule + '-' + wordlist[idx + 1:].split('.txt')[0] + '.txt'
                if not pathlib.Path(f'{self.tmp_dir}/{filename}').is_file():
                    logger.info(f'\t - {filename}')
                    subprocess.run(f'hashcat --stdout -r rules/{rule}.rule {wordlist} > {self.tmp_dir}/{filename}', shell=True, stdout=subprocess.PIPE)

    def combine_right(self, wordlist, bits):
        if not pathlib.Path(f'{self.tmp_dir}/{wordlist}+{bits}.txt').is_file():
            logger.info(f'Combining {wordlist} with {bits}')
            self.run_shell(f'{self.combinator_path} {self.tmp_dir}/{wordlist}.txt bits/{bits}.txt > {self.tmp_dir}/{wordlist}+{bits}.txt')
        return (f'{self.tmp_dir}/{wordlist}+{bits}.txt',)

    def combine_left(self, wordlist, bits):
        if not pathlib.Path(f'{self.tmp_dir}/{bits}+{wordlist}.txt').is_file():
            logger.info(f'Combining {wordlist} with {bits}')
            self.run_shell(f'{self.combinator_path} bits/{bits}.txt {self.tmp_dir}/{wordlist}.txt > {self.tmp_dir}/{bits}+{wordlist}.txt')
        return (f'{self.tmp_dir}/{bits}+{wordlist}.txt',)

    def combine_both(self, wordlist, bits):
        if not pathlib.Path(f'{self.tmp_dir}/{bits}+{wordlist}.txt').is_file():
            self.run_shell(f'{self.combinator_path} bits/{bits}.txt {self.tmp_dir}/{wordlist}.txt > {self.tmp_dir}/{bits}+{wordlist}.txt')
        if not pathlib.Path(f'{self.tmp_dir}/{bits}+{wordlist}+{bits}.txt').is_file():
            logger.info(f'Combining {wordlist} with {bits}')
            self.run_shell(f'{self.combinator_path} {self.tmp_dir}/{bits}+{wordlist}.txt bits/{bits}.txt > {self.tmp_dir}/{bits}+{wordlist}+{bits}.txt')
        return (f'{self.tmp_dir}/{bits}+{wordlist}+{bits}.txt',)

    def combine_all(self, wordlist, bits):
        results = []
        results.extend(self.combine_right(wordlist, bits))
        results.extend(self.combine_left(wordlist, bits))
        results.extend(self.combine_both(wordlist, bits))
        return results

    def merge(self, output, wordlists, prepend=None, compare=None):
        logger.info(f'Merging: {output}')
        wordlists_arg = ' '.join([w for w in wordlists])
        self.run_shell(f'sort -u -T {self.tmp_dir} {self.compress_program} --parallel {self.cores_no} {wordlists_arg} -o {self.tmp_dir}/{output}')
        if prepend:
            self.run_shell(f'cp {prepend} {output}')
        else:
            self.run_shell(f'rm {output}')
        if compare:
            self.run_shell(f'{self.rli2_path} {self.tmp_dir}/{output} {compare} >> {output}')
        else:
            self.run_shell(f'cat {self.tmp_dir}/{output} >> {output}')

    def run(self):
        logger.info(f'Processing with class: {self.__class__.__name__}')
        logger.info(f'Using temporary directory: {self.tmp_dir}')
        self.process()
        logger.info(f'Done! You may want to clean up the temporary directory yourself: {self.tmp_dir}')

    def process(self):
        raise NotImplementedError()


class Basic(Combinator):

    def process(self):
        logger.info('Generating subdomains')
        self.run_shell(f'sort keywords/brutas-subdomains.txt -o {self.tmp_dir}/brutas-subdomains.txt')
        self.run_shell(f'sort keywords/brutas-subdomains-extra.txt -o {self.tmp_dir}/brutas-subdomains-extra.txt')
        self.run_shell(f'cp {self.tmp_dir}/brutas-subdomains.txt brutas-subdomains-1-small.txt')
        self.run_shell(f'comm -13 {self.tmp_dir}/brutas-subdomains.txt {self.tmp_dir}/brutas-subdomains-extra.txt >> brutas-subdomains-1-small.txt')
        self.run_shell(f'cp brutas-subdomains-1-small.txt brutas-subdomains-2-large.txt')
        self.run_shell(f'hashcat --stdout -r rules/subdomains.rule {self.tmp_dir}/brutas-subdomains.txt >> brutas-subdomains-2-large.txt')

        logger.info('Preparing keyword lists')
        self.run_shell(f'sort keywords/brutas-lang-int-common.txt -o {self.tmp_dir}/brutas-lang-int-common.txt')
        self.run_shell(f'sort keywords/brutas-lang-int-less.txt -o {self.tmp_dir}/brutas-lang-int-less.txt')
        self.run_shell(f'comm -13 {self.tmp_dir}/brutas-lang-int-common.txt {self.tmp_dir}/brutas-lang-int-less.txt > keywords/brutas-lang-int-less.txt')
        self.run_shell(f'rm keywords/brutas-lang-int-common.txt')
        self.run_shell(f'cp {self.tmp_dir}/brutas-lang-int-common.txt keywords/brutas-lang-int-common.txt')

        self.run_shell(f'sort bits/extra-common.txt -o {self.tmp_dir}/extra-sorted1')
        self.run_shell(f'sort bits/extra-less.txt -o {self.tmp_dir}/extra-sorted2')
        self.run_shell(f'comm -13 {self.tmp_dir}/extra-sorted1 {self.tmp_dir}/extra-sorted2 > bits/extra-less.txt')
        self.run_shell(f'rm bits/extra-common.txt')
        self.run_shell(f'mv {self.tmp_dir}/extra-sorted1 bits/extra-common.txt')

        self.run_shell(f'sort bits/numbers-common.txt -o {self.tmp_dir}/numbers-sorted1')
        self.run_shell(f'sort bits/numbers-less.txt -o {self.tmp_dir}/numbers-sorted2')
        self.run_shell(f'comm -13 {self.tmp_dir}/numbers-sorted1 {self.tmp_dir}/numbers-sorted2 > bits/numbers-less.txt')
        self.run_shell(f'rm bits/numbers-common.txt')
        self.run_shell(f'mv {self.tmp_dir}/numbers-sorted1 bits/numbers-common.txt')

        # NOTE: Combine all languages
        self.run_shell(f'sort -u keywords/brutas-lang-*.txt -o {self.tmp_dir}/brutas-all-lang.txt')
        self.run_shell(f'rm keywords/brutas-all-lang.txt')
        self.run_shell(f'cp {self.tmp_dir}/brutas-all-lang.txt keywords/brutas-all-lang.txt')

        # NOTE: Process keywords
        self.wordlists_process()

        # NOTE: Prepare some lists beforehand
        self.combine_left('simple-brutas-usernames', 'separators')
        self.combine_left('simple-brutas-usernames-small', 'separators')
        self.combine_left('brutas-all-lang', 'numbers-common')
        self.combine_left('brutas-all-lang', 'numbers-less')
        self.combine_right('brutas-all-lang', 'separators')
        self.combine_right('brutas-lang-int-common', 'separators')
        self.combine_right('simple-brutas-usernames', 'numbers-less')
        self.combine_right('simple-brutas-usernames', 'separators')
        self.combine_right('simple-brutas-usernames-small', 'separators')

        # NOTE: Change the order here...
        self.merge(
            'brutas-passwords-1-xxs.txt',
            (
                'brutas-passwords-classics.txt',
                'brutas-passwords-closekeys.txt',
                'brutas-passwords-numbers.txt',
                'brutas-passwords-top.txt',
                'brutas-passwords-unique.txt',
                'brutas-usernames.txt',
            )
        )

        self.merge(
            'brutas-passwords-2-xs.txt',
            (
                *self.combine_left('simple-brutas-usernames-small', 'extra-common'),
                *self.combine_left('simple-brutas-usernames-small', 'functional'),
                *self.combine_right('simple-brutas-usernames-small', 'extra-common'),
                *self.combine_right('simple-brutas-usernames-small', 'extra-less'),
                *self.combine_right('simple-brutas-usernames-small', 'numbers-common'),
                *self.combine_right('simple-brutas-usernames-small', 'years-current'),
                *self.combine_right('simple-brutas-usernames-small+extra-common', 'years-current'),
                *self.combine_right('simple-brutas-usernames-small+separators', 'functional'),
                *self.combine_right('simple-brutas-usernames-small+separators', 'months'),
                *self.combine_right('simple-brutas-usernames-small+separators', 'years-current'),
                f'{self.tmp_dir}/both-brutas-usernames-small.txt',
                f'{self.tmp_dir}/hax0r-brutas-usernames-small.txt',
                f'{self.tmp_dir}/repeat-brutas-usernames-small.txt',
                f'{self.tmp_dir}/simple-brutas-passwords-classics.txt',
                f'{self.tmp_dir}/simple-brutas-passwords-top.txt',
                f'{self.tmp_dir}/simple-brutas-usernames-small.txt',
                f'{self.tmp_dir}/simple-brutas-lang-int-common.txt',
            ),
            compare='brutas-passwords-1-xxs.txt'
        )

        self.merge(
            'brutas-passwords-3-s.txt',
            (
                *self.combine_left('separators+simple-brutas-usernames-small', 'functional'),
                *self.combine_left('separators+simple-brutas-usernames-small', 'years-current'),
                *self.combine_right('simple-brutas-passwords-closekeys', 'months'),
                *self.combine_right('simple-brutas-passwords-closekeys', 'numbers-common'),
                *self.combine_right('simple-brutas-passwords-closekeys', 'years-current'),
                *self.combine_right('simple-brutas-usernames-small', 'years-all'),
                *self.combine_right('simple-brutas-usernames-small+extra-common', 'extra-common'),
                *self.combine_right('simple-brutas-usernames-small+numbers-common', 'extra-common'),
                *self.combine_right('simple-brutas-usernames-small+years-current', 'extra-common'),
                f'{self.tmp_dir}/hax0r-brutas-passwords-classics.txt',
                f'{self.tmp_dir}/hax0r-brutas-usernames.txt',
            ),
            compare='brutas-passwords-2-xs.txt'
        )


class Extended(Basic):

    def process(self):
        super().process()

        self.merge(
            'brutas-passwords-4-m.txt',
            (
                *self.combine_left('simple-brutas-usernames', 'extra-common'),
                *self.combine_left('simple-brutas-usernames', 'functional'),
                *self.combine_left('simple-brutas-usernames', 'numbers-common'),
                *self.combine_right('brutas-lang-int-common', 'extra-common'),
                *self.combine_right('extra-common+simple-brutas-usernames', 'months'),
                *self.combine_right('extra-common+simple-brutas-usernames', 'years-current'),
                *self.combine_right('simple-brutas-passwords-closekeys', 'numbers-less'),
                *self.combine_right('simple-brutas-passwords-closekeys', 'years-all'),
                *self.combine_right('simple-brutas-usernames', 'extra-common'),
                *self.combine_right('simple-brutas-usernames', 'functional'),
                *self.combine_right('simple-brutas-usernames', 'numbers-common'),
                *self.combine_right('simple-brutas-usernames', 'years-all'),
                *self.combine_right('simple-brutas-usernames+extra-common', 'years-current'),
                *self.combine_right('simple-brutas-usernames+separators', 'functional'),
                *self.combine_right('simple-brutas-usernames+separators', 'months'),
                *self.combine_right('simple-brutas-usernames+separators', 'years-current'),
                *self.combine_right('simple-brutas-usernames+years-all', 'extra-common'),
                f'{self.tmp_dir}/both-brutas-usernames.txt',
                f'{self.tmp_dir}/complex-brutas-usernames-small.txt',
                f'{self.tmp_dir}/hax0r-brutas-passwords-top.txt',
                f'{self.tmp_dir}/hax0r-brutas-passwords-unique.txt',
                f'{self.tmp_dir}/simple-brutas-lang-int-less.txt',
            ),
            compare='brutas-passwords-3-s.txt'
        )

        self.merge(
            'brutas-passwords-5-l.txt',
            (
                *self.combine_both('repeat-brutas-usernames', 'extra-common'),
                *self.combine_left('simple-brutas-usernames', 'extra-less'),
                *self.combine_left('simple-brutas-usernames', 'numbers-less'),
                *self.combine_left('simple-brutas-usernames-small', 'extra-less'),
                *self.combine_left('simple-brutas-usernames-small', 'numbers-common'),
                *self.combine_right('brutas-lang-int-common', 'months'),
                *self.combine_right('brutas-lang-int-less', 'extra-common'),
                *self.combine_right('extra-common+simple-brutas-usernames', 'years-all'),
                *self.combine_right('hax0r-brutas-usernames', 'extra-common'),
                *self.combine_right('simple-brutas-lang-int-common', 'extra-common'),
                *self.combine_right('simple-brutas-passwords-closekeys', 'separators'),
                *self.combine_right('simple-brutas-passwords-closekeys+separators', 'numbers-common'),
                *self.combine_right('simple-brutas-passwords-closekeys+separators', 'numbers-less'),
                *self.combine_right('simple-brutas-passwords-closekeys+separators', 'years-all'),
                *self.combine_right('simple-brutas-usernames', 'extra-less'),
                *self.combine_right('simple-brutas-usernames+extra-common', 'extra-common'),
                *self.combine_right('simple-brutas-usernames+extra-common', 'years-all'),
                *self.combine_right('simple-brutas-usernames+numbers-common', 'extra-common'),
                *self.combine_right('simple-brutas-usernames+separators', 'years-all'),
                *self.combine_right('simple-brutas-usernames-small+separators+months', 'years-current'),
                *self.combine_right('simple-brutas-usernames-small+years-all', 'extra-common'),
                f'{self.tmp_dir}/complex-brutas-lang-int-common.txt',
                f'{self.tmp_dir}/complex-brutas-passwords-classics.txt',
                f'{self.tmp_dir}/complex-brutas-passwords-unique.txt',
                f'{self.tmp_dir}/complex-brutas-usernames.txt',
                f'{self.tmp_dir}/repeat-brutas-usernames.txt',
            ),
            compare='brutas-passwords-4-m.txt'
        )

        self.merge(
            'brutas-passwords-6-xl.txt',
            (
                *self.combine_both('repeat-brutas-usernames', 'extra-less'),
                *self.combine_left('simple-brutas-all-lang', 'extra-common'),
                *self.combine_left('simple-brutas-all-lang', 'extra-less'),
                *self.combine_left('simple-brutas-all-lang', 'numbers-common'),
                *self.combine_left('simple-brutas-all-lang', 'numbers-less'),
                *self.combine_left('simple-brutas-usernames+numbers-common', 'extra-common'),
                *self.combine_right('hax0r-brutas-usernames', 'extra-less'),
                *self.combine_right('numbers-common+brutas-all-lang', 'extra-common'),
                *self.combine_right('numbers-common+brutas-all-lang', 'extra-less'),
                *self.combine_right('numbers-common+simple-brutas-usernames', 'extra-common'),
                *self.combine_right('numbers-common+simple-brutas-usernames', 'extra-less'),
                *self.combine_right('numbers-less+brutas-all-lang', 'extra-less'),
                *self.combine_right('numbers-less+simple-brutas-usernames', 'extra-common'),
                *self.combine_right('numbers-less+simple-brutas-usernames', 'extra-less'),
                *self.combine_right('simple-brutas-all-lang', 'extra-common'),
                *self.combine_right('simple-brutas-all-lang', 'extra-less'),
                *self.combine_right('simple-brutas-all-lang', 'months'),
                *self.combine_right('simple-brutas-all-lang', 'numbers-common'),
                *self.combine_right('simple-brutas-all-lang', 'numbers-less'),
                *self.combine_right('simple-brutas-all-lang', 'separators'),
                *self.combine_right('simple-brutas-all-lang', 'years-all'),
                *self.combine_right('simple-brutas-all-lang+extra-common', 'years-all'),
                *self.combine_right('simple-brutas-all-lang+months', 'extra-common'),
                *self.combine_right('simple-brutas-all-lang+months', 'extra-less'),
                *self.combine_right('simple-brutas-all-lang+months', 'separators'),
                *self.combine_right('simple-brutas-all-lang+months+separators', 'years-all'),
                *self.combine_right('simple-brutas-all-lang+numbers-common', 'extra-common'),
                *self.combine_right('simple-brutas-all-lang+numbers-common', 'extra-less'),
                *self.combine_right('simple-brutas-all-lang+numbers-less', 'extra-common'),
                *self.combine_right('simple-brutas-all-lang+numbers-less', 'extra-less'),
                *self.combine_right('simple-brutas-all-lang+separators', 'functional'),
                *self.combine_right('simple-brutas-all-lang+separators', 'months'),
                *self.combine_right('simple-brutas-all-lang+separators', 'years-all'),
                *self.combine_right('simple-brutas-all-lang+separators+months', 'years-all'),
                *self.combine_right('simple-brutas-all-lang+separators+years-all', 'months'),
                *self.combine_right('simple-brutas-all-lang+years-all', 'extra-common'),
                *self.combine_right('simple-brutas-all-lang+years-all', 'separators'),
                *self.combine_right('simple-brutas-all-lang+years-all+separators', 'months'),
                *self.combine_right('simple-brutas-usernames+numbers-common', 'extra-less'),
                *self.combine_right('simple-brutas-usernames+numbers-less', 'extra-common'),
                *self.combine_right('simple-brutas-usernames+numbers-less', 'extra-less'),
                *self.combine_right('simple-brutas-usernames+separators', 'extra-common'),
                *self.combine_right('simple-brutas-usernames+separators+months', 'years-all'),
                f'{self.tmp_dir}/both-brutas-all-lang.txt',
                f'{self.tmp_dir}/both-brutas-passwords-classics.txt',
                f'{self.tmp_dir}/both-brutas-passwords-top.txt',
                f'{self.tmp_dir}/both-brutas-passwords-unique.txt',
                f'{self.tmp_dir}/complex-brutas-all-lang.txt',
                f'{self.tmp_dir}/hax0r-brutas-all-lang.txt',
                f'{self.tmp_dir}/repeat-brutas-all-lang.txt',
                f'{self.tmp_dir}/simple-brutas-all-lang.txt',
            ),
            compare='brutas-passwords-5-l.txt'
        )


class MergeAll(Combinator):

    def process(self):
        self.merge(
            'brutas-passwords-7-all.txt',
            (
                'brutas-passwords-1-xxs.txt',
                'brutas-passwords-2-xs.txt',
                'brutas-passwords-3-s.txt',
                'brutas-passwords-4-m.txt',
                'brutas-passwords-5-l.txt',
                'brutas-passwords-6-xl.txt',
            )
        )
