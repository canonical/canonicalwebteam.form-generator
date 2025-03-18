#! /usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="canonicalwebteam.form-generator",
    version="1.0.0",
    author="Canonical webteam",
    author_email="webteam@canonical.com",
    url="https://github.com/canonical/canonicalwebteam.form-generator",
    description=(
        "Python script to generate HTML forms and attach them"
        "as a Flask view func."
    ),
    packages=find_packages(),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "Flask",
        "Jinja2",
    ],
)
