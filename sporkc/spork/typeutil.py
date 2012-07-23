__all__ = 'get_modules_of_package', 'publicdir', 'class_for_name', 'fullname'

import sys
from os import walk, path

from . import SporkError

def __getmodules(prefix, files):
    ispackage = False
    result = set()
    for base, ext in (path.splitext(f) for f in files):
        if ext not in ('.py', '.pyc', '.pyo'):
            continue
        if base.startswith('_'):
            if base == '__init__':
                ispackage = True
        else:
            result.add(prefix + base)
    if not ispackage:
        result.clear()
    return result

def get_modules_of_package(pkgname):
    ''' return all module names of package pkgname'''
    result = set()
    for sdir in set(sys.path):
        sdir = path.abspath(sdir)
        for p, _, files in walk(path.join(sdir, pkgname)):
            prefix = p[len(sdir) + 1:].replace('/', '.') + '.'
            result |= __getmodules(prefix, files)

    return result

def my_import(module_name):
    ''' import module or package module

    __import__('a.b') returns the package module not the real module object:
        __import__('a.b') # returns a, not a.b
    my_import('a.b') # return a.b    
    '''
    m = __import__(module_name)
    return reduce(getattr, module_name.split('.')[1:], m)

def load_modules_of_package(pkgname):
    return (__import__(mname, level = -1, fromlist = mname) for \
        mname in get_modules_of_package(pkgname))

def publicdir(symbol):
    ''' a public dir()

    builtin dir() function list all attributes of symbol
    publicdir only list public attributes:
      1. if __all__ is defined, return __all__
      2. or remove all private (i.e. "_" prefixed) attributes
    '''
    return (getattr(symbol, '__all__', None) or 
            (x for x in dir(symbol) if not x.startswith('_')))

def class_for_name(name):
    pos = name.rindex('.')
    mname = name[:pos]
    cname = name[pos + 1:]
    m = sys.modules.get(mname)
    result = getattr(m, cname)
    if not isinstance(result, type):
        raise SporkError(_('%s is not type.') % name)
    return result

def fullname(cls):
    return '.'.join((cls.__module__, cls.__name__))
