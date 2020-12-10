#!/usr/bin/env inv
# Copyright (c) 2020 Alex Carrega <contact@alexcarrega.com>
# author: Alex Carrega <contact@alexcarrega.com>

from about import version
from ago import human
from config import config
from glob import glob
from invoke import Program, task
from log import logger
from os import path
from rich import box
from rich.console import Console
from rich.table import Table
from re import match
from requests import get
from style import theme
from typing import Iterable
from utils import _, datetime_from_str, joinmap, StdClass


program = Program(version=version)

log = logger('tasks')

cfg_main = config('icon', filename='config/main.yaml')

cfg_settings = config('vars', 'style', 'icon', 'endpoints',
                      filename='config/settings.yaml')

console = Console(theme=theme, record=True)


for _ep, _data in cfg_settings.endpoints.to_dict().items():
    def __endpoint(cfg_data):
        def _f(c, field=None, method=None, data=None, where=None):
            if where:
                _data = dict(where={'and': []})
                for _w in where:
                    _clause = dict()
                    _op = _clause
                    if _w.startswith('!'):
                        _w = _w[1:]
                        _op = dict()
                        _clause['not'] = _op
                    if match('^[^=]*=[^=]*$', _w):
                        _target, _expr = _w.split('=')
                        _op['equals'] = dict(target=_target, expr=_expr)
                    elif match('^[^~]*~[^~]*$', _w):
                        _target, _expr = _w.split('~')
                        _op['reg_exp'] = dict(target=_target, expr=_expr)
                    else:
                        log.error(
                            f':{cfg_settings.icon.where}: [hl]Where[/hl] clause [err]not[/err] [hl]valid[/hl]')
                        exit(1)
                    _data['where']['and'].append(_clause)
            else:
                _data = {}
            _r = get(cfg_data.get('uri').format(
                **cfg_settings.vars.to_dict()), json=_data)
            _r_json = _r.json()
            if isinstance(_r_json, dict):
                _table = Table(title=cfg_data.get(
                    'title', ''), show_lines=True, show_header=False, collapse_padding=True, box=box.DOUBLE_EDGE)
                _table.add_column()
                _table.add_column()
                for _k, _v in _r_json.items():
                    _table.add_row(__caption(_k), __parse_cell(_v, _k))
            else:
                _table = Table(title=cfg_data.get('title', ''),
                               show_lines=True, box=box.DOUBLE_EDGE)
                _cols = []
                for _rec in _r_json:
                    for _k in _rec.keys():
                        if (not field or _k in field) and _k not in _cols:
                            _stl = cfg_settings.style.get(_k, '')
                            if isinstance(_stl, StdClass):
                                _stl = ''
                            _table.add_column(__caption(_k), style=_stl)
                            _cols.append(_k)
                    _row = []
                    for _k in _cols:
                        _row.append(__parse_cell(_rec.get(_k, ''), key=_k))
                    _table.add_row(*_row)
            console.print(_table)
        _f.__doc__ = _data.get('help', '')
        return _f
    locals()[_ep] = task(__endpoint(_data),
                         name=_ep, iterable=['field', 'where'])


@ task(name='config')
def show_config(c, type=None):
    """Print the configuration."""
    _choices = [path.basename(f).replace('.yaml', '')
                for f in glob('config/*.yaml')]
    __check(type, key='type', choices=_choices)
    with open(f'config/{type}.yaml') as _f:
        for _l in _f.readlines():
            log.info(_l.rstrip())


def __check(item: str, key: str, choices: Iterable = []):
    _icon = cfg_main.icon.get(key)
    _choices_str = joinmap(_('[hl]{}[/hl]'), choices)
    _msg = f'[inf]Available[/inf] :{_icon}: {key}s: {_choices_str}.'
    if item is None:
        log.error(f'[err]Missing[/err] :{_icon}: [hl]{key}[/hl].')
        log.info(_msg)
        exit(1)
    if choices and item not in choices:
        log.error(
            f'{key.title()} :{_icon}: [hl]{item}[/hl] [err]unknown[/err].')
        log.info(_msg)
        exit(2)


def __parse_cell(cell: any, key: str = None) -> any:
    _table = Table(show_header=False, show_lines=True, box=box.ROUNDED)
    if isinstance(cell, list):
        _table.add_column()
        for _c in cell:
            _table.add_row(__parse_cell(_c, key))
        return _table
    elif isinstance(cell, dict):
        _table.add_column()
        _table.add_column()
        for _k, _v in cell.items():
            _table.add_row(__caption(_k), __parse_cell(_v, _k))
        return _table
    else:
        cell = str(cell).strip()
        if match('\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', cell):
            cell = human(datetime_from_str(cell))
        if not cell:
            cell = ' :no_entry_sign: empty'
        if key:
            _stl = cfg_settings.style.get(key, '')
            if isinstance(_stl, StdClass):
                _stl = _stl.get(str(cell), '')
            if _stl:
                return f'[{_stl}]{cell}[/{_stl}]'
        return cell


def __caption(key: str) -> str:
    _icon = cfg_settings.icon.get(key, '')
    key = key.title().replace('_', ' ')
    if _icon:
        return f':{_icon}: {key}'
    return key
