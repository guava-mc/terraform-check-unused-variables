#!/usr/bin/env python3

"""
usage: terraform-check-unused-variables.py [-h] [--dir DIR] [--var-file VAR_FILE] [--verbose]

Scan root terraform module for unused variables and remove them.

optional arguments:
  -h, --help           show this help message and exit
  --dir DIR            path to search for tf files (default: ".")
  --var-file VAR_FILE  path to search for tf files (default: "variables.tf")
  --verbose, -v        flag to show verbose output
"""

import os
import re
import sys
import argparse
import logging
from glob import glob


def check_for_unused_vars():
    variables_file, all_tf_files = find_tf_files()

    variables = parse_variables_tf(variables_file)
    var_references = find_used_variables(all_tf_files)
    unused_vars = list(variables - var_references)

    if len(unused_vars) > 0:
        logging.info('unused vars detected:')
        logging.info("%s\n" % unused_vars)
        remove_unused_vars(unused_vars, variables_file)
        sys.exit(1)
    else:
        logging.info('no unused variables found')
        sys.exit(0)


def find_tf_files():
    try:
        target_dir = os.getcwd() + "/" + args.dir.replace(".", '')
        all_tf_files = glob(os.path.join(args.dir, '*.tf'))
        logging.debug(f'tf files: {all_tf_files}')

        if len(all_tf_files) < 1:
            raise Exception(f'Failed to find required tf files in {target_dir}\nEnsure running '
                            f'from root terraform module.\n\nTo set custom dir use --dir PATH.')

        variables_file = glob(os.path.join(args.dir, '*' + args.var_file))[0]
        logging.debug(f'variable file: {variables_file}')

        return variables_file, all_tf_files
    except IndexError:
        raise Exception(f'Failed to find required variable file "{args.var_file}" in {target_dir}'
                        '\nEnsure running from root terraform module and the variable tf file exists.\n\nTo set '
                        'custom dir use --dir PATH.\nTo set custom var_file --var-file FILENAME\n')


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
    match = []
    logging.debug(f'searching for unused vars')
    for tf_file in tf_files:
        if 'variables.tf' in tf_file:
            logging.debug(f'skipping {args.var_file}')
            pass
        with open(tf_file, 'r') as file:
            lines = file.read()
            match += re.findall(r'var\.([\w_]+)', lines)
    return set(match)


def parse_variables_tf(var_file):
    temp = set()
    with open(var_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('variable'):
                temp.add(line[line.find("\"") + len("\""):line.rfind("\"")])
    return temp


def parse_args():
    parser = argparse.ArgumentParser(description='Scan root terraform module for unused variables and remove them.')
    parser.add_argument('--dir',
                        dest='dir',
                        default='.',
                        help='path to search for tf files (default: ".")')
    parser.add_argument('--var-file',
                        dest='var_file',
                        default='variables.tf',
                        help='path to search for tf files (default: "variables.tf")')
    parser.add_argument('--verbose', '-v',
                        dest='debug',
                        default=False,
                        action='store_true',
                        help='flag to show verbose output')

    return parser.parse_args()


def init_logger(debug):
    log_level = logging.INFO
    if debug:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level, format='%(levelname) -4s: %(message)s')
    # logging.debug('This message should go to the log file')
    # logging.info('So should this')
    # logging.warning('And this, too')
    # logging.error('And non-ASCII stuff, too, like Øresund and Malmö')


if __name__ == '__main__':
    args = parse_args()
    init_logger(args.debug)
    logging.debug(f'args: {vars(args)}')
    check_for_unused_vars()
