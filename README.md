# terraform-check-unused-variables

a pre-commit hook for finding unused variables in terraform modules and removing them.

### Scan terraform module(s) for unused variables and remove them.

#### optional arguments:
```
  -h, --help           show this help message and exit
  --dir DIR            root dir to search for tf files in (default: ".")
  --var-file VAR_FILE  file name for where tf variables are defined (default: "variables.tf")
  -r, --recursive      flag to run check unused variables recursively on all directories from root dir
  --check-only         flag to only check for unused vars, not remove them
  --verbose, -v        flag to show verbose (debug) output
  --quiet, -q          flag to hide all non-error output.
```

### example .pre-commit-config.yaml

```yaml
repos:
-   repo: https://github.com/mcole18/terraform-check-unused-variables.git
    rev: v1.0.0
    hooks:
    -   id: check-unused-vars
        args: [-r, --dir=., --var-file=variables.tf]
```
### Assumptions

This pre-commit hook assumes standard terraform practices where all variables are declared in a single file for a module and that variables are declared with no leading white space on the keyword or before the closing curly brace.

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

To ignore, or skip removing unused variables you can either comment out the variable since the check assumes the line starts with the keyword variable, or you can add a `# ignore` comment on the previous line, or an `# ignore` comments at the end of the line where the variable is declared.

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
