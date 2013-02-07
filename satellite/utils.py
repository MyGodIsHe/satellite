from fabric.operations import run
from fabric.context_managers import settings
from fabric.contrib.files import upload_template
from fabric.api import env

import satellite
import os


__all__ = ['sudo', 'sudo_upload_template', 'get_template', 'get_template_dir']


# fix for sudo_user
def sudo(command, *args, **kwargs):
    with settings(user=env.orig_user):
        run("sudo %s" % command, *args, **kwargs)

def sudo_upload_template(*args, **kwargs):
    kwargs["use_sudo"] = True
    with settings(user=env.orig_user):
        upload_template(*args, **kwargs)


def get_template(path):
    return os.path.join(satellite.__path__[0], 'templates', path)


def get_template_dir():
    return os.path.join(satellite.__path__[0], 'templates')