#!/usr/bin/env python
# pylint: disable=missing-docstring

from os import path
from setuptools import setup


# Read long description from README.md
ROOT_DIR = path.abspath(path.dirname(__file__))
with open(path.join(ROOT_DIR, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()


setup(
    name="farbfeld",
    version="0.2.1",
    license="MIT",
    description="Library for reading/writing farbfeld images.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author="Jarkko Piiroinen",
    author_email="jmp@python.mail.kapsi.fi",
    url="https://github.com/jmp/farbfeld",
    py_modules=["farbfeld"],
    platforms=["any"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics",
        "Intended Audience :: Developers",
    ],
)
