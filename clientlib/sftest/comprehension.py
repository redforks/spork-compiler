# -*- coding: utf-8 -*-

from unittest import TestCase

class CompTests(TestCase):
    def test_generator_expr(self):
        def assert_genxp(expected, xp):
            self.assertEqual(expected, list(xp))

        assert_genxp([], (x for x in []))
        assert_genxp([1, 2, 3], (x for x in [1, 2, 3]))
        assert_genxp([0, 2, 4], (2*x for x in [0, 1, 2]))
        assert_genxp([0, 2, 4], (x for x in range(5) if x % 2 == 0))
