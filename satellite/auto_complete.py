import os

from fabric.main import load_fabfile,  _task_names


import satellite.commands


def get_dir_list(path):
    modules = []
    for name in os.listdir(path):
        if not os.path.isdir(os.path.join(path, name)):
            if not name.endswith('.py') or name.startswith('.') or name.startswith('_'):
                continue
            name = name[:-3]
        modules.append(name)
    return modules

def get_task_list(parts):
    fabfile = '%s.py' % os.path.join(satellite.commands.__path__[0], *parts[:-1])
    if not os.path.exists(fabfile):
        return []
    docstring, callables, default = load_fabfile(fabfile)
    callables = dict((k, v) for k, v in callables.iteritems() if v.__module__ == parts[-2])
    return _task_names(callables)

def run():
    cwords = os.environ['COMP_WORDS'].split()
    cline = os.environ['COMP_LINE']
    cpoint = int(os.environ['COMP_POINT'])
    cword = int(os.environ['COMP_CWORD'])
    SEP = '.'

    full_path = cline[cline.rfind(' ', 0, cpoint)+1:]
    i = full_path.find(' ')
    if i != -1:
        full_path = full_path[:i]
    parts = full_path.split(SEP)
    module_path = os.path.join(satellite.commands.__path__[0], *parts[:-1])
    complete = parts[-1]

    is_task = False
    if os.path.isdir(module_path):
        modules = get_dir_list(module_path)
    else:
        modules = get_task_list(parts)
        is_task = True

    modules = [name
               for name in modules
               if name.startswith(complete)]
    ln = len(modules)
    if ln > 1:
        print ' '.join(modules)
    elif ln == 1:
        result = modules[0]
        tail = SEP
        if full_path and is_task:
            if full_path == result:
                return
            tail = ''
        print result + tail