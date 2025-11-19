#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

NAME = "aws_enumerateiam"
VERSION = open("VERSION").read().replace("\n", "")
KEYWORDS = ("aws", "enumerate", "iam")
DESCRIPTION = "Enumerate the permissions associated with AWS credential set"
LONG_DRSCRIPTION = open("README.rst").read()
LICENSE = "MIT LICENSE"
URL = "https://github.com/andresrianch/enumerate-iam"
AUTHOR = "andresrianch"
AUTHOR_EMAIL = "andresrianch@gmail.com"
PACKAGES = find_packages()
INSTALL_REQUIRES = ["boto3", "botocore"]
TEST_SUITE = ""

setup(
    name=NAME,
    version=VERSION,
    keywords=KEYWORDS,
    description=DESCRIPTION,
    long_description=LONG_DRSCRIPTION,
    license=LICENSE,

    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,

    packages=PACKAGES,
    install_requires=INSTALL_REQUIRES,
    test_suite=TEST_SUITE,
)
