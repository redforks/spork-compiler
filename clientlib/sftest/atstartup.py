# -*- coding: utf-8 -*-
from unittest import TestCase
from atstartup import register, _trigger, _reset

class AtStartupTests(TestCase):
    def test_one(self):
        hits = 0
        def func():
            hits += 1
        register(func)
        _trigger()
        self.assertEqual(1, hits)

    def test_two(self):
        hits = 0
        def func():
            hits += 1
        register(func)
        register(func)
        _trigger()
        self.assertEqual(2, hits)
