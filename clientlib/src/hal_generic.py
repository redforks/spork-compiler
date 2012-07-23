# -*- coding: utf-8 -*-
from __spork__ import JS

__all__ = 'document', 'do_print', 'window', 'jquery', 'css_set_box_flex', \
    'session_storage'

document = JS('document')
window = JS('window')
jquery = JS('$')
session_storage = JS('sessionStorage')

def set_argv():
    s = JS('window.location.search.substring(1)')
    s = s.py_split('&')
    argv = []
    argv.append(JS('window.location.pathname'))
    for item in s:
        if item:
            argv.append(JS('unescape(item)'))

    import sys
    sys.argv = argv

set_argv()
del set_argv

def do_print(s):
    if do_print.console is None:
        console = document.getElementById('__console__')
        if console is None:
            return
        if console.childNodes.length == 0:
            text = document.createTextNode('')
            console.appendChild(text)
        console = console.childNodes.item(0)
        do_print.console = console

    do_print.line_cache += s
    s = do_print.line_cache
    if '\n' in s or len(s) > 10:
        do_print.console.appendData(s)
        do_print.line_cache = ''

do_print.line_cache = ''
do_print.console = None

def css_set_box_flex(dom, flex):
    dom.style.webkitBoxFlex = flex
    dom.style.MozBoxFlex = flex
    dom.style.boxFLex = flex
