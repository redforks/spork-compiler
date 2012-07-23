# -*- coding: utf-8 -*-

import unittest
from unittest import TestCase
from sys import modules

class SysTests(TestCase):
    def test_modules(self):
        self.assertSame(unittest, modules['unittest'])
        self.assertTrue('sys' in modules, 'sys')
        self.assertTrue('__builtin__' in modules, '__builtin__')

