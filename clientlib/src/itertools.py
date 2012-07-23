# -*- coding: utf-8 -*-
from __spork__ import JS

class _chain(object):
    def __init__(self, iterables):
        self.iters = iter(iterables)
        self.cur_iter = None

    def __iter__(self):
        return self

    def next(self):
        while True:
            if self.cur_iter is None:
                self.cur_iter = iter(self.iters.next())

            JS('try {')
            return self.cur_iter.next()
            JS('''} catch(e) {
                if (e.__name__ !== 'StopIteration') {
                    throw e;
                }
            ''')
            self.cur_iter = None
            JS('}')

def chain(*iterables):
    return _chain(iterables)

def from_iterable(iterables):
    return _chain(iterables)

chain.from_iterable = from_iterable
del from_iterable
