import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(os.path.dirname(current))
VARIABLE_FILES = ['../variables.tf', '../module_test/variables.tf']

os.system(f"python3 {parent}/terraform-check-unused-variables.py --dir ../../tests -r")

for var_file in VARIABLE_FILES:
    assert_file_name = var_file.replace('../', './')
    with open(var_file, 'r') as file:
        text = file.read()
    with open(assert_file_name, 'w') as file:
        file.write(text)

os.system(f"git checkout -- {parent}/tests/*")
