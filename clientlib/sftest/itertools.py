# -*- coding: utf-8 -*-
from unittest import TestCase
from itertools import chain

class IterToolsTests(TestCase):
    def test_from_iterable(self):
        def do_assert1(expected, *iters):
            self.assertEqual(expected, list(chain(*iters)))

        def do_assert2(expected, *iters):
            self.assertEqual(expected, list(chain.from_iterable(iters)))

        do_assert1([])
        do_assert1(range(10), range(10))
        do_assert1(range(11), xrange(11))
        do_assert1(range(12), range(5), range(5, 12))
        do_assert1(range(12), xrange(5), xrange(5, 12))

        do_assert2([])
        do_assert2(range(10), range(10))
        do_assert2(range(11), xrange(11))
        do_assert2(range(12), range(5), range(5, 12))
        do_assert2(range(12), xrange(5), xrange(5, 12))
