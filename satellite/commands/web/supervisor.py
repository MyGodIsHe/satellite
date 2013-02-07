from fabric.api import env

from satellite.utils import *


def install():
    sudo('apt-get install supervisor')

def configure():
    conf_locate = '/etc/supervisor/conf.d/eve.conf'
    sudo_upload_template("%s%s" % (env.FABFILE_DIR, conf_locate), conf_locate, dict(
        app_dir=env.APP_DIR,
        venv=env.VENV_DIR,
        user=env.APP_USER,
        sentry_dir=env.SENTRY_DIR,
        log=env.LOG_DIR,
        port=env.APP_PORT,
    ))

def service(action='start'):
    sudo('service supervisor %s' % action)

def status():
    sudo('supervisorctl status')

def ctl(program, action):
    sudo('supervisorctl %s eve:%s' % (action, program))