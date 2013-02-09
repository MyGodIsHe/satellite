import os
from satellite import get_dir_list, get_task_list

import satellite.commands


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
        variants = get_task_list(head)
        is_task = True

    variants = [name
                for name in variants
                if name.startswith(complete)]
    ln = len(variants)
    if ln > 1:
        if len(complete):
            variants = (SEP.join(head + [i]) for i in variants)
        print ' '.join(variants)
    elif ln == 1:
        result = SEP.join(head + variants)
        tail = SEP
        if full_path and is_task:
            if full_path == result:
                return
            tail = ''
        print result + tail