#!/usr/bin/env python
# Copyright (c) 2020 Alex Carrega <contact@alexcarrega.com>
# author: Alex Carrega <contact@alexcarrega.com>

# General
from os import path
from rich.console import Console
from setuptools import setup
# Local
from src.data import about, theme, icons

console = Console(theme=theme)
requirements_file = 'requirements.txt'
readme_file = 'README.md'


if path.exists(requirements_file):
    with open(requirements_file) as _f:
        requirements = _f.readlines()
    requirements = [_x.strip() for _x in requirements]
else:
    requirements = []
    console.print(f':{icons.warning}: [warning]WARNING   [/warning] Requirement :{icons.requirements}: file: [hl]{requirements_file}[/hl] ' +
                '[warning]not[/warning] [hl]found[/hl].')

if path.exists(readme_file):
    with open(readme_file, 'r', encoding='utf-8') as _f:
        long_description = _f.read()
else:
    console.print(f':{icons.error}: [error]ERROR   [/error] README :{icons.readme}: file: [hl]{readme_file}[/hl] ' +
                  '[error]not[/error] [hl]found[/hl].')
    exit(1)

setup(
    name=about.name,
    version=about.version,
    author=about.author.name,
    author_email=about.author.email,
    description=about.description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=about.url,
    packages=['src'],
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': ['pmrest = src.main:program.run']
    }
)
