#!/usr/bin/env python
# Copyright (c) 2020 Alex Carrega <contact@alexcarrega.com>
# author: Alex Carrega <contact@alexcarrega.com>

import os
from datetime import datetime
from re import match
from sys import prefix

import click
import timeago
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
        @click.option('-p', '--profile', default='default', multiple=True, help='Profile to use.')
        @click.option('-s', '--select', default=None, multiple=True, help='Select only some fields.')
        @click.option('-w', '--where', default=None, multiple=True, help='Filter the data to get based on multiple conditions.')
        def endpoint_cmd(profile: str = 'default', select: str = None, where: str = None):
            if where:
                body = {'where': {'and': []}}
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
            else:
                body = {}
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
                table = Table(title=body.get('title', ''), show_lines=True, show_header=False,
                              collapse_padding=True, box=box.DOUBLE_EDGE)
                table.add_column()
                table.add_column()
                for k, v in r_json.items():
                    table.add_row(__caption(k), __parse_cell(v, k))
            else:
                table = Table(title=body.get('title', ''), show_lines=True, box=box.DOUBLE_EDGE)
                cols = []
                for rec in r_json:
                    for k in rec.keys():
                        if (not select or k in select) and k not in cols:
                            _stl = config.style.get(k, '')
                            if not isinstance(_stl, str):
                                _stl = ''
                            table.add_column(__caption(k), style=_stl)
                            cols.append(k)
                    row = []
                    for k in cols:
                        row.append(__parse_cell(rec.get(k, ''), key=k))
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
    icon = config.icon.get(key, '')
    key = key.title().replace('_', ' ')
    if icon:
        return f':{icon}: {key}'
    return key


if __name__ == '__main__':
    main()
