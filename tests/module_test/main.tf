locals {
    one     = var.module_one
    three   = [var.module_three]
    five    = coalesce(var.module_four, var.module_five)

    seven   = "var.module_seven"
    nine    = svar.nine
}

