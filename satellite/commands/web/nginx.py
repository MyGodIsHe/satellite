from fabric.api import env

from satellite.utils import *


def install():
    sudo('apt-get install nginx')

def configure():
    remote_locate = '/etc/nginx/conf.d/%s.conf' % env.NGINX_SERVER_NAME
    sudo_upload_template('nginx/fcgi.conf.jinja2', remote_locate, dict(
        port=env.NGINX_PORT,
        server_name=env.NGINX_SERVER_NAME,
        public_dir=env.PUBLIC_DIR,
        static_dirs=env.NGINX_STATIC_DIRS.split(),
        fcgi_uri=env.NGINX_FCGI_URI,
        error_page=env.NGINX_ERROR_PAGE,
    ), template_dir=get_template_dir(), use_jinja=True)

def service(action='start'):
    sudo('service nginx %s' % action)