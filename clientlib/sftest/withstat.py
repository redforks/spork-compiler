# -*- coding: utf-8 -*-

from unittest import TestCase

class Context(object):
    def __init__(self, enter, exit):
        super(Context, self).__init__()
        self.enter = enter
        self.exit = exit
        self._log = ''

    def __enter__(self):
        self._log += 'enter '
        return self.enter

    def __exit__(self, cls_type, cls, trace):
        if cls:
            assert cls_type
            self._log += 'exit with error '
        else:
            self._log += 'exit no error '
        return self.exit

    def __str__(self):
        return self._log

class WithStatementTests(TestCase):
    def test_normal(self):
        c = Context(None, None)
        with c:
            pass

        self.assertEqual('enter exit no error ', str(c))

    def test_on_error(self): 
        c = Context(None, None)
        try:
            with c:
                assert False
            raise TypeError()
        except AssertionError:
            pass

        self.assertEqual('enter exit with error ', str(c))

    def test_block_error(self):
        c = Context(None, True)
        with c:
            assert False
        self.assertEqual('enter exit with error ', str(c))

    def test_enter_var(self):
        with Context('wow', None) as c:
            self.assertEqual('wow', c)
