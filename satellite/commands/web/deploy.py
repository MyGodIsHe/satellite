from operator import methodcaller

from fabric.api import run
from fabric.utils import fastprint
from fabric.contrib.files import exists

from satellite import *
from satellite.commands.web.django import prod_config, collect_static, sync_db, migrate_db
from satellite.commands.web.system import install_repo, update_repo, update_deps, adduser


def apply(*args):
    default_options = [
        'db',
        'deps',
        'all',
        ]

    if not args:
        fastprint("Options: %s or none (fab deploy:)" % ','.join(default_options))
        return

    if len(args) == 1 and not args[0]:
        options = []
    else:
        options = map(methodcaller('lower'), args)
        if 'all' in options:
            options = default_options

    abs_path = settings.main.root_app

    if not exists(abs_path):
        install_repo(abs_path)
    else:
        update_repo(abs_path)

    if 'deps' in options:
        update_deps(abs_path)

    prod_config(abs_path)
    collect_static(abs_path)

    if 'db' in options:
        sync_db(abs_path)
        migrate_db(abs_path)



def create_environment():
    adduser()
    # TODO: create ssh access and repo access
    # ssh-keygen
    # touch .ssh/authorized_keys
    # create db, init nginx, supervisor
    dirs = [
        settings.main.root_public,
        settings.main.root_log,
        ]
    for dir in dirs:
        run('mkdir %s' % dir)
