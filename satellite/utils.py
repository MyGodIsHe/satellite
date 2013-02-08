import os

import configparser
from fabric.operations import run
from fabric.context_managers import settings as fabric_settings
from fabric.utils import _AttributeDict, abort

import satellite



__all__ = ['sudo', 'use_sudo', 'get_template', 'get_template_dir',
           'load_settings', 'settings', 'parser', 'render_jinja2']


# fix for sudo_user
def sudo(command, *args, **kwargs):
    with fabric_settings(user=settings.satellite.sudo_user):
        run("sudo %s" % command, *args, **kwargs)

def use_sudo(f, *args, **kwargs):
    kwargs["use_sudo"] = True
    with fabric_settings(user=settings.satellite.sudo_user):
        f(*args, **kwargs)

def get_template(path):
    return os.path.join(satellite.__path__[0], 'templates', path)


def render_jinja2(filename, context=None, template_dir=None):
    try:
        from jinja2 import Environment, FileSystemLoader
        if not template_dir:
            parts = os.path.split(filename)
            if len(parts) > 1:
                template_dir, filename = parts
        jenv = Environment(loader=FileSystemLoader(template_dir or '.'))
        return jenv.get_template(filename).render(**context or {})
    except ImportError:
        import traceback
        tb = traceback.format_exc()
        abort(tb + "\nUnable to import Jinja2 -- see above.")


def get_template_dir():
    return os.path.join(satellite.__path__[0], 'templates')


parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())

def load_settings(path='satellite.ini'):
    if os.path.exists(path):
        parser.read(path)
        return (
            (name, _AttributeDict(section.iteritems()))
            for name, section in parser.iteritems())
    return {}

settings = _AttributeDict()