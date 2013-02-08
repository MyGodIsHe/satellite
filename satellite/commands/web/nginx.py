from fabric.contrib.files import upload_template
from satellite import *


def install():
    sudo('apt-get install nginx')

def configure():
    conf = settings.nginx
    remote_locate = '/etc/nginx/conf.d/%s.conf' % conf.conf_name
    use_sudo(upload_template, 'nginx/fcgi.conf.jinja2', remote_locate, dict(
        port=conf.port,
        server_name=conf.server_name,
        public_dir=conf.public_dir,
        static_dirs=conf.static_dirs.split(),
        fcgi_uri=conf.fcgi_uri,
        error_page=conf.error_page,
    ), template_dir=get_template_dir(), use_jinja=True)

def service(action='start'):
    sudo('service nginx %s' % action)