# -*- coding: utf-8 -*-

from unittest import TestCase

class IntTests(TestCase):
    def test_operates(self):
        self.assertEqual(3, 1+2)
        self.assertEqual(-1, 1-2)
        self.assertEqual(1, 1**2)
        self.assertEqual(8, 2**3)
        self.assertEqual(4, 8/2)
        self.assertEqual(1, 4//3)
        self.assertEqual(0, 1//3)
        self.assertEqual(0, 1//8640000)
        i = 1
        self.assertEqual(-1, -i)
        self.assertEqual(1, +i)
        i -= 3
        self.assertEqual(-2, i)
        i += 4
        self.assertEqual(2, i)
        i *= 3
        self.assertEqual(6, i)
        i /= 2
        self.assertEqual(3, i)
        i //= 2
        self.assertEqual(1, i)
        self.assertTrue(1 >= 0)
        self.assertTrue(1 >= 1)
        self.assertTrue(1 > 0)
        self.assertFalse(1 > 1)
        self.assertTrue(1 <= 1)
        self.assertFalse(1 <= 0)

    def test_abs(self):
        self.assertEqual(1, abs(1))
        self.assertEqual(1, abs(-1))

    def test_int_constructor(self):
        self.assertEqual(0, int(0))
        self.assertEqual(0, int('0'))
        self.assertEqual(10, int('10'))
        self.assertEqual(2, int('10', 2))
        self.assertEqual(1, int(1.0))
        self.assertEqual(1, int(1.9))
        self.assertEqual(0, int(-0.9))
        self.assertEqual(-1, int(-1.9))

    def test_power(self):
        self.assertEqual(1, pow(1, 2))

    def test_divmod(self):
        self.assertEqual((2,0), divmod(2,1))

    def test_bitop(self):
        self.assertEqual(0b11, 0b10 | 0b01)
        self.assertEqual(0, 0x10 & 0x01)
        self.assertEqual(0b11, 0b10 ^ 0b01)
        self.assertEqual(0b10, 0b11 ^ 0b01)
        self.assertEqual(0b10, 1 << 1)
        self.assertEqual(0b1, 2 >> 1)
        self.assertEqual(-1, ~0)
