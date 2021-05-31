#!/usr/bin/env python3
import os
import pathlib
import subprocess
import tempfile


WORDLISTS = [
    'brutas-passwords-classics.txt',
    'brutas-passwords-closekeys.txt',
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


def run_shell(cmd):
    return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout


def wordlists_process():
    for rule in RULES:
        print(f'Processing wordlists with rules "{rule}"')
        for wordlist in WORDLISTS:
            idx = wordlist.find('/')
            filename = rule + '-' + wordlist[idx + 1:].split('.txt')[0] + '.txt'
            if not pathlib.Path(f'{tmp_dir}/{filename}').is_file():
                print(f'\t - {filename}')
                subprocess.run(f'hashcat --stdout -r rules/{rule}.rule {wordlist} > {tmp_dir}/{filename}', shell=True, stdout=subprocess.PIPE)


if 'TEMP_DIR' in os.environ:
    tmp_dir = os.environ['TEMP_DIR']
else:
    tmp_dir = tempfile.mkdtemp()
cores_no = int(run_shell('sysctl -n hw.ncpu'))


print(f'Using temporary directory: {tmp_dir}')

print('Generating subdomains')

run_shell(f'cat keywords/brutas-subdomains.txt > brutas-subdomains-1-small.txt')
run_shell(f'comm -13 keywords/brutas-subdomains.txt keywords/brutas-subdomains-extra.txt >> brutas-subdomains-1-small.txt')
run_shell(f'cat brutas-subdomains-1-small.txt > brutas-subdomains-2-large.txt')
run_shell(f'hashcat --stdout -r rules/subdomains.rule keywords/brutas-subdomains.txt >> brutas-subdomains-2-large.txt')

print('Preparing keyword lists')

# NOTE: Remove duplicates
run_shell(f'sort --mergesort -T {tmp_dir} -f keywords/brutas-lang-int-common.txt > {tmp_dir}/brutas-lang-int-common.txt')
run_shell(f'sort --mergesort -T {tmp_dir} -f keywords/brutas-lang-int-less.txt > {tmp_dir}/brutas-lang-int-less.txt')
run_shell(f'comm -13 {tmp_dir}/brutas-lang-int-common.txt {tmp_dir}/brutas-lang-int-less.txt > keywords/brutas-lang-int-less.txt')
run_shell(f'rm keywords/brutas-lang-int-common.txt')
run_shell(f'cp {tmp_dir}/brutas-lang-int-common.txt keywords/brutas-lang-int-common.txt')

run_shell(f'sort --mergesort -T {tmp_dir} -f bits/extra-common.txt > {tmp_dir}/extra-sorted1')
run_shell(f'sort --mergesort -T {tmp_dir} -f bits/extra-less.txt > {tmp_dir}/extra-sorted2')
run_shell(f'comm -13 {tmp_dir}/extra-sorted1 {tmp_dir}/extra-sorted2 > bits/extra-less.txt')
run_shell(f'rm bits/extra-common.txt')
run_shell(f'mv {tmp_dir}/extra-sorted1 bits/extra-common.txt')

run_shell(f'sort --mergesort -T {tmp_dir} -f bits/numbers-common.txt > {tmp_dir}/numbers-sorted1')
run_shell(f'sort --mergesort -T {tmp_dir} -f bits/numbers-less.txt > {tmp_dir}/numbers-sorted2')
run_shell(f'comm -13 {tmp_dir}/numbers-sorted1 {tmp_dir}/numbers-sorted2 > bits/numbers-less.txt')
run_shell(f'rm bits/numbers-common.txt')
run_shell(f'mv {tmp_dir}/numbers-sorted1 bits/numbers-common.txt')

# NOTE: Combine all languages
run_shell(f'sort --mergesort -T {tmp_dir} -f keywords/brutas-lang-*.txt | uniq > {tmp_dir}/brutas-all-lang.txt')
run_shell(f'rm keywords/brutas-all-lang.txt')
run_shell(f'cp {tmp_dir}/brutas-all-lang.txt keywords/brutas-all-lang.txt')


def combine_right(wordlist, bits):
    if not pathlib.Path(f'{tmp_dir}/{wordlist}+{bits}.txt').is_file():
        print(f'Combining {wordlist} with {bits}')
        run_shell(f'combinator.bin {tmp_dir}/{wordlist}.txt bits/{bits}.txt > {tmp_dir}/{wordlist}+{bits}.txt')
    return (f'{tmp_dir}/{wordlist}+{bits}.txt',)


def combine_left(wordlist, bits):
    if not pathlib.Path(f'{tmp_dir}/{bits}+{wordlist}.txt').is_file():
        print(f'Combining {wordlist} with {bits}')
        run_shell(f'combinator.bin bits/{bits}.txt {tmp_dir}/{wordlist}.txt > {tmp_dir}/{bits}+{wordlist}.txt')
    return (f'{tmp_dir}/{bits}+{wordlist}.txt',)


def combine_both(wordlist, bits):
    if not pathlib.Path(f'{tmp_dir}/{bits}+{wordlist}.txt').is_file():
        run_shell(f'combinator.bin bits/{bits}.txt {tmp_dir}/{wordlist}.txt > {tmp_dir}/{bits}+{wordlist}.txt')
    if not pathlib.Path(f'{tmp_dir}/{bits}+{wordlist}+{bits}.txt').is_file():
        print(f'Combining {wordlist} with {bits}')
        run_shell(f'combinator.bin {tmp_dir}/{bits}+{wordlist}.txt bits/{bits}.txt > {tmp_dir}/{bits}+{wordlist}+{bits}.txt')
    return (f'{tmp_dir}/{bits}+{wordlist}+{bits}.txt',)


def combine_all(wordlist, bits):
    results = []
    results.extend(combine_right(wordlist, bits))
    results.extend(combine_left(wordlist, bits))
    results.extend(combine_both(wordlist, bits))
    return results


def merge(output, wordlists, prepend=None, compare=None):
    print(f'Merging: {output}')
    wordlists_arg = ' '.join([w for w in wordlists])
    run_shell(f'cat {wordlists_arg} | sort --mergesort -T {tmp_dir} --compress-program=lzop --parallel {cores_no} -f | uniq > {tmp_dir}/{output}')
    if prepend:
        run_shell(f'cat {prepend} > {output}')
    else:
        run_shell(f'cat /dev/null > {output}')
    if compare:
        run_shell(f'comm -13 {compare} {tmp_dir}/{output} >> {output}')
    else:
        run_shell(f'cat {tmp_dir}/{output} >> {output}')


# NOTE: Process keywords
wordlists_process()


# NOTE: Prepare some lists beforehand
combine_left('simple-brutas-usernames', 'separators')
combine_left('simple-brutas-usernames-small', 'separators')
combine_left('brutas-all-lang', 'numbers-common')
combine_left('brutas-all-lang', 'numbers-less')
combine_right('brutas-all-lang', 'separators')
combine_right('brutas-lang-int-common', 'separators')
combine_right('simple-brutas-usernames', 'numbers-less')
combine_right('simple-brutas-usernames', 'separators')
combine_right('simple-brutas-usernames-small', 'separators')


# NOTE: Change the order here...
merge(
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

merge(
    'brutas-passwords-2-xs.txt',
    (
        *combine_left('simple-brutas-usernames-small', 'extra-common'),
        *combine_left('simple-brutas-usernames-small', 'functional'),
        *combine_right('simple-brutas-usernames-small', 'extra-common'),
        *combine_right('simple-brutas-usernames-small', 'extra-less'),
        *combine_right('simple-brutas-usernames-small', 'numbers-common'),
        *combine_right('simple-brutas-usernames-small', 'years-current'),
        *combine_right('simple-brutas-usernames-small+extra-common', 'years-current'),
        *combine_right('simple-brutas-usernames-small+separators', 'functional'),
        *combine_right('simple-brutas-usernames-small+separators', 'months'),
        *combine_right('simple-brutas-usernames-small+separators', 'years-current'),
        f'{tmp_dir}/both-brutas-usernames-small.txt',
        f'{tmp_dir}/hax0r-brutas-usernames-small.txt',
        f'{tmp_dir}/repeat-brutas-usernames-small.txt',
        f'{tmp_dir}/simple-brutas-passwords-classics.txt',
        f'{tmp_dir}/simple-brutas-passwords-top.txt',
        f'{tmp_dir}/simple-brutas-usernames-small.txt',
        f'{tmp_dir}/simple-brutas-lang-int-common.txt',
    ),
    compare='brutas-passwords-1-xxs.txt'
)


merge(
    'brutas-passwords-3-s.txt',
    (
        'keywords/brutas-lang-int-common.txt',
        *combine_left('separators+simple-brutas-usernames-small', 'functional'),
        *combine_left('separators+simple-brutas-usernames-small', 'years-current'),
        *combine_right('simple-brutas-passwords-closekeys', 'months'),
        *combine_right('simple-brutas-passwords-closekeys', 'numbers-common'),
        *combine_right('simple-brutas-passwords-closekeys', 'years-current'),
        *combine_right('simple-brutas-usernames-small', 'years-all'),
        *combine_right('simple-brutas-usernames-small+extra-common', 'extra-common'),
        *combine_right('simple-brutas-usernames-small+numbers-common', 'extra-common'),
        *combine_right('simple-brutas-usernames-small+years-current', 'extra-common'),
        f'{tmp_dir}/hax0r-brutas-passwords-classics.txt',
        f'{tmp_dir}/hax0r-brutas-usernames.txt',
    ),
    compare='brutas-passwords-2-xs.txt'
)


merge(
    'brutas-passwords-4-m.txt',
    (
        'keywords/brutas-lang-int-less.txt',
        *combine_left('simple-brutas-usernames', 'extra-common'),
        *combine_left('simple-brutas-usernames', 'functional'),
        *combine_left('simple-brutas-usernames', 'numbers-common'),
        *combine_right('brutas-lang-int-common', 'extra-common'),
        *combine_right('extra-common+simple-brutas-usernames', 'months'),
        *combine_right('extra-common+simple-brutas-usernames', 'years-current'),
        *combine_right('simple-brutas-passwords-closekeys', 'numbers-less'),
        *combine_right('simple-brutas-passwords-closekeys', 'years-all'),
        *combine_right('simple-brutas-usernames', 'extra-common'),
        *combine_right('simple-brutas-usernames', 'functional'),
        *combine_right('simple-brutas-usernames', 'numbers-common'),
        *combine_right('simple-brutas-usernames', 'years-all'),
        *combine_right('simple-brutas-usernames+extra-common', 'years-current'),
        *combine_right('simple-brutas-usernames+separators', 'functional'),
        *combine_right('simple-brutas-usernames+separators', 'months'),
        *combine_right('simple-brutas-usernames+separators', 'years-current'),
        *combine_right('simple-brutas-usernames+years-all', 'extra-common'),
        f'{tmp_dir}/hax0r-brutas-passwords-top.txt',
        f'{tmp_dir}/both-brutas-usernames.txt',
        f'{tmp_dir}/complex-brutas-usernames-small.txt',
        f'{tmp_dir}/hax0r-brutas-passwords-unique.txt',
    ),
    compare='brutas-passwords-3-s.txt'
)


merge(
    'brutas-passwords-5-l.txt',
    (
        'keywords/brutas-all-lang.txt',
        *combine_both('repeat-brutas-usernames', 'extra-common'),
        *combine_left('simple-brutas-usernames', 'extra-less'),
        *combine_left('simple-brutas-usernames', 'numbers-less'),
        *combine_left('simple-brutas-usernames-small', 'extra-less'),
        *combine_left('simple-brutas-usernames-small', 'numbers-common'),
        *combine_right('brutas-lang-int-common', 'months'),
        *combine_right('brutas-lang-int-less', 'extra-common'),
        *combine_right('extra-common+simple-brutas-usernames', 'years-all'),
        *combine_right('hax0r-brutas-usernames', 'extra-common'),
        *combine_right('simple-brutas-lang-int-common', 'extra-common'),
        *combine_right('simple-brutas-passwords-closekeys', 'separators'),
        *combine_right('simple-brutas-passwords-closekeys+separators', 'numbers-common'),
        *combine_right('simple-brutas-passwords-closekeys+separators', 'numbers-less'),
        *combine_right('simple-brutas-passwords-closekeys+separators', 'years-all'),
        *combine_right('simple-brutas-usernames', 'extra-less'),
        *combine_right('simple-brutas-usernames+extra-common', 'extra-common'),
        *combine_right('simple-brutas-usernames+extra-common', 'years-all'),
        *combine_right('simple-brutas-usernames+numbers-common', 'extra-common'),
        *combine_right('simple-brutas-usernames+separators', 'years-all'),
        *combine_right('simple-brutas-usernames-small+separators+months', 'years-current'),
        *combine_right('simple-brutas-usernames-small+years-all', 'extra-common'),
        f'{tmp_dir}/complex-brutas-lang-int-common.txt',
        f'{tmp_dir}/complex-brutas-passwords-classics.txt',
        f'{tmp_dir}/complex-brutas-passwords-unique.txt',
        f'{tmp_dir}/complex-brutas-usernames.txt',
        f'{tmp_dir}/repeat-brutas-usernames.txt',
    ),
    compare='brutas-passwords-4-m.txt'
)


merge(
    'brutas-passwords-6-xl.txt',
    (
        *combine_both('repeat-brutas-usernames', 'extra-less'),
        *combine_left('simple-brutas-all-lang', 'extra-common'),
        *combine_left('simple-brutas-all-lang', 'extra-less'),
        *combine_left('simple-brutas-all-lang', 'numbers-common'),
        *combine_left('simple-brutas-all-lang', 'numbers-less'),
        *combine_left('simple-brutas-usernames+numbers-common', 'extra-common'),
        *combine_right('hax0r-brutas-usernames', 'extra-less'),
        *combine_right('numbers-common+brutas-all-lang', 'extra-common'),
        *combine_right('numbers-common+brutas-all-lang', 'extra-less'),
        *combine_right('numbers-common+simple-brutas-usernames', 'extra-common'),
        *combine_right('numbers-common+simple-brutas-usernames', 'extra-less'),
        *combine_right('numbers-less+brutas-all-lang', 'extra-less'),
        *combine_right('numbers-less+simple-brutas-usernames', 'extra-common'),
        *combine_right('numbers-less+simple-brutas-usernames', 'extra-less'),
        *combine_right('simple-brutas-all-lang', 'extra-common'),
        *combine_right('simple-brutas-all-lang', 'extra-less'),
        *combine_right('simple-brutas-all-lang', 'months'),
        *combine_right('simple-brutas-all-lang', 'numbers-common'),
        *combine_right('simple-brutas-all-lang', 'numbers-less'),
        *combine_right('simple-brutas-all-lang', 'years-all'),
        *combine_right('simple-brutas-all-lang+extra-common', 'years-all'),
        *combine_right('simple-brutas-all-lang+months', 'extra-common'),
        *combine_right('simple-brutas-all-lang+months', 'extra-less'),
        *combine_right('simple-brutas-all-lang+months', 'separators'),
        *combine_right('simple-brutas-all-lang+months+separators', 'years-all'),
        *combine_right('simple-brutas-all-lang+numbers-common', 'extra-common'),
        *combine_right('simple-brutas-all-lang+numbers-common', 'extra-less'),
        *combine_right('simple-brutas-all-lang+numbers-less', 'extra-common'),
        *combine_right('simple-brutas-all-lang+numbers-less', 'extra-less'),
        *combine_right('simple-brutas-all-lang+separators', 'functional'),
        *combine_right('simple-brutas-all-lang+separators', 'months'),
        *combine_right('simple-brutas-all-lang+separators', 'years-all'),
        *combine_right('simple-brutas-all-lang+separators+months', 'years-all'),
        *combine_right('simple-brutas-all-lang+separators+years-all', 'months'),
        *combine_right('simple-brutas-all-lang+years-all', 'extra-common'),
        *combine_right('simple-brutas-all-lang+years-all', 'separators'),
        *combine_right('simple-brutas-all-lang+years-all+separators', 'months'),
        *combine_right('simple-brutas-usernames+numbers-common', 'extra-less'),
        *combine_right('simple-brutas-usernames+numbers-less', 'extra-common'),
        *combine_right('simple-brutas-usernames+numbers-less', 'extra-less'),
        *combine_right('simple-brutas-usernames+separators', 'extra-common'),
        *combine_right('simple-brutas-usernames+separators+months', 'years-all'),
        f'{tmp_dir}/both-brutas-all-lang.txt',
        f'{tmp_dir}/both-brutas-passwords-classics.txt',
        f'{tmp_dir}/both-brutas-passwords-top.txt',
        f'{tmp_dir}/both-brutas-passwords-unique.txt',
        f'{tmp_dir}/complex-brutas-all-lang.txt',
        f'{tmp_dir}/hax0r-brutas-all-lang.txt',
        f'{tmp_dir}/repeat-brutas-all-lang.txt',
        f'{tmp_dir}/simple-brutas-all-lang.txt',
    ),
    compare='brutas-passwords-5-l.txt'
)


merge(
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

print(f'Done! You may want to clean up the temporary directory yourself: {tmp_dir}')
