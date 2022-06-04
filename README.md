# terraform-check-unused-variables

a pre-commit hook for finding unused variables in terraform modules and removing them.

### Scan terraform module(s) for unused variables and remove them.

#### optional arguments:
```
  -h, --help           show this help message and exit
  --dir DIR            root dir to search for tf files in (default: ".")
  --var-file VAR_FILE  file name for where tf variables are defined (default: "variables.tf")
  -r                   flag to run check unused variables recursively on all directories from root dir
  --check-only         flag to only check for unused vars, not remove them
  --verbose, -v        flag to show verbose (debug) output
  --quiet, -q          flag to hide all non-error output. overrides verbose
```

# example .pre-commit-config.yaml

```yaml
repos:
-   repo: https://github.com/mcole18/terraform-check-unused-variables.git
    rev: v0.2.4-alpha
    hooks:
    -   id: check-unused-vars
        args: [-r, --dir=., --var-file=variables.tf]
```
