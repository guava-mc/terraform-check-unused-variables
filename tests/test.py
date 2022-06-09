import os

"""
"""

VARIABLE_FILES = ['variables.tf', 'module_test/variables.tf',
                  '.assertions/variables.tf', '.assertions/module_test/variables.tf']
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
EXPECTED_VALUES = []
RESULT_VALUES = []


def get_results(args):
    global EXPECTED_VALUES
    global RESULT_VALUES
    EXPECTED_VALUES = []
    RESULT_VALUES = []
    for var_file in VARIABLE_FILES:
        with open(CURRENT_DIR + '/' + var_file, 'r') as file:
            text = file.read()
            if '.assertions' in var_file:
                EXPECTED_VALUES.append(text)
            else:
                RESULT_VALUES.append(text)


def run_test(args):
    os.system(f"python3 {PARENT_DIR}/terraform-check-unused-variables.py -r")
    get_results(args)
    for i, file in enumerate(EXPECTED_VALUES):
        assert file == RESULT_VALUES[i]


def clean_up():
    os.system(f"git checkout -- {CURRENT_DIR}/*")


def parse_args():
    return {}


if __name__ == '__main__':
    args = parse_args()
    # setup(args)
    run_test(args)
    clean_up()
