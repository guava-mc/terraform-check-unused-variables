import os

"""
"""

VARIABLE_FILES = ['./variables.tf', './module_test/variables.tf',
                  './.assertions/variables.tf', './.assertions/module_test/variables.tf']
EXPECTED_VALUES = []
RESULT_VALUES = []


def setup(args):
    for var_file in VARIABLE_FILES:
        with open(var_file, 'r') as file:
            text = file.read()
            if '.assertions' in var_file:
                EXPECTED_VALUES.append(text)
            else:
                RESULT_VALUES.append(text)


def run_test(args):
    current = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(current)
    os.system(f"python3 {parent}/terraform-check-unused-variables.py -r")
    setup(args)
    for i, file in enumerate(EXPECTED_VALUES):
        assert file == RESULT_VALUES[i]


def clean_up():
    os.system("git checkout -- tests/*")


def parse_args():
    return {}


if __name__ == '__main__':
    args = parse_args()
    # setup(args)
    run_test(args)
    clean_up()
