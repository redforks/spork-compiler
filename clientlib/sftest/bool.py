# -*- coding: utf-8 -*-

from unittest import TestCase

class BoolTests(TestCase):
    def test_bool(self):
        self.assertTrue(True, 'true')
        self.assertFalse(False, 'false')
        self.assertSame(True, bool(1), '1')
        self.assertSame(False, bool(0), '0')
        self.assertSame(False, bool(0.0), '0.0')
        self.assertSame(True, bool(0.1), '0.1')
        self.assertSame(False, bool([]))
        self.assertSame(False, bool(()))
        self.assertSame(False, bool(''))
        self.assertSame(True, bool('a'))
        self.assertSame(True, bool([1]))
        self.assertSame(True, bool((1,)))

    def test_same(self):
        self.assertNotSame(1, '1')
        self.assertNotSame(object(), object())
