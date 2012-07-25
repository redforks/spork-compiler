#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys, os.path

from jsmin import jsmin
def get_min_filename(path):
    f, ext = os.path.splitext(path)
    if ext == '.js':
        return f + '.min.js'
    raise ValueError("'{}' is not javascript file".format(path))

def convert(f):
    outf = get_min_filename(f)
    with open(f) as src, open(outf, 'wt') as dst:
        js = src.read()
        js = jsmin(js)
        dst.write(js)

for f in sys.argv[1:]:
    convert(f)
