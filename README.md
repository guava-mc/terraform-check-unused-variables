# terraform-check-unused-variables

a [soon to be] pre-commit hook for finding unused variables in terraform modules and removing them.

## Assumptions
- all tf files are in a single directory and related to a single module
- variables are only declared in variables.tf
- there are more things to add here and to the script
