# -*- coding: utf-8 -*-
from hal_generic import do_print as _do_print
from hal_generic import *
from hal_generic import __all__

def do_print(s):
    _do_print(s.py_replace('\n', '\r\n'))

