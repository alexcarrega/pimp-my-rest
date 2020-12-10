# Copyright (c) 2020 Alex Carrega <contact@alexcarrega.com>
# author: Alex Carrega <contact@alexcarrega.com>

from utils import StdClass
from yaml import loader
import os
import yaml


def config(*args, filename: str = 'config.yaml', **kwargs) -> StdClass:
    _content = {}
    _cfg = StdClass()
    assert(os.path.exists(filename))
    with open(f'{filename}') as _file:
        _content = yaml.load(_file, Loader=yaml.FullLoader)
    for _k in args:
        _cfg.set(__format(_k), _content.get(_k, {}))
    for _k, _v in kwargs.items():
        for _ik in _v:
            _cfg.set(__format(_ik), _content.get(_k, {}).get(_ik, {}))
    return _cfg


def __format(key: str) -> str:
    return key.replace('-', '_')
