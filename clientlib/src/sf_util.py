# -*- coding: utf-8 -*-

def is_seq(o):
    ''' return True if o is sequence, i.e. has __iter__() method. '''
    return hasattr(o, '__iter__')
