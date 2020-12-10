#!/usr/bin/env python
# Copyright (c) 2020 Alex Carrega <contact@alexcarrega.com>
# author: Alex Carrega <contact@alexcarrega.com>

import about
import setuptools

with open('requirements.txt') as _f:
    requirements = _f.readlines()
requirements = [_x.strip() for _x in requirements]

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name=about.name,
    version=about.version,
    author=about.author,
    author_email=about.author_email,
    description=about.description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=about.url,
    packages=['.'],
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': ['invrest = tasks:program.run']
    }
)
