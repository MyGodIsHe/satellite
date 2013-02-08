=========
Satellite
=========

Satellite is command-line tool for streamlining the use of SSH for application deployment or systems administration tasks based on fabric.

============
Requirements
============

* `Fabric <http://fabfile.org/>`_
* `ConfigParser <http://docs.python.org/library/configparser.html>`_

=============
Settings file
=============

Satellite looks for ``./satellite.ini``.

Example:

.. code-block:: ini

    [main]
    app_name = hello
    root = /home/${app_name}
    root_app = ${root}/www
    root_public = ${root}/public
    root_venv = ${root}/venv
    venv_activate = source ${root_venv}/bin/activate
    root_log = ${root}/log
    root_revisions = ${root}/revisions
    local_settings = ${app_name}/settings/production.py
    remote_settings = ${root_app}/${app_name}/settings/local.py
    app_host = 127.0.0.1
    app_port = 8003

    [fabric]
    host_string = 176.9.220.203
    user = ${main:app_name}

    [satellite]
    sudo_user = elias

    [git]
    repo = git@github.com:NElias/${main:app_name}.git

    [mysql]
    db = ${main:app_name}

    [supervisor]
    default_group = ${main:app_name}

    [supervisor:hello:django.fcgi]
    directory = ${main:root_app}
    user = ${fabric:user}
    virtualenv = ${main:root_venv}
    log = ${main:root_log}
    host = ${main:app_host}
    port = ${main:app_port}

    [nginx]
    conf_name = ${fabric:user}
    server_name = ${main:app_name}.com
    port = 80
    public_dir = ${main:root_public}
    static_dirs = static media
    fcgi_uri = ${main:app_host}:${main:app_port}
    error_page = /static/50x.html

=====
Usage
=====

Next command creates a configuration file for nginx. Go to the folder with settings file, run it:

.. code-block:: bash

    satellite web.nginx.configure


Use auto-completion to navigate the command tree:

.. code-block:: bash

    satellite web.[tab]