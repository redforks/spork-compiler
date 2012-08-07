# -*- coding: utf-8 -*-
from __spork__ import JS
__all__ = 'log', 'debug', 'info', 'warning', 'error'

if JS('!console'):
    def log(msg):
        pass

    debug = info = warning = error = log
else:
    def log(msg):
        JS('console.log(msg);')

    def info(msg):
        JS('console.info(msg);')

    def warning(msg):
        JS('console.warn(msg);')

    def error(msg):
        JS('console.error(msg);')

    def debug(msg):
        JS('console.debug(msg);')
