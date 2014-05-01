#!/usr/bin/env python

import os
import shutil
from setuptools import setup, find_packages


package_name = 'satellite'
data_files = []

for dirpath, dirnames, filenames in os.walk(package_name):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.') or dirname == '__pycache__':
            del dirnames[i]
    if filenames and '__init__.py' not in filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

BASH_COMPLETION_DIR = os.environ.get('BASH_COMPLETION_DIR', '/etc/bash_completion.d/')
if BASH_COMPLETION_DIR:
    shutil.copyfile('autocomplete', os.path.join(BASH_COMPLETION_DIR, package_name))

setup(
    name='Satellite',
    version='0.0.1',
    description='Deployment tool based on fabric.',
    author='Ilya Chistyakov',
    author_email='ilchistyakov@gmail.com',
    packages=find_packages(),
    data_files=data_files,
    install_requires=['Fabric==1.5.3', 'configparser', 'jinja2'],
    entry_points={
        'console_scripts': [
            '%(name)s = %(name)s.main:main' % {'name': package_name},
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Clustering',
        'Topic :: System :: Software Distribution',
        'Topic :: System :: Systems Administration',
        ],
)
