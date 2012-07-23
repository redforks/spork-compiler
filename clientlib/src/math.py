# -*- coding: utf-8 -*-
from __spork__ import JS

''' Return the floor of x as a float

    This is the largest integral value <= x.
'''
floor = JS('Math.floor')

''' Return the ceiling of x as a float.

    This is the smallest integral vale >= x.
'''
ceil = JS('Math.ceil')

# Note all triangle function use radians
cos = JS('Math.cos')
cos = JS('Math.cos')
acos = JS('Math.acos')
asin = JS('Math.asin')
atan = JS('Math.atan')
atan2 = JS('Math.atan2')
exp = JS('Math.exp')

def log(x, base=None):
    if base is not None:
        raise NotImplementedError('log with base is not implemented:')
    return JS('Math.log(x)')

pow = JS('Math.pow')
sqrt = JS('Math.sqrt')
sin = JS('Math.sin')
tan = JS('Math.tan')

e = JS('Math.E')
pi = JS('Math.PI')

def degrees(x):
    ''' Converts angle x from radians to degrees '''
    return x / pi * 180

def radians(x):
    ''' Converts angle x from degrees to radians '''
    return x / 180 * pi
