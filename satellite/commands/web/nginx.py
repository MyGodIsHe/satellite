from fabric.contrib.files import upload_template
from satellite import *


def install():
    sudo('apt-get install nginx')

def configure():
    conf = settings.nginx
    remote_locate = '/etc/nginx/conf.d/%s.conf' % conf.conf_name
    if isinstance(conf.static_dirs, (str, unicode)):
        conf.static_dirs = conf.static_dirs.split()
    use_sudo(upload_template, 'nginx/%s.conf.jinja2' % conf.interface, remote_locate, conf, template_dir=get_template_dir(), use_jinja=True)

def service(action='start'):
    sudo('service nginx %s' % action)
