from fabric.contrib.files import upload_template
from fabric.api import run, cd
import posixpath
from fabric.context_managers import prefix

from satellite import *


def prod_config(path):
    upload_template(settings.main.local_settings, settings.main.remote_settings)


def collect_static(path):
    run('ln -Tfs %s %s' % (settings.main.root_public, posixpath.join(path, settings.main.app_public)))

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


def getssetting(name):
    """
    Get remote setting from django.conf.settings
    """
    return run('python -W ignore::DeprecationWarning ./manage.py getsetting %s' % name)
