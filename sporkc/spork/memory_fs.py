# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os, errno, time
from StringIO import StringIO as _StringIO
from functional import partial
from ._mem_fs import Entry
from .internal import constf

def _create_os_error(errno, path):
    result = OSError(errno, path)
    result.errno = errno
    result.strerror = os.strerror(errno)
    result.path = path
    result.args = (errno, result.strerror, path)
    return result

class errors(object):
    not_a_directory = partial(_create_os_error, errno.ENOTDIR)
    path_exist = partial(_create_os_error, errno.EEXIST)
    path_not_exist = partial(_create_os_error, errno.ENOENT)
    is_a_directory = partial(_create_os_error, errno.EISDIR)
    invalid_argument = partial(_create_os_error, errno.EINVAL)
    not_empty = partial(_create_os_error, errno.ENOTEMPTY)
    busy = partial(_create_os_error, errno.EBUSY)

class StringIO(_StringIO):
    is_append_mode = disable_write = disable_read = False

    def __init__(self, file_entry):
        _StringIO.__init__(self, file_entry.data)
        self._file_entry = file_entry

    def _save_back(self):
        def update_mtime():
            if not self.disable_write:
                self._file_entry._stat.st_mtime = time.time()

        def update_atime():
            self._file_entry._stat.st_atime = time.time()

        if not self.closed:
            self._file_entry.data = self.getvalue()

            update_mtime()
            update_atime()

    def close(self):
        self._save_back()
        _StringIO.close(self)

    def __del__(self):
        self._save_back()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()

    def write(self, s):
        def check_diable_write():
            if self.disable_write:
                raise IOError('File not open for writing')
        
        check_diable_write()
        if self.is_append_mode:
            self.seek(0, 2)
        _StringIO.write(self, s)

    def check_disable_read(self):
        if self.disable_read:
            raise IOError('File not open for reading')

    def read(self, size=-1):
        self.check_disable_read()
        return _StringIO.read(self, size)

    def readline(self, length=None):
        self.check_disable_read()
        return _StringIO.readline(self, length)
        
import stat as _stat
class StatStruct(object):
    __last_ino = 0
    _attrs = {
        'st_mode': _stat.ST_MODE,
        'st_ino': _stat.ST_INO,
        'st_dev': _stat.ST_DEV,
        'st_nlink': _stat.ST_NLINK,
        'st_uid': _stat.ST_UID,
        'st_gid': _stat.ST_GID,
        'st_size': _stat.ST_SIZE,
        'st_atime': _stat.ST_ATIME,
        'st_mtime': _stat.ST_MTIME,
        'st_ctime': _stat.ST_CTIME
    }

    def __init__(self):
        self._data = [0] * len(self._attrs)
        self.st_ino = StatStruct.__new_ino()
        self.st_atime = self.st_ctime = self.st_mtime = time.time()

    @staticmethod
    def __new_ino():
        StatStruct.__last_ino += 1
        return StatStruct.__last_ino

    def __getitem__(self, idx):
        return self._data[idx]

    def __getattr__(self, name):
        idx = self._attrs[name]
        return self._data[idx]

    def __setattr__(self, name, value):
        if name in self._attrs:
            idx = self._attrs[name]
            self._data[idx] = value
        else:
            super(StatStruct, self).__setattr__(name, value)

class MemFSEntry(Entry):
    def __init__(self, name, parent=None):
        super(MemFSEntry, self).__init__(name, parent, '', _stat =
                StatStruct())

    @property
    def _stat(self):
        return self.attrs['_stat']

    def stat(self):
        result = self._stat
        result.st_size = len(self.data)
        if self.is_folder():
            result.st_mode = _stat.S_IFDIR
        else:
            result.st_mode = _stat.S_IFREG
        return result

    def utime(self, times):
        if times is None:
            atime = mtime = time.time()
        else:
            atime, mtime = times

        st = self._stat
        st.st_atime = atime
        st.st_mtime = mtime

    def open(self, mode):
        result = StringIO(self)
        if not is_writable_mode(mode):
            result.disable_write = True
        if not is_readable_mode(mode):
            result.disable_read = True
        if is_append_mode(mode):
            result.is_append_mode = True

        if is_write_mode(mode) and not is_read_mode(mode):
            result.truncate()
        if is_append_mode(mode) and not is_update_mode(mode):
            result.seek(0, 2)
        return result

    def __delitem__(self, name):
        entry = self.get_path(name)
        self._remove_child(entry)

    def __contains__(self, name):
        return any(entry.name == name for entry in self)

    def get_as_directory(self, path):
        result = self.get_path(path)
        need_be_directory(result, path)
        return result

    def open_file(self, filename, mode):
        if filename in self:
            file = self.get_path(filename)
        else:
            file = MemFSEntry(filename, self)
        return file.open(mode)

    def new_directory(self, fullpath, dirname):
        if dirname in self:
            raise errors.path_exist(fullpath)

        return MemFSDirectory(dirname, self)

    def remove_file(self, fullpath, filename):
        f = self.get_path(filename)
        need_be_file(f, fullpath)
        del self[filename]

    def remove_directory(self, fullpath, dirname):
        dir = self.get_path(dirname)
        need_be_directory(dir, fullpath)
        del self[dirname]

    def listdir(self):
        return [x.name for x in self]

    def rename(self, old_name, new_dir_entry, new_name):
        entry = self.get_path(old_name)
        self._remove_child(entry)
        entry.name = new_name
        if new_name in new_dir_entry:
            del new_dir_entry[new_name]
        new_dir_entry._add_child(entry)

class MemFSDirectory(MemFSEntry):
    is_folder = constf(True)

def need_be_directory(entry, path):
    if not entry.is_folder():
        raise errors.not_a_directory(path)

def need_be_file(entry, path):
    if not is_file(entry):
        raise errors.is_a_directory(path)

def is_file(entry):
    return not entry.is_folder()

def is_read_mode(mode):
    return 'r' in mode

def is_readable_mode(mode):
    return is_read_mode(mode) or is_update_mode(mode)

def is_write_mode(mode):
    return 'w' in mode

def is_writable_mode(mode):
    return 'w' in mode or '+' in mode or 'a' in mode

def is_update_mode(mode):
    return '+' in mode

def is_append_mode(mode):
    return mode.startswith('a')

