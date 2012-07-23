#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from glob import glob
from spork.jscompiler import setup

setup(
        name='sporklib', 
        version='0.1.0',
        py_modules=[],
        author='Red Forks',
        author_email='redforks@gmail.com',
        package_dir={'': 'src', 'sftest': 'sftest'},
        packages=['', 'sftest'],
        package_data={
            '': ['*.js', '*.css'], 
            'sftest': ['*.html']
        },
        data_files=[
            ('images', glob('src/images/*'))
        ]
    )
