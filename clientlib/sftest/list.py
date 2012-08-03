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

class ListTests(TestCase):
    def test_empty(self):
        lst = []
        self.assertEqual(0, len(lst))
        self.assertFalse(lst)

        lst = list()
        self.assertEqual(0, len(lst))
        self.assertFalse(lst)

    def test(self):
        lst = list()
        lst.append(lst)
        self.assertEqual(1, len(lst))
        lst.extend([])
        self.assertEqual(1, len(lst))
        self.assertTrue(lst in lst)

    def test_eq(self): 
        self.assertEqual([], [])
        self.assertEqual([1,2,'2'], [1, 2, '2'])
        self.assertNotEqual([], [1])
        self.assertNotEqual([2], [1])
        self.assertNotEqual([2], ['abc'])
        self.assertNotEqual([], ())
        self.assertNotEqual([], 1)

        self.assertEqual([Custom('a')], [Custom('a')])
        self.assertNotEqual([Custom('b')], [Custom('a')])

    def test_hash(self):
        self.assertRaises(TypeError, lambda: hash([]))

    def test_bool(self):
        self.assertFalse([])
        self.assertTrue([0])

    def test_slice(self):
        lst = range(10)
        self.assertEqual(0, lst[0])
        self.assertEqual(9, lst[-1])
        self.assertEqual(8, lst[-2])
        self.assertEqual(lst, lst[:])
        self.assertEqual([0], lst[0:1])
        self.assertEqual([7, 8], lst[7:-1])
        self.assertEqual([2, 3, 4], lst[-8:5])
        self.assertError(lambda: lst[10], IndexError, 
                'list index out of range')
        self.assertEqual([1, 3], lst[1:5:2])

    def test_in(self):
        assert 1 in range(10)
        assert 10 not in range(10)

    def test_concat(self):
        x, y = [1], [3]
        self.assertEqual([1, 3], x + y)
        self.assertEqual([1], x)
        self.assertEqual([3], y)

    def test_mul(self):
        self.assertEqual([], [] * 3)
        self.assertEqual(['a', 'a', 'a'], ['a'] * 3)
        self.assertEqual(['a', 'b', 'a', 'b'], ['a', 'b'] * 2)

    def test_min(self):
        self.assertEqual(1, min([1, 2]))
        self.assertError(lambda: min([]), ValueError, 
            'min() arg is an empty sequence.')

    def test_max(self):
        self.assertEqual(2, max([1, 2]))
        self.assertError(lambda: max([]), ValueError, 
            'max() arg is an empty sequence.')

    def test_del(self):
        s = range(3)
        del s[0]
        self.assertEqual([1, 2], s)
        del s[-1]
        self.assertEqual([1], s)

    def test_del_slice(self):
        s = range(10)
        del s[2:8]
        self.assertEqual([0, 1, 8, 9], s)
        del s[0:-2]
        self.assertEqual([8, 9], s)
        s = range(10)
        del s[::2]
        self.assertEqual([1, 3, 5, 7, 9], s)
        s = range(10)
        del s[1::3]
        self.assertEqual([0, 2, 3, 5, 6, 8, 9], s)
        del s[::2]
        self.assertEqual([2, 5, 8], s)

        del s[4:5] # delete range not raise exception

    def test_count(self):
        s = []
        self.assertEqual(0, s.count(3))
        s = [1, 3, 4]
        self.assertEqual(1, s.count(3))
        s = [1, 3, 3, 5, '3']
        self.assertEqual(2, s.count(3))

    def test_set_negative_idx(self):
        s = [1, 2, 3]
        s[-1] = 4
        self.assertEqual(4, s[2])

    def test_set_slice(self):
        s = [1]
        s[0] = 2
        self.assertEqual(2, s[0])
        s[:] = []
        self.assertEqual([], s)
        s = range(10)
        s[:5] = []
        self.assertEqual([5, 6, 7, 8, 9], s)
        s[2:] = [2, 3]
        self.assertEqual([5, 6, 2, 3], s)
        s[::2] = [0, 1]
        self.assertEqual([0, 6, 1, 3], s)
        with self.assertRaises(ValueError):
            s[::2] = []

    def test_index(self):
        s = [1]
        self.assertEqual(0, s.index(1), '0')
        self.assertError(lambda: s.index(2), ValueError, 
            'list.index(x): x not in list')

    def test_get(self):
        s = [1, 2]
        self.assertEqual(2, s[-1])
        self.assertEqual(1, s[-2])

    def test_insert(self):
        s = []
        s.insert(0, 3)
        self.assertEqual([3], s)
        s.insert(0, 4)
        self.assertEqual([4, 3], s)
        s.insert(1, 5)
        self.assertEqual([4, 5, 3], s)
        s.insert(3, 6)
        self.assertEqual([4, 5, 3, 6], s)

    def test_pop(self):
        s = [1, 3, 4, 5]
        self.assertEqual(5, s.pop())
        self.assertEqual(3, s.pop(1))
        self.assertEqual(4, s.pop())
        self.assertEqual(1, s.pop())
        self.assertFalse(s)
        self.assertEqual(0, len(s))
        self.assertError(lambda: s.pop(), IndexError,
                'list index out of range')

    def test_remove(self):
        s = [1, 3, 4, 5]
        s.remove(3)
        self.assertEqual([1, 4, 5], s)
        self.assertError(lambda: s.remove(0), ValueError,
                'list.index(x): x not in list')

    def test_reverse(self):
        s = []
        s.reverse()
        self.assertEqual([], s)
        s = [1]
        s.reverse()
        self.assertEqual([1], s)
        s = [1, 2]
        s.reverse()
        self.assertEqual([2, 1], s)
        s = [1, 2, 3]
        s.reverse()
        self.assertEqual([3, 2, 1], s)

    def test_sort(self):
        s = [2, 1, 3]
        s.sort()
        self.assertEqual([1, 2, 3], s)

        s = [2, 1, 3]
        s.sort(lambda x, y: y - x)
        self.assertEqual([3, 2, 1], s)

        s = [2, 1, 3]
        s.sort(key=lambda x: x)
        self.assertEqual([1, 2, 3], s)

        s = [2, 1, 3]
        s.sort(key=lambda x: x, reverse=True)
        self.assertEqual([3, 2, 1], s)

    def test_str(self):
        self.assertEqual('[]', str([]))
        self.assertEqual('[1]', str([1]))
        self.assertEqual('[1, 2]', str([1,2]))
        self.assertEqual('[]', repr([]))
        self.assertEqual('[1]', repr([1]))
        self.assertEqual('[1, 2]', repr([1,2]))
