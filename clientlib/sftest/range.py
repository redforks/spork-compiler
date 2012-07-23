# -*- coding: utf-8 -*-

from unittest import TestCase

class RangeTests(TestCase):
    def test_xrange(self):
        self.assertEqual([], list(xrange(0)))
        self.assertEqual([0, 1], list(xrange(2)))
        self.assertEqual([1, 2], list(xrange(1, 3)))
        self.assertEqual([0, 2], list(xrange(0, 3, 2)))
        self.assertEqual([3, 2, 1], list(xrange(3, 0, -1)))
        self.assertEqual([3, 1], list(xrange(3, 0, -2)))

    def test_range(self):
        self.assertEqual([], range(0))
        self.assertEqual([0, 1], range(2))
        self.assertEqual([1, 2], range(1, 3))
        self.assertEqual([0, 2], range(0, 3, 2))
        self.assertEqual([3, 2, 1], range(3, 0, -1))
        self.assertEqual([3, 1], range(3, 0, -2))
