# -*- coding: utf-8 -*-
from __future__ import absolute_import

import __builtin__
from __builtin__ import open as _sys_open
import os, errno, sys, stat as sys_stat

from . import SporkError, add_cleanup_step
import spork.memory_fs as memfs

'''
Virtual file system is a stacked file system on physic file system, 
any changes are stored in memory. 

After calling function `hack()`, `virtual_fs` will steal fowling
system symbols:
    * open
    * os.access
    * os.chdir
    * os.getcwd
    * os.getcwdu
    * os.listdir
    * os.mkdir
    * os.open
    * os.remove
    * os.rmdir
    * os.stat
    * os.tmpfile
    * os.unlink
    * os.utime
    * os.rename
    * os.chmod

Almost all system file operation is based on these *low level* file operation,
so other *high level* file operation will be stolen either.

After calling `restore()`, `virtual_fs` restore stolen symbols.
'''
def _cp_attr(attrname, src, dst):
    val = getattr(src, attrname)
    setattr(dst, attrname, val)

def path_split(path):
    head, tail = os.path.split(path)
    if not tail:
        head, tail = os.path.split(head)
    return head, tail

class OSRawSymbols(object):
    _names = 'access', 'chdir', 'getcwd', 'getcwdu',\
        'mkdir', 'remove', 'rmdir', 'stat', 'unlink', 'rename',\
        'tmpfile', 'listdir', 'utime', 'chmod'

    def __init__(self):
        super(OSRawSymbols, self).__init__()
        def backup_func(name):
            _cp_attr(name, os, self)
        map(backup_func, self._names)

    def restore(self):
        def restore_func(name):
            _cp_attr(name, self, os)
        map(restore_func, self._names)

    def hack(self):
        def hack_func(name):
            func = globals()[name]
            setattr(os, name, func)
        map(hack_func, self._names)

class DeletedPaths(object):
    def __init__(self):
        self.__deleted = set()

    def clear(self):
        self.__deleted.clear()

    def add(self, path):
        path = os.path.abspath(path)
        self.__deleted.add(path)

    def is_fake_deleted(self, path):
        path = os.path.abspath(path)
        return path in self.__deleted

raw_os = OSRawSymbols()
_deleted_paths = DeletedPaths()
del OSRawSymbols, DeletedPaths

def _phy_path_exist(path):
    if _deleted_paths.is_fake_deleted(path):
        return False
    return raw_os.access(path, os.F_OK)

def _phy_is_dir(path):
    try:
        st = raw_os.stat(path)
    except OSError:
        return False
    else:
        return sys_stat.S_ISDIR(st.st_mode)

def _valid_dir_exist(path):
    if _path_in_memfs(path):
        _get_memfs_directory(path)
    else:
        _valid_phy_dir_exist(path)

def _path_in_memfs(path):
    return _safe_get_memfs_entry(path) is not None

def _mem_open(name, mode):
    dir, filename = os.path.split(name)
    dir_entry = _get_phy_mem_directory(dir)
    return dir_entry.open_file(filename, mode)

def oserror_to_ioerror(e):
    result = IOError(e.errno, e.path)
    result.strerror = e.strerror
    result.args = e.args
    return result

def open(name, mode='rt', buffering=-1):
    try:
        if isinstance(mode, basestring) and \
                (memfs.is_writable_mode(mode) or _path_in_memfs(name)):
            if _phy_path_exist(name) and not _path_in_memfs(name):
                _map_phy_file_to_mem(name)
            return _mem_open(name, mode)
        else:
            return _sys_open(name, mode, buffering)
    except OSError as e:
        raise oserror_to_ioerror(e)

def access(path, mode):
    if _path_in_memfs(path):
        return True
    else:
        return _phy_path_exist(path)

def chdir(path):
    _valid_dir_exist(path)
    getcwd.curcwd = path

def getcwd():
    result = getcwd.curcwd
    if result is None:
        result = raw_os.getcwd()
        _get_phy_mem_directory(result)
    return result

def getcwdu():
    return unicode(getcwd(), sys.getfilesystemencoding())

def _valid_phy_dir_exist(path):
    if not _phy_path_exist(path):
        raise memfs.errors.path_not_exist(path)
    if not _phy_is_dir(path):
        raise memfs.errors.not_a_directory(path)

def _get_phy_mem_directory(path):
    if _path_in_memfs(path):
        return _get_memfs_directory(path)

    path = os.path.abspath(path)
    head, tail = path_split(path)
    if not tail:
        return _memfs_root

    _valid_phy_dir_exist(path)
    dir = _get_phy_mem_directory(head)
    result = dir.safe_get_path(tail)
    return result or dir.new_directory(path, tail)

import shutil
def _map_phy_file_to_mem(path):
    def create_fill_mem_file(path):
        srcfile = open(path, 'r')
        dstfile = _mem_open(path, 'w')
        shutil.copyfileobj(srcfile, dstfile)
        srcfile.close()
        dstfile.close()

    head, tail = path_split(path)
    parent_dir = _get_phy_mem_directory(head)
    create_fill_mem_file(path)

def _get_memfs_directory(path):
    path = os.path.abspath(path)
    return _memfs_root.get_as_directory(path)

def _safe_get_memfs_entry(path):
    path = os.path.abspath(path)
    return _memfs_root.safe_get_path(path)

def _get_memfs_entry(path):
    path = os.path.abspath(path)
    return _memfs_root.get_path(path)

def mkdir(path, mode=0777):
    head, tail = path_split(path)

    dir = _get_phy_mem_directory(head)
    dir.new_directory(path, tail)

def stat(path):
    def _get_mem_stat(path):
        entry = _get_memfs_entry(path)
        return entry.stat()

    def _get_phy_stat(path):
        if not _phy_path_exist(path):
            raise memfs.errors.path_not_exist(path)
        return raw_os.stat(path)

    if _path_in_memfs(path):
        return _get_mem_stat(path)
    else:
        return _get_phy_stat(path)

class Remove(object):
    def do_remove_mem(self, parent_dir, path, tail):
        parent_dir.remove_file(path, tail)

    def remove_mem(self, path):
        head, tail = os.path.split(path)
        parent_dir = _get_memfs_directory(head)
        self.do_remove_mem(parent_dir, path, tail)
        _deleted_paths.add(path)

    def remove_phy(self, path):
        _deleted_paths.add(path)

    def __call__(self, path):
        if _path_in_memfs(path):
            self.remove_mem(path)
        elif _phy_path_exist(path):
            self.remove_phy(path)
        else:
            raise memfs.errors.path_not_exist(path)

class Rmdir(Remove):
    def do_remove_mem(self, parent_dir, path, tail):
        parent_dir.remove_directory(path, tail)

    def __call__(self, path):
        def cur_dir_not_allowed(path):
            if path == '.':
                raise memfs.errors.invalid_argument(path)

        def root_dir_not_allowed(path):
            if path == '/':
                raise memfs.errors.busy(path)

        cur_dir_not_allowed(path)
        root_dir_not_allowed(path)

        if listdir(path):
            raise memfs.errors.not_empty(path)
        super(Rmdir, self).__call__(path)

unlink = remove = Remove()
rmdir = Rmdir()
del Remove

def tmpfile():
    return raw_os.tmpfile()

def listdir(path):
    dir_entry = _get_phy_mem_directory(path)
    result = dir_entry.listdir()
    if _phy_path_exist(path):
        result.extend(raw_os.listdir(path))
    return result

def utime(path, times):
    entry = _get_memfs_entry(path)
    entry.utime(times)

def rename(old, new):
    def mem_rename(old, new):
        old_head, old_tail = path_split(old)
        new_head, new_tail = path_split(new)
        parent_dir = _get_memfs_directory(old_head)
        new_dir = _get_memfs_directory(new_head)

        parent_dir.rename(old_tail, new_dir, new_tail)

    def phy_rename(old, new):
        if os.path.isfile(old):
            _map_phy_file_to_mem(old)
            mem_rename(old, new)
            _deleted_paths.add(old)
        elif os.path.isdir(old):
            raise NotImplementedError('rename phy directory is not support')
        else:
            raise memfs.errors.path_not_exist(old)

    if os.path.isdir(new):
        raise memfs.errors.is_a_directory(new)
    if os.path.isdir(old) and os.path.isfile(new):
        raise memfs.errors.not_a_directory(new)

    if _path_in_memfs(old):
        mem_rename(old, new)
    else:
        phy_rename(old, new)

def chmod(path, mode):
    pass

def is_hacked():
    return __builtin__.open is open

def hack():
    if is_hacked():
        raise SporkError('do not call hack() twice.')

    add_cleanup_step(restore)

    __builtin__.open = open
    raw_os.hack()
    _recreate_mem_fs()

def restore():
    __builtin__.open = _sys_open
    raw_os.restore()

def _recreate_mem_fs():
    global _memfs_root, _deleted_paths
    _memfs_root = memfs.MemFSDirectory('')
    _deleted_paths.clear()
    getcwd.curcwd = None
_recreate_mem_fs()

