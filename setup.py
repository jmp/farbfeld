#!/usr/bin/env python

from distutils.core import setup

setup(
    name="farbfeld",
    version="0.1.0",
    description="Loader for the farbfeld image format.",
    author="Jarkko Piiroinen",
    author_email="jmp@python.mail.kapsi.fi",
    url="https://github.com/jmp/farbfeld",
    py_modules=["farbfeld"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics",
    ],
)
