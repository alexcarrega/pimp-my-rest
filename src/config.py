# Copyright (c) 2020 Alex Carrega <contact@alexcarrega.com>
# author: Alex Carrega <contact@alexcarrega.com>

from os import path

from click import ParamType
from dynaconf import Dynaconf

from log import Log


class Config(ParamType):
    name = 'config'
    log = Log.get()

    def convert(self, value, param, ctx):
        try:
            if not path.exists(value):
                self.log.error(f'Config file {value} not found.')
                exit(1)
            if not path.isfile(value):
                self.log.error(f'Config file {value} not valid.')
                exit(2)
            return Dynaconf(settings_files=[value])
        except Exception as e:
            self.log.exception(e)


CONFIG = Config()
