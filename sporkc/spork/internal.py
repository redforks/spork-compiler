# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
from functools import partial
import operator
from collections import Container, Mapping, Iterable

from os import environ
# set _test to true to set test mode
_test = bool(int(environ.get('UNITTEST', '0')))
del environ

logger = logging.getLogger('spork')
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(levelname)s - %(process)d - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
del formatter, console_handler

__cleanup_steps = []

def _cleanup_for_test():
    error = None
    while __cleanup_steps:
        try:
            __cleanup_steps.pop()()
        except Exception as e:
            if not error:
                error = e
    if error:
        raise error

def add_cleanup_step(step):
    if _test:
        __cleanup_steps.append(step)

def nonef(*x):
    #NOTE: use C extension 
    return None

def constf(val):
    #NOTE: use C extension 
    return lambda *x: val

class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kargs)
        return cls._instance

class ReadOnlyMixin(object):
    def __setattr__(self, name, value):
        if not hasattr(self, name):
            super(ReadOnlyMixin, self).__setattr__(name, value)
        else:
            raise AttributeError('object is readonly.')

class EqStrMixin(object):
    def __eq__(self, other):
        if not issubclass(type(other), type(self)):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '<' + type(self).__name__ + str(vars(self)) + '>'

    __repr__ = __str__

from weakref import WeakValueDictionary

class InstanceCacheMixin(ReadOnlyMixin):
    _instance_store = None
    def __new__(cls, *args):
        if cls._instance_store is None:
            cls._instance_store = WeakValueDictionary()

        if args in cls._instance_store:
            return cls._instance_store[args]
        result = cls._instance_store[args] = \
                super(InstanceCacheMixin, cls).__new__(cls)
        return result

class StaticClass(object):
    def __init__(self):
        raise SporkError(_('do not create %s instance') % type(self))

class BitAccess(object):
    __slots__ = 'mask', 'store'

    def __init__(self, pos, store = '_bits'):
        self.mask = 1 << pos
        self.store = store

    def __get__(self, obj, objtype=None):
        bits = getattr(obj, self.store, 0)
        return bits & self.mask != 0

    def __set__(self, obj, value):
        bits = getattr(obj, self.store, 0)
        if value:
            bits |= self.mask
        else:
            bits &= ~self.mask
        setattr(obj, self.store, bits)

class ModificationCheckerMixin(object):
    _modifiable_attrs = ()

    def __init__(self):
        super(ModificationCheckerMixin, self).__init__()
        self._modified = False

    def __setattr__(self, name, val):
        ''' mark _modified '''
        super(ModificationCheckerMixin, self).__setattr__('_modified', True)
        super(ModificationCheckerMixin, self).__setattr__(name, val)

    def _end_update(self):
        self._modified = False
        for attr in self._modifiable_attrs:
            getattr(self, attr)._end_update()

    def modified(self):
        if self._modified:
            return True

        for attr in self._modifiable_attrs:
            val = getattr(self, attr)
            modified = getattr(val, 'modified', None)
            if modified is not None:
                if modified():
                    return True
        return False
