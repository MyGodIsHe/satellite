from fabric.contrib.files import upload_template
from satellite import *


def start():
    sudo('service uwsgi %s %s' % ('start', settings.fabric.user))


def stop():
    sudo('service uwsgi %s %s' % ('stop', settings.fabric.user))


def reload():
    sudo('service uwsgi %s %s' % ('reload', settings.fabric.user))


def configure():
    conf = settings.nginx
    remote_locate = '/etc/uwsgi/apps-enabled/%s.ini' % settings.fabric.user
    use_sudo(upload_template, 'uwsgi/app.ini.jinja2', remote_locate, conf, template_dir=get_template_dir(), use_jinja=True)