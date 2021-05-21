# Copyright (c) 2020 Alex Carrega <contact@alexcarrega.com>
# author: Alex Carrega <contact@alexcarrega.com>

from functools import partial
from inspect import FrameInfo, stack
from os import path

# General
from bunch import Bunch
from dynaconf import Dynaconf
from emoji import emojize
from loguru import logger as loguru
from rich.traceback import install as traceback_install

from data import about

traceback_install(show_locals=False)
emoji = partial(emojize, use_aliases=True)


class Formatter:
    @staticmethod
    def info(name: str) -> FrameInfo:
        for s in stack():
            if name.replace('_', '') in s.filename.replace('_', '-'):
                return s

    @classmethod
    def apply(cls, record) -> str:
        s = cls.info(record['name'])
        record['called'] = Bunch(filename=path.basename(s.filename), function=s.function,
                                 lineno=s.lineno, icon=emoji(':computer:'))
        record['elapsed'] = Bunch(time=record['elapsed'], icon=emoji(':alarm_clock:'))
        record['message'] = emoji(record['message'])


class Log:
    __instance = None

    @classmethod
    def get(cls, name: str = about.name):
        if cls.__instance is None:
            cfg = Dynaconf(settings_files=["log.yaml"])
            logger = loguru.bind(context=name)
            hdls = []
            for _k, _v in cfg.sinks.items():
                if _v.get('enabled', True):
                    _h = dict(sink=_v.klass.format(name=name), **_v.args)
                    hdls.append(_h)
            logger.configure(handlers=hdls, patcher=Formatter.apply)
            cls.__instance = logger.opt(colors=True)
        return cls.__instance


log = Log.get()
