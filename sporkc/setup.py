#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from setuptools import setup
#from distutils.core import setup

setup(
        name='spork', 
        version='0.1.0',
        py_modules=[],
        author='Red Forks',
        author_email='redforks@gmail.com',
        packages=['spork'],
        requires=['functional', 'cherrypy'],
        #do not know why package name has '-' will fail
        #requires=['functional', 'cherrypy', 'python-memcached', 'mysql-python'],
    )
