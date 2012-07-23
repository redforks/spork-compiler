# -*- coding: utf-8 -*-
from unittest import TestCase
from random import randint, choice

class RandomTests(TestCase):
    def test_randint(self):
        counts = [0, 0, 0]
        for i in xrange(10):
            val = randint(0, 2)
            counts[val] += 1
        self.assertTrue(all(counts), str(counts))

    def test_choice(self):
        counts = [0, 0, 0]
        for i in xrange(10):
            idx = choice(range(3, 6))
            counts[idx - 3] += 1
        self.assertTrue(all(counts), str(counts))
