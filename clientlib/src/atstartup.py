# -*- coding: utf-8 -*-
'''
like atexit, functions registered will run at startup. 
'''
from __spork__ import JS
from hal import jquery
import sys

__funcs = []
def register(func):
    __funcs.append(func)

def _trigger(event=None):
    def browser_not_support():
        return sys.platform == 'ie'

    if browser_not_support():
        jquery('body').append('<p>对不起，运行本程序需要 chrome 插件</p>')
        return

    __funcs.reverse()
    while __funcs:
        try:
            __funcs.pop()()
        except Exception as e:
            msg = str(e)
            JS('alert(msg);')
            raise e

def _reset():
    del __funcs[:]

JS('$($m._trigger);')
