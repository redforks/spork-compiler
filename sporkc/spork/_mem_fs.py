# -*- coding: utf-8 -*-
from __future__ import absolute_import

from . import SporkError
from .internal import constf

class Entry(object):
    def __init__(self, name, parent=None, data=None, **attrs):
        self.name = name
        self.child = None
        self.parent = parent
        self.next_sibling = None
        self.data = data
        self.attrs = attrs
        if parent:
            parent._add_child(self)

    def _add_child(self, child):
        name = child.name
        for ch in self:
            if name == ch.name:
                raise SporkError(
                    _("duplicate name '%s' in ert folder '%s'") % \
                    (name, self.fullname))

        child.next_sibling = self.child
        self.child = child

    def _remove_child(self, child):
        if self.child is child:
            self.child = child.next_sibling
        else:
            ch = self.child
            while ch:
                if ch.next_sibling is child:
                    ch.next_sibling = child.next_sibling
                    break
                ch = ch.next_sibling

    def iter_to_root(self):
        p = self
        yield p
        while p.parent:
            p = p.parent
            yield p

    def iter_deep_first(self, fowllow_link = False):
        yield self
        for ch in self:
            for node in ch.iter_deep_first(fowllow_link):
                yield node

    def is_folder(self):
        return self.child is not None

    @property
    def fullname(self):
        buf = [p.name for p in self.iter_to_root()]
        buf.reverse()
        if self.is_folder():
            buf.append('')
        return '/'.join(buf)

    def __str__(self):
        return self.fullname

    def __repr__(self):
        return '<' + self.__class__.__name__ + ' ' + str(self) + '>'

    def get_root(self):
        for p in self.iter_to_root():
            pass
        else:
            return p

    def get_path(self, path):
        first, __, remain = path.partition('/')
        if not first:
            found = self.get_root()
        elif first == '.':
            found = self
        elif first == '..':
            found = self.parent or self
        else:
            for ch in self:
                if ch.name == first:
                    found = ch
                    break
            else:
                raise LookupError(
                        _("path '%s' not found on '%s'") % (path, self))
        if remain:
            return found.get_path(remain)
        else:
            return found

    def path_exist(self, path):
        return self.safe_get_path(path) is not None

    def safe_get_path(self, path, default = None):
        try:
            return self.get_path(path)
        except LookupError:
            return default

    def __iter__(self):
        child = self.child
        while child:
            yield child
            child = child.next_sibling

    def __len__(self):
        result = 0
        for item in self:
            result += 1
        return result

    def __nonzero__(self):
        return True

class Folder(Entry):
    is_folder = constf(True)

class Link(Entry):
    def get_path(self, path):
        return self.target.get_path(path)

    def __len__(self):
        return self.target.__len__()

    def __iter__(self):
        return iter(self.target)

    def __str__(self):
        result = super(Link, self).__str__().rstrip('/')
        return result + ' link to ' + self.target.fullname

    def is_folder(self):
        return self.target.is_folder()

    def iter_deep_first(self, fowllow_link = False):
        if fowllow_link:
            return super(Link, self).iter_deep_first()
        return (self,)

