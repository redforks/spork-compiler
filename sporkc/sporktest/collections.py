# -*- coding: utf-8 -*-
import unittest
from spork.collections import OrderedSet

class OrderedSetTest(unittest.TestCase):
    def test_empty(self):
        s = OrderedSet()
        self.assertEquals(0, len(s))
        self.assertFalse(0 in s)
        self.assertEquals([], list(s))

    def test_from_iterable(self):
        s = OrderedSet([1, 2, 3])
        self.assertEquals(3, len(s))
        self.assertEquals([1, 2, 3], list(s))

    def test(self):
        s = OrderedSet()
        s.add(1)
        s.add(2)
        s.add(3)
        self.assertEquals([1, 2, 3], list(s))

        s.update([2, 3, 4])
        self.assertEquals([1, 2, 3, 4], list(s))
