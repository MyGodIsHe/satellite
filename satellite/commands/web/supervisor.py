from StringIO import StringIO
from fabric.operations import put
from satellite import *


def install():
    sudo('apt-get install supervisor')

def configure():
    groups = {}
    for k, conf in settings.iteritems():
        if k.startswith('supervisor:'):
            group, name = k.split(':')[1:]
            if group not in groups:
                groups[group] = {}
            groups[group][name] = conf

    template_dir = get_template_dir()
    for group, confs in groups.iteritems():
        renders = []
        programs = []
        for name, conf in confs.iteritems():
            programs.append(name)
            renders.append(render_jinja2('supervisor/%s.jinja2' % name, conf, template_dir))

        group_render = [
            '[group:%s]' % group,
            'programs = %s' % ','.join(programs)
        ]
        renders.append('\n'.join(group_render))

        remote_locate = '/etc/supervisor/conf.d/%s.conf' % group
        use_sudo(put, StringIO('\n\n'.join(renders)), remote_locate)

def service(action='start'):
    sudo('service supervisor %s' % action)

def status():
    sudo('supervisorctl status')

def ctl(program, action):
    sudo('supervisorctl %s %s:%s' % (action, settings.supervisor.default_group, program))

def ctl_group(group, program, action):
    sudo('supervisorctl %s %s:%s' % (action, group, program))