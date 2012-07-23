# -*- coding: utf-8 -*-
from __spork__ import JS

def match(pattern, string):
    pattern = '^' + pattern
    r = JS('new RegExp(pattern)')
    return True if r.test(string) else None

def search(pattern, string):
    r = JS('new RegExp(pattern)')
    return True if r.test(string) else None

def split(pattern, s, maxsplit=0):
    if not pattern:
        return [s]
    if maxsplit:
        JS('''
var r = new RegExp(pattern, 'g');
var arr;
var result = [];
var idx = 0;
while ((arr = r.exec(s)) != null)
{
  result.push(s.slice(idx, arr.index));
  idx = r.lastIndex;
  maxsplit --;
  if (maxsplit == 0) {
    break;
  }
}
result.push(s.slice(idx, s.length));
return __builtin__.list(result);
        ''')
    else:
        return list(JS('s.__split(new RegExp(pattern))'))
