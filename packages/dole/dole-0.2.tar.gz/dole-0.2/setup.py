#!/usr/bin/env python
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025, 2ps all rights reserved.

# Support setuptools only, distutils has a divergent and more annoying API and
# few folks will lack setuptools.
from setuptools import setup
# from importlib.resources import open_text
# Version info -- read without importing
_locals = {}

# PyYAML ships a split Python 2/3 codebase. Unfortunately, some pip versions
# attempt to interpret both halves of PyYAML, yielding SyntaxErrors. Thus, we
# exclude whichever appears inappropriate for the installing interpreter.
exclude = ["*.yaml2", 'test']

# Frankenstein long_description: version-specific changelog note + README
with open('README.md') as f:
    long_description = f.read()

extras = {}
all_extras = set()
for x in [ 'dev' ]:
    filename = f'{x}.txt'
    with open(filename, 'r') as f:
        st = f.read()
    rg = st.split()
    extras[x] = rg
    if x != 'dev':
        all_extras |= set(rg)
if all_extras:
    all_extras = list(all_extras)
    all_extras.sort()
    extras['all'] = all_extras


setup(
    name='dole',
    version='0.2',
    description='dole',
    license='BSD',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='2ps',
    url='https://github.com/crazy-penguins/dole',
    packages=[
        'dole',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'fastmcp==2.12.5',
        'py-key-value-aio[redis]',
    ],
    extras_require=extras,
)