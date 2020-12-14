#!/usr/bin/env python
# Copyright (c) 2020 Alex Carrega <contact@alexcarrega.com>
# author: Alex Carrega <contact@alexcarrega.com>

# General
from datetime import datetime
from os import path
from typing import Callable, Iterable
# Local
from src import log
from src import settings


def _(out: str) -> any:
    return lambda x: out.format(x)


def check_param(key: str, value: str, allowed_values: Iterable = [], file: bool = False, dir: bool = False):
    _log = log.logger('utils')
    _icon = settings.icons.get(key)
    _allow_vals = joinmap(_('[hl]{}[/hl]'), allowed_values)
    _msg = f'[inf]Available[/inf] :{_icon}: {key}s: {_allow_vals}.'
    _not_found = '[error]not[/error] [hl]found[/hl].'
    _not_valid = '[error]not[/error] [hl]valid[/hl].'
    if value is None:
        _log.error(f'[error]Missing[/error] :{_icon}: [hl]{key}[/hl].')
        if allowed_values:
            _log.info(_msg)
        exit(1)
    if allowed_values and value not in allowed_values:
        _log.error(f'{key.title()} :{_icon}: [hl]{value}[/hl] ' +
                   '[error]unknown[/error].')
        _log.info(_msg)
        exit(2)
    if file:
        if not path.exists(value):
            _log.error(f'File {key} :{_icon}: [hl]{value}[/hl] ' +
                       _not_found)
            exit(3)
        if not path.isfile(value):
            _log.error(f'File {key} :{_icon}: [hl]{value}[/hl] ' +
                       _not_valid)
            exit(4)
    if dir:
        if not path.exists(value):
            log.error(f'Directory {key} :{_icon}: [hl]{value}[/hl] ' +
                      _not_found)
            exit(5)
        if not path.isdir(value):
            log.error(f'Directory {key} :{_icon}: [hl]{value}[/hl] ' +
                      _not_valid)
            exit(4)


class DateTime:
    FORMAT = '%Y-%m-%dT%H:%M:%S'

    @staticmethod
    def from_str(date_time_str, format=FORMAT):
        """Get a datetime object from the string.

        :params date_time_str: datetime in string
        :params format: datetime format
        :returns: datetime object
        """
        return datetime.strptime(date_time_str, format)

    @staticmethod
    def to_str(date_time=None, format=FORMAT):
        """Convert the datetime to string in the given format.

        :params data_time: datetime input
        :params format: datetime format
        :returns: datetime string in the given format
        """
        if date_time is None:
            date_time = datetime.utcnow()
        return date_time.strftime(format)


def joinmap(func: Callable, sequence: list, sep: str = ', ') -> str:
    return sep.join(map(func, sequence))
