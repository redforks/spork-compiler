# -*- coding: utf-8 -*-

import os
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

def change_ext(path, ext):
    ''' change path's ext to new ext 
        
        ext should start with '.'
    '''
    return os.path.splitext(path)[0] + ext

def read_file(filename):
    ''' read file content as string. '''
    return open(filename).read()

def write_file(filename, content):
    ''' write text content to file. '''
    open(filename, 'wt').write(content)

def touch(filename):
    if not os.path.exists(filename):
        write_file(filename, '')
    else:
        os.utime(filename, None)

class NullStream(object):
    __slots__ = ('closed')
    def __init__(self):
        self.closed = False

    def __check_closed(self, arg1 = None):
        if self.closed:
            raise ValueError(_('NullStream is closed'))
        
    write = __check_closed
    writelines = __check_closed
    flush = __check_closed
    
    def close(self):
        self.closed = True

    def __exit__(self, errorcls, error, trace):
        self.close()
        return False

    def __enter__(self):
        return self

    def __iter__(self):
        return self

    xreadlines = __iter__

    def next(self):
        raise StopIteration

    def read(self, size = None):
        self.__check_closed()
        return ''

    readline = read

    def readlines(self, size = None):
        self.__check_closed()
        return []

    def tell(self):
        self.__check_closed()
        return 0

    def seek(self, offset, whence = 0):
        self.__check_closed()

    def truncate(self, size = None):
        self.__check_closed()

class IOUtil(object):
    def __init__(self, rootdir):
        super(IOUtil, self).__init__()
        self.__rootdir = rootdir

    def _translate_path(self, path):
        return os.path.join(self.__rootdir, path)

    def open_write(self, path):
        path = self._translate_path(path)
        try:
            return open(path, 'wt')
        except IOError:
            os.makedirs(os.path.dirname(path))
            return open(path, 'wt')

    def open_read(self, path):
        path = self._translate_path(path)
        return open(path, 'rt')

    def exist(self, path):
        path = self._translate_path(path)
        return os.path.exists(path)

def get_str_from_writer(writer):
    ''' writer: foo(file) like function

        call the writer function, return the content the writer writes.
    '''
    stream = StringIO()
    writer(stream)
    return stream.getvalue()
