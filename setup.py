from setuptools import setup

setup(
    name="check-unused-vars",
    version=1.0,
    package=["pre-commit"],
    description="remove unused variables from terraform",
    scripts=["terraform-check-unused-variables.py"],
)
