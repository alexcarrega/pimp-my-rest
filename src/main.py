#!/usr/bin/env python
# Copyright (c) 2020 Alex Carrega <contact@alexcarrega.com>
# author: Alex Carrega <contact@alexcarrega.com>

import itertools
import os
from datetime import datetime
from itertools import chain
from re import match
from sys import prefix

import click
import dpath.util
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
@click.option('-c', '--config', type=Config(), default=lambda: config, help='Configuration file.')
@click.pass_context
def main(ctx, config):
    ctx.config = config


for ep, ep_data in config.endpoints.items():
    def endpoint_handler(endpoint, data):
        @main.command(name=endpoint, short_help=data.help, help=data.help)
        @click.option('-p', '--profile', default=['default'], multiple=True, help='Profile to use.')
        @click.option('-s', '--select', default=[], multiple=True, help='Select only some fields.')
        @click.option('-w', '--where', default=[], multiple=True, help='Filter the data to get based on multiple conditions.')
        @click.option('-o', '--order', default=[], multiple=True, help='Order the data based on multiple fields.')
        def endpoint_cmd(profile: list = ['default'], select: list = [], where: list = [], order: list = []):
            body = {}

            __where(where, body)
            __order(order, body)

            headers = config.get('headers')
            prof_data = {}
            for prof in profile:
                if prof in config.profiles:
                    prof_data.update(config.profiles.get(prof).to_dict())

            try:
                for k, v in headers.items():
                    headers[k] = v.format(**prof_data)
                r = get(data.get('uri').format(**prof_data), headers=headers, json=body)
            except KeyError as key_err:
                log.error(f'Variable {key_err} not defined')
                print(f'Error: variable {key_err} not defined')
                exit(os.EX_CONFIG)

            r_json = r.json()
            if isinstance(r_json, dict):
                r_json = [r_json]
            table = Table(title=body.get('title', ''), show_lines=True, box=box.DOUBLE_EDGE)

            if not select:
                select = list(set(chain.from_iterable(r_json)))

            fields = list(itertools.chain(*map(braceexpand, select)))
            for field in fields:
                table.add_column(__caption(field), style=config.style.get(field, ''))

            for rec in r_json:
                row = []
                for field in fields:
                    val = dpath.util.values(rec, field, separator='.')
                    if type(val) is list:
                        if len(val) == 1:
                            val = val[0]
                        elif len(val) == 0:
                            val = ''
                    row.append(__parse_cell(val, key=field))
                table.add_row(*row)
            console.print(table)
    endpoint_handler(endpoint=ep, data=ep_data)


def __where(where: dict, body: dict) -> None:
    if where:
        body['where'] = {'and': []}
        for w in where:
            clause = {}
            op = clause
            if w.startswith('!'):
                w = w[1:]
                op = {}
                clause['not'] = op
            if match('^[^=]*=[^=]*$', w):
                _target, _expr = w.split('=')
                op['equals'] = {'target': _target, 'expr': _expr}
            elif match('^[^~]*~[^~]*$', w):
                _target, _expr = w.split('~')
                op['reg_exp'] = {'target': _target, 'expr': _expr}
            else:
                log.error(f':{config.icon.where}: ' + '<b>Where</b> clause <red><b>not</b></red> <b>valid</b>.')
                exit(1)
            body['where']['and'].append(clause)


def __order(order: dict, body: dict) -> None:
    if order:
        body['order'] = []
        for o in order:
            mode: str = 'asc'
            if o.startswith('>'):
                mode: str = 'desc'
                o = o[1:]
            elif o.startswith('<'):
                o = o[1:]
            body['order'].append({'target': o, 'mode': mode})


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
        if match('\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', cell):
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
