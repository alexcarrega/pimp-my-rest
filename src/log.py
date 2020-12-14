#!/usr/bin/env python
# Copyright (c) 2020 Alex Carrega <contact@alexcarrega.com>
# author: Alex Carrega <contact@alexcarrega.com>

# General
from dynaconf import settings
from inspect import FrameInfo, stack
from logging import Formatter as DefaultFormatter, LogRecord, Logger
from os import path
from re import sub
from loguru import logger
from rich.traceback import install as traceback_install
from sys import stderr, stdout
# Locals
from src import settings


traceback_install(show_locals=False)


class Formatter(DefaultFormatter):
    @staticmethod
    def info(name: str) -> FrameInfo:
        for _s in stack():
            if name in _s.filename.replace('_', '-'):
                return _s

    def format(self, record: LogRecord) -> str:
        _s = self.info(record.name)
        record.calledfilename = path.basename(_s.filename)
        record.calledfunction = _s.function
        record.calledlineno = _s.lineno
        record.levelstyle = record.levelname.lower()
        record.levelicon = settings.icons.get(record.levelstyle)
        return DefaultFormatter.format(self, record)


class NoStyleFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        _out = DefaultFormatter.format(self, record)
        _out = sub(r'\[[^\]]*\]([^\]]*)\[\/[^\]]*\]', r'\1', _out)
        _out = sub(r':[A-Za-z-_]*:[ ]{0,1}', '', _out)
        return _out


def logger(name: str) -> Logger:
    _l = settings.log

    logger.add(stdout, colorize=True, **_l.console)
    logger.add(f'{_l.file.path}/{name}.log', **_l.file)

    def __response(r, ok, error, force={'ok': False, 'error': False, 'exit': True}):
        _stdout = r.stdout.strip()
        _stderr = r.stderr.strip()
        if r.ok:
            if _stderr and not force.get('ok', False):
                for l in _stderr.splitlines():
                    logger.warning(l)
            elif _stdout and not force.get('ok', False):
                for l in _stdout.splitlines():
                    logger.success(l)
            else:
                logger.info(ok)
        else:
            if _stderr and not force.get('error', False):
                for l in _stderr.strip().splitlines():
                    logger.error(l)
            elif _stdout and not force.get('error', False):
                for l in _stdout.strip().splitlines():
                    logger.error(l)
            else:
                logger.error(error)
            logger.warning(f':{settings.icons.exit}: [warning]Exit[/warning] ' +
                           f':{settings.icons.code}: code: [hl]{r.exited}[/hl]')
        if force.get('exit', True):
            exit(r.exited)
        else:
            return r.exited
    logger.response = __response

    logger.setLevel(_l.logger.get(name, _l.logger.__default__))

    return logger


class DisableHandler:
    def __init__(self, log: Logger, index: str):
        self.log = log
        self.index = index

    def __enter__(self):
        self.hndl = self.log.handlers[self.index]
        del self.log.handlers[self.index]

    def __exit__(self, exit_type, exit_value, exit_traceback):
        self.log.handlers.append(self.hndl)


class Section:
    def __init__(self, log: Logger, title: str):
        self.console = log.console
        self.title = title

    def __enter__(self):
        self.console.rule(self.title)

    def __exit__(self, exit_type, exit_value, exit_traceback):
        self.console.print()
