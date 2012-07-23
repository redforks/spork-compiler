# -*- coding: utf-8 -*-
import unittest
import math

class MathTests(unittest.TestCase):
    def test_degrees(self):
        self.assertEqual(0, math.degrees(0))
        self.assertEqual(180, math.degrees(math.pi))
        self.assertEqual(90, math.degrees(math.pi / 2))
        self.assertEqual(360, math.degrees(math.pi * 2))
        self.assertEqual(720, math.degrees(math.pi * 4))
        self.assertEqual(-720, math.degrees(-math.pi * 4))

    def test_radians(self):
        self.assertEqual(0, math.radians(0))
        self.assertEqual(math.pi, math.radians(180))
        self.assertEqual(math.pi / 2, math.radians(90))
        self.assertEqual(math.pi * 2, math.radians(360))
        self.assertEqual(-math.pi * 4, math.radians(-720))
