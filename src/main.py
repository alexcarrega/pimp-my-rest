#!/usr/bin/env python
# Copyright (c) 2020-2029 Alex Carrega <contact@alexcarrega.com>
# author: Alex Carrega <contact@alexcarrega.com>

import itertools
import os
from datetime import datetime
from itertools import chain
from re import match
from string import Template

import click
import jmespath
import timeago
from braceexpand import braceexpand
from dynaconf import Dynaconf
from requests import get
from rich import box
from rich.console import Console
from rich.table import Table

from config import Config
from data import theme
from log import log
from utils import DateTime

config = Dynaconf(settings_files=['config.yaml'])
console = Console(theme=theme)

CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}


@click.group(context_settings=CONTEXT_SETTINGS, help=f'{config.name}\n\n{config.help}')
@click.option('-c', '--config', type=Config(), default='config.yaml', help='Configuration file.')
@click.pass_context
def main(ctx, config):
    ctx.config = config


for ep, ep_data in config.endpoints.items():
    def endpoint_handler(endpoint, data):
        @main.command(name=endpoint, short_help=data.help, help=data.help)
        @click.option('-p', '--profile', default=['default'], multiple=True, help='Profile to use.')
        @click.option('-e', '--expr', default=None, multiple=False,
                      help='Expression to filter the result (based on JMESPath).')
        def endpoint_cmd(profile: list = ['default'], expr: str = None):
            body = data.get('body', '')

            if isinstance(body, dict) and 'template' in body:
                body_template = config.get('body', {}).get(body.get('template')).get('content')
                body = Template(body_template).substitute(**body)

            headers = config.get('headers')
            prof_data = {}
            for prof in profile:
                if prof in config.profiles:
                    prof_data.update(config.profiles.get(prof).to_dict())

            try:
                for k, v in headers.items():
                    headers[k] = Template(v).substitute(**prof_data)
                r = get(Template(data.get('uri')).substitute(**prof_data), headers=headers, json=body)
            except KeyError as key_err:
                log.error(f'Variable {key_err} not defined')
                print(f'Error: variable {key_err} not defined')
                exit(os.EX_CONFIG)

            if r.status_code >= 300:
                log.error(f'Request not correct: {r.content}')
                exit(1)
            r_json = r.json()
            if expr:
                r_json = jmespath.search(expr, r_json)
            if isinstance(r_json, dict):
                r_json = [r_json]

            table = Table(title=data.get('title', ''), show_lines=True, box=box.DOUBLE_EDGE)

            fields = list(set(chain.from_iterable(r_json)))
            fields = list(itertools.chain(*map(braceexpand, fields)))
            for field in fields:
                table.add_column(__caption(field), style=config.style.get(field, ''))

            for rec in r_json:
                row = []
                for field in fields:
                    val = rec.get(field)
                    if val is not None and type(val) is list and len(val) == 1:
                        val = val[0]
                    elif (
                        val is not None
                        and type(val) is list
                        and len(val) == 0
                        or val is None
                    ):
                        val = ''
                    row.append(__parse_cell(val, key=field))
                table.add_row(*row)
            console.print(table)
    endpoint_handler(endpoint=ep, data=ep_data)


def __parse_cell(cell: any, key: str = None) -> any:
    table = Table(show_header=False, show_lines=True, box=box.ROUNDED)
    if isinstance(cell, list):
        table.add_column()
        for c in cell:
            table.add_row(__parse_cell(c, key))
        return table
    elif isinstance(cell, dict):
        table.add_column()
        table.add_column()
        for k, v in cell.items():
            table.add_row(__caption(k), __parse_cell(v, k))
        return table
    else:
        cell = str(cell).strip()
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', cell):
            cell = timeago.format(DateTime.from_str(cell), datetime.utcnow())
        if not cell:
            cell = ' :no_entry_sign: empty'
        if key:
            stl = config.style.get(key, '')
            if not isinstance(stl, str):
                stl = stl.get(str(cell), '')
            if stl:
                return f'[{stl}]{cell}[/{stl}]'
        return cell


def __caption(key: str) -> str:
    caption: list = []
    for part in key.split('.'):
        icon: str = config.icon.get(part, '')
        o: str = (f':{icon}: ' if icon else '') + part.title().replace('_', ' ').replace('.', ' / ')
        caption.append(o)
    return ' / '.join(caption)


if __name__ == '__main__':
    main()
