# terraform-check-unused-variables

a pre-commit hook for finding unused variables in terraform modules and removing them.

![pre-commit](https://img.shields.io/badge/pre--commit-Terraform-purple) ![python](https://shields.io/badge/python-v3.x-blue) ![semver](https://img.shields.io/badge/semver-v1.2.1-orange)
### Scan terraform module(s) for unused variables and remove them.

#### optional arguments:
```
  -h, --help           show this help message and exit
  --dir DIR            root dir to search for tf files in (default: ".")
  --check-only         flag to only check for unused vars, not remove them
  -r, --recursive      flag to run check unused variables recursively on all directories from root dir
  --ignore IGNORE_TXT  text in variable declaration comment used to tell the hook to ignore a specific unused
                       variable (Default: "ignore")
  -v, --verbose        flag to show verbose (debug) output
  -q, --quiet          flag to hide all non-error output.
```

### example .pre-commit-config.yaml

```yaml
repos:
-   repo: https://github.com/mcole18/terraform-check-unused-variables.git
    rev: v1.2.1
    hooks:
    -   id: check-unused-vars
        args: [-r, --dir=.]
```
### Assumptions

This pre-commit hook assumes standard terraform practices such as: variables are declared with no leading white space on the keyword or before the closing curly brace.

ex: variables.tf
```hcl
variable "example_one" {
    default = null
}

variable "example_two" {
    description = "this is another example"
    default = null
}

variable "example_three" {
    description = "this is another another example"
    type = string
}
```

### skipping desired unused variables

To ignore, or skip removing unused variables, you can either comment out the variable since the check assumes the line starts with the keyword variable, or you can add a `# ignore` comment on the previous line, or an `# ignore` comment at the end of the line where the variable is declared.

_NOTE: you can customize the ignore comment text with `--ignore IGNORE_TXT` this will replace the default "ignore" string with the custom value passed in._

ex 1:
```hcl
# variable "commented_out" {
#  description: "ignores commented variables"
#  type = list(string)
#  default = ['commented', 'out', 'variables', 'are', 'skipped']  
# }
```

ex 2:
```hcl
# ignore
variable "ignore_above" {
  description: "ignores variables with # ignore commented on previous line"
  type = bool
  default = True  
}
```

ex 3:
```hcl
variable "ignore_after" { # ignore
  description: "ignores variables with # ignore comment at end of line"
  type = bool
  default = True  
}
```

ex 4:
using `--ignore 'tf-check-unused-vars:skip'` option:

```hcl
# tf-check-unused-vars:ignore
variable "ignore_after" {
  description: "ignores variables with # ignore comment at end of line"
  type = bool
  default = True  
}
```
