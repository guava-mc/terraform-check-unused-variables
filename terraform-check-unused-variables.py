#!/usr/bin/env python3

"""
Scan terraform module(s) for unused variables and remove them.

optional arguments:
  -h, --help           show this help message and exit
  --dir DIR            root dir to search for tf files in (default: ".")
  -r, --recursive      flag to run check unused variables recursively on all directories from root dir
  --check-only         flag to only check for unused vars, not remove them
  --verbose, -v        flag to show verbose (debug) output
  --quiet, -q          flag to hide all non-error output.
"""

import os
import re
import sys
import argparse
import logging
from glob import glob


def check_for_unused_vars(dir):
    try:
        tf_files = find_tf_files(dir)
        logging.info(f'Checking {dir} for unused variables')
        variables = parse_variables_tf(tf_files)
        var_references = find_used_variables(tf_files)
        unused_vars = list(variables - var_references)

        if len(unused_vars) > 0:
            logging.info('unused vars detected:')
            logging.info("%s\n" % unused_vars)
            if not args.check_only:
                remove_unused_vars(unused_vars, tf_files)
            return False
        else:
            logging.info('no unused variables found')
            return True
    except IndexError as e:
        logging.error(f'{e}')
        return False


def find_tf_files(_dir):

    target_dir = os.getcwd() + "/" + _dir.replace(".", '')
    all_tf_files = glob(os.path.join(_dir, '*.tf'))
    logging.debug(f'tf files: {all_tf_files}')

    if len(all_tf_files) < 1:
        logging.info(f'Did not find any tf files in {target_dir}\nEnsure running '
                     'from root terraform module or correct custom dir.\n\nTo set custom dir use --dir PATH')
        return None, None

    return all_tf_files


def remove_unused_vars(unused_vars, tf_files):
    for file in tf_files:
        removing_variable = False
        with open(file, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if removing_variable:
                    if line.startswith('}'):
                        removing_variable = False
                        if remove_trailing_new_line(i, lines):
                            lines[i + 1] = ''
                    lines[i] = ''
                elif line.startswith('variable'):
                    variable = strip_var_name(line)
                    if variable in unused_vars:
                        if var_is_ignored(i, lines):
                            logging.info('ignore flag detected, skipping...' + variable)
                        else:
                            lines[i] = ''
                            removing_variable = True
                            logging.info('removing...' + variable)
                            lines = remove_preceding_comments(i, lines)

            with open(file, 'w') as wf:
                wf.write(''.join(lines))


def remove_preceding_comments(i, lines):
    j = i - 1
    while j >= 0:
        if not lines[j].startswith('#'):
            break
        lines[j] = ''
        j -= 1
    return lines


def remove_trailing_new_line(i, lines):
    return i + 1 < len(lines) and lines[i + 1].strip() == ''


def var_is_ignored(i, lines):
    ignore_comment = '# ' + args.ignore_txt
    return ignore_comment in lines[i] or (i - 1 >= 0 and ignore_comment in lines[i - 1])


def find_used_variables(tf_files):
    referenced_vars = []
    logging.debug(f'searching for unused vars')
    for tf_file in tf_files:
        logging.debug(f'searching for var references in {tf_file}...')
        with open(tf_file, 'r') as file:
            lines = file.read()
            # remove commented lines
            lines = re.sub(r'(\s*#).*', '', lines)
            has_var = set(re.findall(r'var\.([\w]+)', lines))
            invalid_var = set(re.findall(r'[^!{([\s]var\.([\w]+)', lines))
            referenced_vars += list(has_var - invalid_var)
    logging.debug(f'all referenced vars: {referenced_vars}')
    return set(referenced_vars)


def parse_variables_tf(tf_files):
    declared_vars = set()
    for file in tf_files:
        logging.debug(f'scanning {file} for all defined vars')
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('variable'):
                    declared_vars.add(strip_var_name(line))
        logging.debug(f'all declared vars: {declared_vars}')
    return declared_vars


def strip_var_name(line):
    return line[line.find("\"") + len("\""):line.rfind("\"")]


def parse_args():
    parser = argparse.ArgumentParser(description='Scan terraform module(s) for unused variables and remove them.')
    verbosity_group = parser.add_mutually_exclusive_group()
    parser.add_argument('--dir',
                        dest='dir',
                        default='.',
                        help='root dir to search for tf files in (default: ".")')
    parser.add_argument('--check-only',
                        dest='check_only',
                        default=False,
                        action='store_true',
                        help='flag to only check for unused vars, not remove them')
    parser.add_argument('-r', '--recursive',
                        dest='recursive',
                        default=False,
                        action='store_true',
                        help='flag to run check unused variables recursively on all directories from root dir')
    parser.add_argument('--ignore',
                        dest='ignore_txt',
                        default='ignore',
                        help='text in variable declaration comment used to tell the hook to ignore a specific unused variable (Default: "ignore")')
    verbosity_group.add_argument('-v', '--verbose',
                                 dest='debug',
                                 default=False,
                                 action='store_true',
                                 help='flag to show verbose (debug) output')
    verbosity_group.add_argument('-q', '--quiet',
                                 dest='quiet',
                                 default=False,
                                 action='store_true',
                                 help='flag to hide all non-error output.')

    return parser.parse_args()


def init_logger(debug, quiet):
    log_level = logging.INFO
    if quiet:
        log_level = logging.ERROR
    elif debug:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level, format='[%(levelname) -4s] %(message)s')
    logging.debug('executing in debug mode')


if __name__ == '__main__':
    args = parse_args()
    init_logger(args.debug, args.quiet)
    logging.debug(f'args: {vars(args)}\n')
    passed = []
    dirs_to_check = [args.dir]
    if args.recursive:
        dirs_to_check = [x[0] for x in os.walk(args.dir) if
                         len(x[0].split('/.')) < 2 and len(x[0].split('\\.')) < 2]
    for _dir in dirs_to_check:
        logging.debug(f'Checking for unused vars in {_dir}')
        passed.append(check_for_unused_vars(_dir))
        logging.debug(f'Completed check in {_dir}\n')

    if all(passed):
        sys.exit(0)
    else:
        sys.exit(1)
