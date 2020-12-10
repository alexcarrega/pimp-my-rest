# Copyright (c) 2020 Alex Carrega <contact@alexcarrega.com>
# author: Alex Carrega <contact@alexcarrega.com>

from datetime import datetime
from typing import Callable
import json


def _(out: str) -> any:
    return lambda x: out.format(x)


FORMAT = '%Y-%m-%dT%H:%M:%S'


def datetime_from_str(date_time_str, format=FORMAT):
    """Get a datetime object from the string.

    :params date_time_str: datetime in string
    :params format: datetime format
    :returns: datetime object
    """
    return datetime.strptime(date_time_str, format)


def datetime_to_str(date_time=None, format=FORMAT):
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


class StdClass:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.set(k, v)

    def set(self, k: str, v: any):
        if isinstance(v, dict):
            setattr(self, k, StdClass(**v))
        else:
            setattr(self, k, v)

    def get(self, k: str, default: any = None) -> any:
        if self.has(k):
            return getattr(self, k)
        return default

    def has(self, k: str) -> bool:
        return hasattr(self, k)

    def to_dict(self) -> dict:
        return json.loads(json.dumps(self, default=lambda o: o.__dict__))
