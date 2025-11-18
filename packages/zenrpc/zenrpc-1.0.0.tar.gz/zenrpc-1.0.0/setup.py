#!./venv/bin/python3
'''
Created on 20220926
Update on 20251114
@author: Eduardo Pagotto
'''

import os
from setuptools import setup, find_packages

from zenrpc import __version__ as VERSION

PACKAGE = "zenrpc"

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname), "r", encoding="utf-8") as f:
        return f.read()

setup(
    name="zenrpc",
    version=VERSION,
    author="Eduardo Pagotto",
    author_email="edupagotto@gmail.com",
    description="Json RPC Python server-client class syn and async",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    url="https://github.com/EduardoPagotto/zenrpc.git",
    packages=find_packages(
        where=".",
        exclude=["tests.*", "tests"]
    ),
    platforms='any',
    include_package_data=True,
    license=read('LICENSE'),
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: File Formats :: JSON",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    install_requires=['setuptools',
                      'typing_extensions',
                      'wheel',
                      'zencomm',
                      'sjsonrpc'])
