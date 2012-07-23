# -*- coding: utf-8 -*-

from unittest import TestCase

class FloatTests(TestCase):
    def test_ops(self):
        self.assertEqual(1.2, 1.0 + 0.2)
        self.assertEqual(1.5, 3.0 / 2)
        self.assertEqual(1.0, 3.0 // 2)
        self.assertEqual(1.0, 3.0 % 2)

    def test_abs(self):
        self.assertEqual(1.1, abs(1.1))
        self.assertEqual(1.1, abs(-1.1))

    def test_pow(self):
        self.assertEqual(1, pow(2.0, 0))
        self.assertEqual(1, 2.0**0)

    def test_float_constructor(self):
        self.assertEqual(0, float(0))
        self.assertEqual(-2.34, float(-2.34))
        self.assertEqual(-2.34, float('-2.34'))

    def test_divmod(self):
        self.assertEqual((1.0, 1.0), divmod(3.0, 2))

    def test_as_integer_ratio(self):
        msg = 'float.as_integer_ratio() is not supported.'
        self.assertError(lambda: 3.0.as_integer_ratio(), 
                NotImplementedError, msg)

    def test_hex(self):
        msg = 'float.hex() is not supported.'
        self.assertError(lambda: 3.0.hex(), NotImplementedError, msg)

    def test_fromhex(self):
        msg = 'float.fromhex() is not supported.'
        self.assertError(lambda: 3.0.fromhex(), NotImplementedError, msg)

    def test_fromstr(self):
        self.assertEqual(5, float('5'))
        self.assertEqual(4, float('4.'))
        self.assertEqual(0.3, float('.3'))
        self.assertEqual(4.33, float('+4.33'))
        self.assertError(lambda: float('4hr'), ValueError,
            'invalid literal for float(): 4hr')


