import os
import re
import sys
from glob import glob


def check_for_unused_vars():
    variables_file = [tf_files for files in os.walk('.') for tf_files in glob(os.path.join(files[0], '*variables.tf'))]
    all_tf_files = [tf_files for files in os.walk('.') for tf_files in glob(os.path.join(files[0], '*.tf'))]
    
    variables = parse_variables_tf(variables_file[0])
    var_references = find_used_variables(all_tf_files)
    unused_vars = list(variables - var_references)
    
    if len(unused_vars) > 0:
        print('unused vars detected:')
        print("%s\n" % unused_vars)
        remove_unused_vars(unused_vars, variables_file[0])
        sys.exit(1)
    else:
        print('no unused variables found')
        sys.exit(0)


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
                    print('removing...' + variable)
                else:
                    new_file += line
            elif not removing_variable:
                new_file += line
                
    with open(var_file, 'w') as file:
        file.write(new_file)
        
        
def find_used_variables(tf_files):
    match = []
    for tf_file in tf_files:
        if 'variables.tf' in tf_file:
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
  
  
if __name__ == '__main__':
    # args = parse_args()
    check_for_unused_vars()
