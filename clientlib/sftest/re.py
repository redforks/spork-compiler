# -*- coding: utf-8 -*-
from unittest import TestCase
import re

class ReTests(TestCase):
    def test_match(self):
        self.assertEqual(None, re.match('abc', 'cd'), '1')
        self.assertNotEqual(None, re.match('abc', 'abcd'), '2')
        self.assertEqual(None, re.match('abc', 'xabcd'), '3')

    def test_search(self):
        self.assertEqual(None, re.search('abc', 'cd'))
        self.assertNotEqual(None, re.search('abc', 'abcd'))
        self.assertNotEqual(None, re.search('abc', 'xabcd'))

    def test_split(self):
        self.assertEqual([''], re.split('', ''))
        self.assertEqual(['a'], re.split(' ', 'a'))
        self.assertEqual(['a', 'b', 'c'], re.split('\\s+', 'a b \tc'))

        self.assertEqual(['a', 'b \tc'], re.split('\\s+', 'a b \tc', 1))
