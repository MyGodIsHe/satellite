import os

import configparser
from fabric.main import load_fabfile, _task_names
from fabric.operations import run
from fabric.context_managers import settings as fabric_settings
from fabric.utils import _AttributeDict, abort

import satellite



__all__ = ['sudo', 'use_sudo', 'get_template', 'get_template_dir',
           'load_settings', 'settings', 'parser', 'render_jinja2',
           'get_dir_list', 'get_task_list', 'check_equal', 'command_exists']


def get_dir_list(path):
    modules = []
    for name in os.listdir(path):
        if not os.path.isdir(os.path.join(path, name)):
            if not name.endswith('.py') or name.startswith('.') or name.startswith('_'):
                continue
            name = name[:-3]
        modules.append(name)
    return modules

def command_exists(parts):
    if len(parts) <= 1:
        return
    return parts[-1] in get_task_list(parts[:-1])

def get_task_list(parts):
    fabfile = '%s.py' % os.path.join(satellite.commands.__path__[0], *parts)
    if not os.path.exists(fabfile):
        return []
    docstring, callables, default = load_fabfile(fabfile)
    callables = dict((k, v) for k, v in callables.iteritems() if v.__module__ == parts[-1])
    return _task_names(callables)

def check_equal(lst):
    return not lst or [lst[0]]*len(lst) == lst

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

settings = _AttributeDict({
    'fabric': _AttributeDict(),
})