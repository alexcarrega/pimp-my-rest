#!/usr/bin/env inv
# Copyright (c) 2020 Alex Carrega <contact@alexcarrega.com>
# author: Alex Carrega <contact@alexcarrega.com>

# General
from invoke import Responder, task
# Local
from src import log
from src import utils

@task
def build(c):
    """Build the package."""
    r = c.run('python setup.py sdist bdist_wheel')
    print(r)


@task
def install(c):
    """Install the package."""
    r = c.run('python setup.py install')
    print(r)


@task
def uninstall(c):
    """Uninstall the package."""
    _responder = Responder(
        pattern=r'Proceed \(y/n\)?',
        response='y\n',
    )
    _r = c.run('pip uninstall pimp-my-rest', watchers=[_responder])
    print(_r)


@task
def keyring(c, username=None, password=None):
    utils.check_param(key='username', value=username)
    utils.check_param(key='password', value=password)
    """Set the authentication for the upload."""
    _responder = Responder(
        pattern=f"Password for '{username}' in 'https://upload.pypi.org/legacy/':",
        response=password,
    )
    _r = c.run(f'keyring set https://upload.pypi.org/legacy/ {username}', watchers=[_responder], hide=False)
    print(_r)


@task
def upload(c):
    """Upload the package."""
    _r = c.run('python -m twine upload --repository pypi dist/*')
    print(_r)


@task
def clean(c):
    """Clean all the builds."""
    _r = c.run('rm -rf dist build *.egg-info')
    print(_r)


def print(r):
    r.stdout = r.stdout.strip()
    r.stderr = r.stderr.strip()
    if r.stdout:
        log.info(r.stdout)
    elif r.stderr:
        log.info(r.stderr)
