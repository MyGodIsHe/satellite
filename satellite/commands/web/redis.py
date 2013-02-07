from satellite.utils import *


def install():
    sudo('apt-get install redis-server')

def service(action='start'):
    sudo('service redis-server %s' % action)