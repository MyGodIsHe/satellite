from operator import methodcaller
import posixpath
from fabric.context_managers import prefix

from fabric.api import run, cd
from fabric.utils import fastprint
from fabric.contrib.files import exists, upload_template

from satellite import *


def deploy_head(*args):
    cmd = 'git ls-remote %s | head -n 1 | cut -f 1,1' % settings.git.repo
    # because `run` will return the _full_ i/o log
    # including the password prompt
    revision = run(cmd).strip().split('\n')[-1]

    deploy(revision, *args)


def deploy(revision, *args):
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

    abs_path = posixpath.join(settings.main.root_revisions, revision)

    if not exists(abs_path):
        install_repo(abs_path)
    else:
        update_repo(abs_path)

    if 'deps' in options:
        update_deps(abs_path)

    update_link(abs_path)

    prod_config(abs_path)
    collect_static(abs_path)

    if 'db' in options:
        sync_db(abs_path)
        migrate_db(abs_path)


def update_link(path):
    run('ln -Tfs %s %s' % (path, settings.main.root_app))


def prod_config(path):
    upload_template(settings.main.local_settings, settings.main.remote_settings)


def collect_static(path):
    run('ln -Tfs %s %s' % (settings.main.root_public, posixpath.join(path, 'public')))

    with cd(path):
        with prefix(settings.main.venv_activate):
            run('python manage.py collectstatic --noinput')


### DB stuff
def migrate_db(path):
    with cd(path):
        with prefix(settings.main.venv_activate):
            run('python manage.py migrate')


def sync_db(path):
    with cd(path):
        with prefix(settings.main.venv_activate):
            run('python manage.py syncdb --noinput')


### Dependencies:
def update_deps(path):
    if not exists(settings.main.root_venv):
        run("virtualenv %s --system-site-packages" % settings.main.root_venv)
    with cd(path):
        with prefix(settings.main.venv_activate):
            run('pip install -r requirements.txt')


### Git stuff
def update_repo(path):
    with cd(path):
        run('git pull')
        run('git submodule update')


def install_repo(dest):
    run('git clone %s %s' % (settings.git.repo, dest))

    with cd(dest):
        run('git submodule init')
        run('git submodule update')


def getssetting(name):
    """
    Get remote setting from django.conf.settings
    """
    return run('python -W ignore::DeprecationWarning ./manage.py getsetting %s' % name)


def adduser():
    sudo('adduser --disabled-password %s' % settings.fabric.user)


def create_environment():
    adduser()
    dirs = [
        settings.main.root_revisions,
        settings.main.root_public,
        settings.main.root_log,
    ]
    for dir in dirs:
        run('mkdir %s' % dir)