# -*- coding: utf-8 -*-
'''
like atexit, functions registered will run at startup. 
'''
from __spork__ import JS
import sys

__funcs = []
def register(func):
    __funcs.append(func)

def _trigger(event=None):
    __funcs.reverse()
    while __funcs:
        __funcs.pop()()

def _reset():
    del __funcs[:]

JS('$($m._trigger);')
