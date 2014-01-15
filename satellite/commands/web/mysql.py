from tempfile import mktemp
from fabric.operations import run, get, local

from satellite import *


def install():
    sudo('apt-get install mysql-server libmysqlclient-dev')

def create_db(db=None):
    if db is None:
        db = settings.mysql.db
    run("mysql -u root -e 'CREATE DATABASE %s CHARACTER SET utf8'" % db)

def service(action='start'):
    sudo('service mysql %s' % action)

def clone_db():
    db_name = settings.mysql.db
    remote_name = mktemp('.sql')
    run('mysqldump -u root %s > %s' % (db_name, remote_name))
    local_name = mktemp('.sql')
    get(remote_name, local_name)
    run('rm %s' % remote_name)
    local("mysql -u root -e 'DROP DATABASE IF EXISTS %s'" % db_name)
    local("mysql -u root -e 'CREATE DATABASE %s CHARACTER SET utf8'" % db_name)
    local('mysql -u root %s < %s' % (db_name, local_name))
    local('rm %s' % local_name)