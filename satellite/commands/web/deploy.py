from operator import methodcaller
import posixpath
from fabric.context_managers import prefix

from fabric.api import run, cd, env
from fabric.utils import fastprint
from fabric.contrib.files import exists


def deploy_head(*args):
    cmd = 'git ls-remote %s | head -n 1 | cut -f 1,1' % env.GIT_REPO
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

    abs_path = posixpath.join(env.ROOT_DIR, env.REV_DIR, revision)

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

    # What is better, migrate DB before or after dir change?
    update_link(abs_path)


def update_link(path):
    run('ln -Tfs %s %s' % (path, env.APP_DIR))


def prod_config(path):
    prod = posixpath.join(path, env.FABFILE_DIR, 'production_settings.py')
    orig = posixpath.join(path, 'eve', 'settings', 'local.py')
    run('cp -f %s %s' % (prod, orig))


def collect_static(path):
    if not exists(env.PUBLIC_DIR):
        run('mkdir %s' % env.PUBLIC_DIR)
    run('ln -Tfs %s %s' % (env.PUBLIC_DIR, posixpath.join(path, 'public')))

    with cd(path):
        with prefix(env.activate):
            run('python manage.py collectstatic --noinput')


### DB stuff
def migrate_db(path):
    with cd(path):
        with prefix(env.activate):
            run('python manage.py migrate')


def sync_db(path):
    with cd(path):
        with prefix(env.activate):
            run('python manage.py syncdb --noinput')


### Dependencies:
def update_deps(path):
    if not exists(env.VENV_DIR):
        run("virtualenv %s --system-site-packages" % env.VENV_DIR)
    with cd(path):
        with prefix(env.activate):
            run('pip install -r requirements.txt')


### Git stuff
def update_repo(path):
    with cd(path):
        run('git pull')
        run('git submodule update')


def install_repo(dest):
    run('git clone %s %s' % (env.GIT_REPO, dest))

    with cd(dest):
        run('git submodule init')
        run('git submodule update')


def getssetting(name):
    """
    Get remote setting from django.conf.settings
    """
    return run('python -W ignore::DeprecationWarning ./manage.py getsetting %s' % name)