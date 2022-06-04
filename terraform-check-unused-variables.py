#!/usr/bin/env python3

"""
usage: terraform-check-unused-variables.py [-h] [--dir DIR] [--var-file VAR_FILE] [-r] [--check-only] [--verbose]

Scan terraform module(s) for unused variables and remove them.

optional arguments:
  -h, --help           show this help message and exit
  --dir DIR            root dir to search for tf files in (default: ".")
  --var-file VAR_FILE  file name for tf variables (default: "variables.tf")
  -r                   flag to run check unused variables recursively on all directories from root dir
  --check-only         flag to show only check for unused vars, not remove them
  --verbose, -v        flag to show verbose output

"""

import os
import re
import sys
import argparse
import logging
from glob import glob


def check_for_unused_vars(dir):
    variables_file, all_tf_files = find_tf_files(dir)
    if variables_file is None:
        return True  # no files to check in this directory
    variables = parse_variables_tf(variables_file)
    var_references = find_used_variables(all_tf_files)
    unused_vars = list(variables - var_references)

    if len(unused_vars) > 0:
        logging.info('unused vars detected:')
        logging.info("%s\n" % unused_vars)
        if not args.check_only:
            remove_unused_vars(unused_vars, variables_file)
        return False
    else:
        logging.info('no unused variables found')
        return True


def find_tf_files(_dir):
    try:
        target_dir = os.getcwd() + "/" + _dir.replace(".", '')
        all_tf_files = glob(os.path.join(_dir, '*.tf'))
        logging.debug(f'tf files: {all_tf_files}')

        if len(all_tf_files) < 1:
            logging.info(f'Did not find any tf files in {target_dir}\nEnsure running '
                         'from root terraform module or correct custom dir.\n\nTo set custom dir use --dir PATH')
            return None, None

        variables_file = glob(os.path.join(_dir, '*' + args.var_file))[0]
        logging.debug(f'variable file: {variables_file}')

        return variables_file, all_tf_files
    except IndexError:
        raise Exception(f'Failed to find required variable file "{args.var_file}" in {target_dir}, but did find other '
                        'tf files.\nEnsure running from root terraform module or correct custom dir and the variable '
                        'tf file exists.\n\nTo set custom dir use --dir PATH\nTo set custom var_file --var-file '
                        'FILENAME\n')


def remove_unused_vars(unused_vars, var_file):
    removing_variable = False
    new_file = ''
    with open(var_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if removing_variable:
                if line.startswith('}'):
                    removing_variable = False
                new_file += ''
            elif line.startswith('variable'):
                variable = line[line.find("\"") + len("\""):line.rfind("\"")]
                if variable in unused_vars:
                    new_file += ''
                    removing_variable = True
                    logging.info('removing...' + variable)
                else:
                    new_file += line
            elif not removing_variable:
                new_file += line

    with open(var_file, 'w') as file:
        file.write(new_file)


def find_used_variables(tf_files):
    referenced_vars = []
    logging.debug(f'searching for unused vars')
    for tf_file in tf_files:
        if 'variables.tf' in tf_file:
            logging.debug(f'skipping {args.var_file}')
            continue
        logging.debug(f'searching for var references in {tf_file}...')
        with open(tf_file, 'r') as file:
            lines = file.read()
            referenced_vars += re.findall(r'var\.([\w_]+)', lines)
    logging.debug(f'all referenced vars: {referenced_vars}')
    return set(referenced_vars)


def parse_variables_tf(var_file):
    declared_vars = set()
    logging.debug(f'scanning {args.var_file} for all defined vars')
    with open(var_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('variable'):
                declared_vars.add(line[line.find("\"") + len("\""):line.rfind("\"")])
    logging.debug(f'all declared vars: {declared_vars}')
    return declared_vars


def parse_args():
    parser = argparse.ArgumentParser(description='Scan terraform module(s) for unused variables and remove them.')
    parser.add_argument('--dir',
                        dest='dir',
                        default='.',
                        help='root dir to search for tf files in (default: ".")')
    parser.add_argument('--var-file',
                        dest='var_file',
                        default='variables.tf',
                        help='file name for where tf variables are defined (default: "variables.tf")')
    parser.add_argument('-r',
                        dest='recursive',
                        default=False,
                        action='store_true',
                        help='flag to run check unused variables recursively on all directories from root dir')
    parser.add_argument('--check-only',
                        dest='check_only',
                        default=False,
                        action='store_true',
                        help='flag to only check for unused vars, not remove them')
    parser.add_argument('--verbose', '-v',
                        dest='debug',
                        default=False,
                        action='store_true',
                        help='flag to show verbose (debug) output')

    return parser.parse_args()


def init_logger(debug):
    log_level = logging.INFO
    if debug:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level, format='%(levelname) -4s: %(message)s')
    logging.debug('executing in debug mode')


if __name__ == '__main__':
    args = parse_args()
    init_logger(args.debug)
    logging.debug(f'args: {vars(args)}\n')
    passed = []
    dirs_to_check = [args.dir]
    if args.recursive:
        dirs_to_check = [x[0] for x in os.walk(args.dir) if not x[0].startswith('./.') and '.terraform' not in x]  # make this better
    for _dir in dirs_to_check:
        logging.debug(f'Checking for unused vars in {_dir}')
        passed.append(check_for_unused_vars(_dir))
        logging.debug(f'Completed check in {_dir}\n')
    if all(passed):
        sys.exit(0)
    else:
        sys.exit(1)
