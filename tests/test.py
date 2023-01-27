import os

"""
"""

VARIABLE_FILES = ['variables.tf', 'module_test/variables.tf']
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
        RESULT_VALUES.append(read_test_vars(CURRENT_DIR + '/' + var_file))
        EXPECTED_VALUES.append(read_test_vars(CURRENT_DIR + '/.assertions/' + var_file))


def read_test_vars(path):
    with open(path, 'r') as file:
        return file.read()


def run_dir_test(args):
    os.system(f"python3 {PARENT_DIR}/terraform-check-unused-variables.py --dir . -q")
    get_results(args)
    print('dir test 1...', end='')
    assert EXPECTED_VALUES[0] == RESULT_VALUES[0]
    print('pass')
    print('dir test 2...', end='')
    assert EXPECTED_VALUES[1] != RESULT_VALUES[1]
    print('pass')
    clean_up()


def run_recursive_test(args):
    os.system(f"python3 {PARENT_DIR}/terraform-check-unused-variables.py -rq ")
    get_results(args)
    for i, file in enumerate(EXPECTED_VALUES):
        print(f'recursive test {i + 1}...', end='')
        assert file == RESULT_VALUES[i]
        print('pass')
    clean_up()


def run_ignore_test(args):
    ignore_flag = 'tf-check-unused-vars:skip'
    os.system(f"python3 {PARENT_DIR}/terraform-check-unused-variables.py -rq --ignore {ignore_flag}")
    get_results(args)
    for i, file in enumerate(RESULT_VALUES):
        print(f'ignore test {i + 1}...', end='')
        assert ignore_flag in file
        assert '# ignore' not in file
        print('pass')
    clean_up()


def clean_up():
    os.system(f"git checkout -- {CURRENT_DIR}/*")


def parse_args():
    return {}


def test_header(text):
    whitespace = '    '
    text = whitespace + text + whitespace
    flavor = '=' * ((80 - len(text)) // 2)
    text = flavor + text + flavor + '\n'
    linebreak = '=' * (len(text)-1) + '\n'
    print(linebreak + text + linebreak)


if __name__ == '__main__':
    try:
        args = parse_args()
        test_header('Running tests')
        run_dir_test(args)
        run_recursive_test(args)
        run_ignore_test(args)
    finally:
        clean_up()
