#!/usr/bin/env python
# Copyright (c) 2020 Alex Carrega <contact@alexcarrega.com>
# author: Alex Carrega <contact@alexcarrega.com>

# General
from bunch import Bunch
from rich.theme import Theme

about = Bunch(
    author=Bunch(
        name='Alex Carrega',
        email='contact@alexcarrega.com'
    ),
    name='pimp-my-rest',
    version='1.0.0',
    description='Invoke wrapper to make REST request and display the results in a table pretty format.',
    url='https://github.com/alexcarrega/pimp-my-rest'
)

icons = Bunch(
    file='file_folder',
    # setup
    requirements='triangular_ruler',
    readme='book',
    username='man',
    password='secret'
)

style = Bunch(
    bold_cyan='bold cyan',
    bold_green='bold green',
    bold_red='bold red',
    bold_yellow='bold yellow',
    bold_purple='bold purple'
)

theme = Theme({
    # log level
    'spam': style.bold_purple,
    'debug': style.bold_purple,
    'verbose': style.bold_purple,
    'info': style.bold_cyan,
    'notice': style.bold_cyan,
    'warning': style.bold_yellow,
    'success': style.bold_green,
    'error': style.bold_red,
    'critical': style.bold_red,
    # log format
    'filename': style.bold_green,
    'function': style.bold_yellow,
    'lineno': style.bold_red,
    'log-name': 'bold purple',
    'log-time': 'cyan',
    # log extra
    'hl': 'purple'
})
