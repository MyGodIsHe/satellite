from fabric.api import run
from satellite import *


def start():
    run('uwsgi --ini %s' % settings.uwsgi.config)


def stop():
    run('uwsgi --stop %s' % settings.uwsgi.pid)


def reload():
    run('touch %s' % settings.uwsgi.touch_reload)