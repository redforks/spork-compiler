# -*- coding: utf-8 -*-
from __spork__ import JS
from sys import platform

if platform in ('mozilla', 'opera'):
    from hal_generic import *
elif platform == 'ie':
    from hal_ie import *
else:
    raise NotImplementedError('%s not supported' % platform)

def new_js_arr():
    return JS('[]')

def new_js_obj():
    return JS('{}')
