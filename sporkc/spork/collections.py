# -*- coding: utf-8 -*-
from __future__ import absolute_import

import collections

__all__ = ()

class OnloadDict(dict):
    def __init__(self, onload):
        ''' create OnloadDict

        onload: function to load value by key, 
            return None if no value correspond to key,
            raise exception when error happend'''
        super(OnloadDict, self).__init__()
        self.__onload = onload

    def __missing__(self, key):
        result = self.__onload(key)
        if not result:
            raise KeyError(key)

        self[key] = result
        return result

    def get(self, key, default = None):
        ''' dict.get() won't call __missing__, so override '''
        try:
            return self[key]
        except KeyError:
            return default

class StrictDict(dict):
    def add(self, key, value):
        oldval = self.setdefault(key, value)
        if oldval is not value:
            raise KeyError(_("key '%s' is already in StrictDict"), key)

def eat(seq):
    #NOTE: use C extension
    for x in seq:
        pass

class LruCache(object):
    def __init__(self, size):
        super(LruCache, self).__init__()
        self.size = size
        self.__dict = collections.OrderedDict()

    def __getitem__(self, key):
        def on_not_found(key):
            raise KeyError(key)
        return self.get(key, on_not_found)

    def __setitem__(self, key, value):
        self.__dict[key] = value
        if len(self) > self.size:
            self.__dict.popitem(False)

    def get(self, key, do_load):
        result = self.__dict.pop(key, None)
        if result is not None:
            self.__dict[key] = result
            return result

        result = self[key] = do_load(key)
        return result

    def __len__(self):
        return len(self.__dict)

    def iteritems(self):
        return self.__dict.iteritems()

def iter_or_singleton(val):
    if val is None:
        return ()
    elif hasattr(val, '__iter__'):
        return iter(val)
    else:
        return (val,)

class OrderedSet(collections.OrderedDict):
    # it is not a real set, but enough for our use
    def __init__(self, iterable=None):
        if iterable:
            super(OrderedSet, self).__init__(((k, None) for k in iterable))
        else:
            super(OrderedSet, self).__init__()

    def add(self, item):
        self[item] = None

    def update(self, iterable):
        super(OrderedSet, self).update(collections.OrderedDict.fromkeys(iterable))
