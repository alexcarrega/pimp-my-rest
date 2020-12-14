#!/usr/bin/env python
# Copyright (c) 2020 Alex Carrega <contact@alexcarrega.com>
# author: Alex Carrega <contact@alexcarrega.com>

# General
from invoke import Collection, Program
# Local
from src import tasks
from src import settings

program = Program(namespace=Collection.from_module(tasks), version=settings.about.version)
