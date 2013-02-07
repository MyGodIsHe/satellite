from fabric.operations import run

from satellite.utils import *


def install():
    sudo('apt-get install mysql-server libmysqlclient-dev')

def create_db(db):
    run("mysql -u root -e 'CREATE DATABASE %s CHARACTER SET utf8'" % db)

def service(action='start'):
    sudo('service mysql %s' % action)