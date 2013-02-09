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

def check_equal(lst):
    return not lst or [lst[0]]*len(lst) == lst

def run():
    cwords = os.environ['COMP_WORDS'].split()
    cline = os.environ['COMP_LINE']
    cpoint = int(os.environ['COMP_POINT'])
    cword = int(os.environ['COMP_CWORD'])
    SEP = '.'

    full_path = cwords[cword] if len(cwords) > cword else ''
    parts = full_path.split(SEP)
    head = parts[:-1]
    complete = parts[-1]
    module_path = os.path.join(satellite.commands.__path__[0], *head)

    is_task = False
    if os.path.isdir(module_path):
        variants = get_dir_list(module_path)
    else:
        variants = get_task_list(parts)
        is_task = True

    variants = [name
                for name in variants
                if name.startswith(complete)]
    ln = len(variants)
    if ln > 1:
        start = len(complete)
        i = start
        error = False
        try:
            while check_equal([v[i] for v in variants]):
                i += 1
        except IndexError:
            error = True
        if i != start or error:
            print ' '.join(SEP.join(head + [i]) for i in variants)
        else:
            print ' '.join(variants)
    elif ln == 1:
        result = SEP.join(head + variants)
        tail = SEP
        if full_path and is_task:
            if full_path == result:
                return
            tail = ''
        print result + tail