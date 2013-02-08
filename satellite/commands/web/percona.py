from fabric.api import run

from satellite import *


def install(ubuntu_version):
    """
    http://www.percona.com/doc/percona-server/5.5/installation/apt_repo.html
    """
    sudo('gpg --keyserver  hkp://keys.gnupg.net --recv-keys 1C4CBDCDCD2EFD2A; gpg -a --export CD2EFD2A | sudo apt-key add -')
    for postfix in ['', '-src']:
        sudo('echo "deb%s http://repo.percona.com/apt %s main" >> sudo /etc/apt/sources.list' % (postfix, ubuntu_version))
    sudo('apt-get update')
    sudo('apt-get install percona-server-server percona-server-client')

def set_engine(*tables, **opts):
    db = settings.mysql.db if 'db' not in opts else opts['db']
    for table in tables:
        run("mysql -u root -e 'ALTER TABLE %s ENGINE=xtradb;' %s" % (table, db))