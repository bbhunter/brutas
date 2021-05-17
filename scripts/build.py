#!/usr/bin/env python3
import os
import pathlib
import subprocess
import tempfile


WORDLISTS = [
    'brutas-passwords-classics.txt',
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
run_shell(f'sort --mergesort -T {tmp_dir} -f keywords/brutas-lang-int-common.txt > {tmp_dir}/int-sorted1')
run_shell(f'sort --mergesort -T {tmp_dir} -f keywords/brutas-lang-int-less.txt > {tmp_dir}/int-sorted2')
run_shell(f'comm -13 {tmp_dir}/int-sorted1 {tmp_dir}/int-sorted2 > keywords/brutas-lang-int-less.txt')
run_shell(f'rm keywords/brutas-lang-int-common.txt')
run_shell(f'mv {tmp_dir}/int-sorted1 keywords/brutas-lang-int-common.txt')

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
run_shell(f'sort --mergesort -T {tmp_dir} -f keywords/brutas-lang-*.txt | uniq > keywords/brutas-all-lang.txt')

# NOTE: Process keywords
wordlists_process()


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


def merge(output, wordlists, prepend=None):
    print(f'Merging: {output}')
    wordlists_arg = ' '.join([w for w in wordlists])
    run_shell(f'cat {wordlists_arg} | sort --mergesort -T {tmp_dir} --compress-program=lzop --parallel {cores_no} -f | uniq > {tmp_dir}/{output}')
    if prepend:
        run_shell(f'cat {prepend} > {output}')
        run_shell(f'comm -13 {prepend} {tmp_dir}/{output} >> {output}')
    else:
        run_shell(f'mv {tmp_dir}/{output} {output}')


# NOTE: Prepare some lists beforehand
combine_left('simple-brutas-usernames', 'separators')[0]
combine_left('simple-brutas-usernames-small', 'separators')[0]
combine_right('simple-brutas-usernames', 'separators')[0]
combine_right('simple-brutas-usernames-small', 'separators')[0]
combine_right('simple-brutas-usernames', 'numbers-less'),


# NOTE: Change the order here...
merge(
    'brutas-passwords-1-xxs.txt',
    (
        'brutas-passwords-classics.txt',
        'brutas-passwords-closekeys.txt',
        'brutas-usernames.txt',
        *combine_right('simple-brutas-usernames-small', 'extra-common'),
        *combine_right('simple-brutas-usernames-small+separators', 'years-current'),
        f'{tmp_dir}/repeat-brutas-usernames-small.txt',
    )
)

merge(
    'brutas-passwords-2-xs.txt',
    (
        'brutas-passwords-numbers.txt',
        'brutas-passwords-top.txt',
        'brutas-passwords-unique.txt',
        'keywords/brutas-lang-int-common.txt',
        *combine_left('simple-brutas-usernames-small', 'extra-common'),
        *combine_left('simple-brutas-usernames-small', 'numbers-common'),
        *combine_right('simple-brutas-usernames-small', 'functional'),
        *combine_right('simple-brutas-usernames-small', 'numbers-common'),
        *combine_right('simple-brutas-usernames-small+separators', 'functional'),
        f'{tmp_dir}/both-brutas-usernames-small.txt',
        f'{tmp_dir}/hax0r-brutas-usernames-small.txt',
        f'{tmp_dir}/simple-brutas-passwords-classics.txt',
    ),
    prepend='brutas-passwords-1-xxs.txt'
)


merge(
    'brutas-passwords-3-s.txt',
    (
        'keywords/brutas-lang-int-less.txt',
        *combine_left('simple-brutas-usernames', 'extra-common'),
        *combine_left('simple-brutas-usernames', 'numbers-common'),
        *combine_left('simple-brutas-usernames-small', 'extra-less'),
        *combine_right('hax0r-brutas-usernames-small', 'extra-common'),
        *combine_right('simple-brutas-usernames', 'functional'),
        *combine_right('simple-brutas-usernames', 'numbers-common'),
        *combine_right('simple-brutas-usernames+separators', 'functional'),
        *combine_right('simple-brutas-usernames-small+numbers-common', 'extra-common'),
        *combine_right('simple-brutas-usernames-small+separators', 'months'),
        f'{tmp_dir}/both-brutas-usernames.txt',
        f'{tmp_dir}/hax0r-brutas-passwords-classics.txt',
        f'{tmp_dir}/hax0r-brutas-usernames.txt',
    ),
    prepend='brutas-passwords-2-xs.txt'
)


merge(
    'brutas-passwords-4-m.txt',
    (
        *combine_left('separators+simple-brutas-usernames-small', 'functional'),
        *combine_left('separators+simple-brutas-usernames-small', 'years-current'),
        *combine_left('simple-brutas-usernames', 'extra-less'),
        *combine_left('simple-brutas-usernames', 'functional'),
        *combine_left('simple-brutas-usernames', 'numbers-less'),
        *combine_right('hax0r-brutas-usernames', 'extra-common'),
        *combine_right('hax0r-brutas-usernames', 'extra-less'),
        *combine_right('numbers-common+simple-brutas-usernames', 'extra-common'),
        *combine_right('simple-brutas-usernames', 'extra-common'),
        *combine_right('simple-brutas-usernames+numbers-common', 'extra-common'),
        *combine_right('simple-brutas-usernames+separators', 'months'),
        *combine_right('simple-brutas-usernames+separators', 'years-all'),
        *combine_right('simple-brutas-usernames-small+separators+months', 'years-current'),
        f'{tmp_dir}/both-brutas-passwords-classics.txt',
        f'{tmp_dir}/both-brutas-passwords-unique.txt',
        f'{tmp_dir}/complex-brutas-usernames-small.txt',
        f'{tmp_dir}/hax0r-brutas-passwords-unique.txt',
    ),
    prepend='brutas-passwords-3-s.txt'
)


merge(
    'brutas-passwords-5-l.txt',
    (
        'keywords/brutas-all-lang.txt',
        *combine_both('repeat-brutas-usernames', 'extra-common'),
        *combine_right('numbers-less+simple-brutas-usernames', 'extra-common'),
        *combine_right('simple-brutas-usernames+numbers-less', 'extra-common'),
        f'{tmp_dir}/complex-brutas-lang-int-common.txt',
        f'{tmp_dir}/complex-brutas-passwords-classics.txt',
        f'{tmp_dir}/complex-brutas-passwords-unique.txt',
        f'{tmp_dir}/complex-brutas-usernames.txt',
        f'{tmp_dir}/repeat-brutas-lang-int-common.txt',
        f'{tmp_dir}/repeat-brutas-usernames.txt',
    ),
    prepend='brutas-passwords-4-m.txt'
)


merge(
    'brutas-passwords-6-xl.txt',
    (
        *combine_both('repeat-brutas-usernames', 'extra-less'),
        *combine_right('simple-brutas-usernames+separators+months', 'years-all'),
        f'{tmp_dir}/both-brutas-all-lang.txt',
        f'{tmp_dir}/complex-brutas-all-lang.txt',
        f'{tmp_dir}/hax0r-brutas-all-lang.txt',
        f'{tmp_dir}/repeat-brutas-all-lang.txt',
        f'{tmp_dir}/simple-brutas-all-lang.txt',
    ),
    prepend='brutas-passwords-5-l.txt'
)

print('Cleaning up...')
run_shell('rm -rf {tmp_dir}')
print('Done!')
