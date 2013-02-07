#!/usr/bin/env python

from setuptools import setup, find_packages

from fabric.version import get_version


setup(
    name='Satellite',
    version=get_version('short'),
    description='Deployment tool based on fabric.',
    author='Ilya Chistyakov',
    author_email='ilchistyakov@gmail.com',
    packages=find_packages(),
    install_requires=['Fabric==1.5.3'],
    entry_points={
        'console_scripts': [
            'satellite = satellite.main:main',
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