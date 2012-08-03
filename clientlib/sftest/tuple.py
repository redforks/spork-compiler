# -*- coding: utf-8 -*-
from unittest import TestCase

class Custom(object):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        if self is other:
            return True

        if type(self) is not type(other):
            return False

        return self.name == other.name

class TupleTests(TestCase):
    def test_empty(self):
        lst = ()
        self.assertEqual(0, len(lst))
        self.assertFalse(lst)

        lst = tuple()
        self.assertEqual(0, len(lst))
        self.assertFalse(lst)

    def test_eq(self):
        t = ()
        self.assertEqual(t, t)
        self.assertEqual((), ())
        self.assertEqual((Custom('a'),), (Custom('a'),))
        self.assertEqual((None, Custom('a')), (None, Custom('a')))
        self.assertNotEqual((None, Custom('a')), (None, Custom('b')))

    def test_eq_hash(self):
        self.assertEqual((), ())
        self.assertEqual(((),), ((),))
        hash1 = hash(())
        hash2 = hash(())
        self.assertEqual(hash1, hash2)

    def test_bool(self):
        self.assertFalse(())
        self.assertTrue(3,)

    def test_in(self):
        lst = tuple()
        self.assertFalse(lst in lst)

        lst = tuple((1, 2))
        self.assertTrue(1 in lst)

    def test_slice(self):
        lst = tuple(range(10))
        self.assertEqual(0, lst[0], '0')
        self.assertEqual(9, lst[-1], '9')
        self.assertEqual(8, lst[-2], '8')
        self.assertEqual((0,), lst[0:1], '[0]')
        self.assertEqual((7, 8), lst[7:-1], '[7, 8]')
        self.assertEqual((2, 3, 4), lst[-8:5], '[2, 3, 4]')
        self.assertError(lambda: lst[10], IndexError, 
                'tuple index out of range')
        self.assertEqual((0, 2, 4, 6, 8), lst[::2])
        self.assertEqual((1, 4, 7), lst[1::3])

    def test_concat(self):
        x, y = (1,), (3,)
        self.assertEqual((1, 3), x + y)
        self.assertEqual((1,), x)
        self.assertEqual((3,), y)

    def test_mul(self):
        self.assertEqual((), () * 3)
        self.assertEqual(('a', 'a', 'a'), ('a',) * 3)
        self.assertEqual(('a', 'b', 'a', 'b'), ('a', 'b') * 2)

    def test_max(self):
        self.assertEqual(2, max((1, 2)))
        self.assertError(lambda: max(()), ValueError, 
            'max() arg is an empty sequence.')

    def test_min(self):
        self.assertEqual(1, min((1, 2)))
        self.assertError(lambda: min(()), ValueError, 
            'min() arg is an empty sequence.')

    def test_count(self):
        s = ()
        self.assertEqual(0, s.count(3))
        s = (1, 3, 4)
        self.assertEqual(1, s.count(3))
        s = (1, 3, 3, 5, '3')
        self.assertEqual(2, s.count(3))

    def test_index(self):
        s = (1,)
        self.assertEqual(0, s.index(1), '0')
        self.assertError(lambda: s.index(2), ValueError, 
            'tuple.index(x): x not in list')
