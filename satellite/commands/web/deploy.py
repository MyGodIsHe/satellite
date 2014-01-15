from operator import methodcaller

from fabric.api import run, prompt, local
from fabric.utils import fastprint
from fabric.contrib.files import exists

from satellite import *
from satellite.commands.web.django import prod_config, collect_static, sync_db, migrate_db
from satellite.commands.web.system import install_repo, update_repo, update_deps, adduser, ssh_keygen, add_access


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
    ssh_keygen()
    key = local('cat ~/.ssh/id_rsa.pub', capture=True)
    add_access(key)
    dirs = [
        settings.main.root_public,
        ]
    for dir in dirs:
        run('mkdir %s' % dir)
    prompt('Done. Now you can create DB.')
