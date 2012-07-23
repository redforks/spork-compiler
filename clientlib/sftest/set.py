# -*- coding: utf-8 -*-
from unittest import TestCase

class SetTests(TestCase):
    def test(self):
        s = set()
        self.assertEqual(0, len(s))
        self.assertFalse(None in s)
        self.assertTrue(None not in s)
        self.assertRaises(TypeError, lambda: s[0])
        with self.assertRaises(TypeError):
            s[0] = 1
        self.assertEqual([], list(s))
        self.assertEqual((), tuple(s))
        self.assertRaises(TypeError, lambda: {s: 1})
        #self.assertTrue(s.issubset(s))
        #self.assertTrue(s <= s)
        #self.assertFalse(s < s)
        #self.assertTrue(s.issuperset(s))
        #self.assertTrue(s >= s)
        #self.assertFalse(s > s)
        #self.assertEqual(s, set())
        #self.assertEqual(0, len(s.union(set())))
        #self.assertEqual(0, len(s | set()))
        #self.assertEqual(s, s.intersection(s))
        #self.assertEqual(s, s & s & s)
        #self.assertEqual(s, s.difference(s))
        #self.assertEqual(s, s - s)
        #self.assertEqual(s, s.symmetric_difference(s))
        #self.assertEqual(s, s ^ s)
        #self.assertEqual(s, s.copy())
        #s.update(s)
        #s |= s
        #s.intersection_update(s)
        #s &= s
        #s.difference_update(s)
        #s -= s
        #s.symmetric_difference_update(s)
        #s ^= s
        #self.assertEqual(set(), s)
        #s.add(1)
        #s.remove(1)
        #s.discard(1)
        #s.add(2)
        #s.pop()
        #s.clear()
        #self.assertEqual(set(), s)
        #self.assertEqual('set([])', str(s))
        #self.assertEqual('set([])', repr(s))

    def test_add(self):
        s = set([1, 2, 3, 3])
        self.assertEqual(set([1, 2, 3]), s)
        s.add(2)
        s.add(3)
        self.assertEqual(set([1, 2, 3]), s)

    def test_len_iter_in(self):
        s = set()
        s.add(1)
        self.assertEqual(1, len(s))
        self.assertEqual([1], list(s))
        self.assertTrue(1 in s)
        self.assertTrue(2 not in s)

    def test_init(self):
        s1 = set()
        s2 = set([])
        s3 = set(())
        self.assertEqual(s1, s2)
        self.assertEqual(s2, s3)

        s1 = set([1, 2])
        s2 = set((1, 2))
        s3 = set(s1)
        self.assertEqual([1, 2], list(s1))
        self.assertEqual(s1, s2)
        self.assertEqual(s2, s3)

    def test_issubset(self):
        s, empty = set([1]), set()
        self.assert_issubset(empty, s, True)
        self.assert_issubset(s, s, True)
        self.assert_issubset(s, empty, False)

        s1 = set([2])
        self.assert_issubset(s1, s, False)
        self.assert_issubset(s, s1, False)

        s1.add(3)
        self.assert_issubset(s1, s, False)
        self.assert_issubset(s, s1, False)

    def test_lt(self):
        s1, s2 = set(), set([1, 2, 3])
        self.assertTrue(s1 < s2)
        self.assertFalse(s2 < s1)

        s1.add(2)
        self.assertTrue(s1 < s2)
        self.assertFalse(s2 < s1)

        s1.add(1)
        s1.add(3)
        self.assertFalse(s1 < s2)
        self.assertFalse(s2 < s1)

        s1 = set([4, 5])
        self.assertFalse(s1 < s2)
        self.assertFalse(s2 < s1)

    def test_issuperset(self):
        s, empty = set([1]), set()
        self.assert_issuperset(empty, s, False)
        self.assert_issuperset(s, s, True)
        self.assert_issuperset(s, empty, True)

        s1 = set([2])
        self.assert_issuperset(s1, s, False)
        self.assert_issuperset(s, s1, False)

        s1.add(3)
        self.assert_issuperset(s1, s, False)
        self.assert_issuperset(s, s1, False)

    def test_gt(self):
        s1, s2 = set(), set([1, 2, 3])
        self.assertFalse(s1 > s2)
        self.assertTrue(s2 > s1)

        s1.add(2)
        self.assertFalse(s1 > s2)
        self.assertTrue(s2 > s1)

        s1.add(1)
        s1.add(3)
        self.assertFalse(s1 > s2)
        self.assertFalse(s2 > s1)

        s1 = set([4, 5])
        self.assertFalse(s1 > s2)
        self.assertFalse(s2 > s1)

    def test_str(self):
        self.assertEqual('set([])', str(set()))
        self.assertEqual('set([1])', str(set([1])))
        self.assertEqual('set([1])', str(set((1,))))

    def test_union(self):
        s1, s2 = set([1, 2]), set([2, 3])
        self.assertEqual(set([1, 2, 3]), s1.union(s2))
        self.assertEqual(set([1, 2]), s1)
        self.assertEqual(set([2, 3]), s2)

        s3 = s1 | s2
        self.assertEqual(set([1, 2, 3]), s3)
        self.assertEqual(set([1, 2]), s1)
        self.assertEqual(set([2, 3]), s2)

    def test_intersection(self):
        s1, s2 = set([1, 2]), set([2, 3])
        self.assertEqual(set([2]), s1.intersection(s2))
        self.assertEqual(set([1, 2]), s1)
        self.assertEqual(set([2, 3]), s2)

        self.assertEqual(set([2]), s1 & s2)
        self.assertEqual(set([1, 2]), s1)
        self.assertEqual(set([2, 3]), s2)

    def test_difference(self):
        s1, s2 = set([1, 2]), set([2, 3])
        self.assertEqual(set([1]), s1.difference(s2))
        self.assertEqual(set([1, 2]), s1)
        self.assertEqual(set([2, 3]), s2)

        self.assertEqual(set([1]), s1 - s2)
        self.assertEqual(set([1, 2]), s1)
        self.assertEqual(set([2, 3]), s2)

    def test_symmetric_difference(self):
        s1, s2 = set([1, 2]), set([2, 3])
        self.assertEqual(set([1, 3]), s1.symmetric_difference(s2))
        self.assertEqual(set([1, 2]), s1)
        self.assertEqual(set([2, 3]), s2)

        self.assertEqual(set([1, 3]), s1 ^ s2)
        self.assertEqual(set([1, 2]), s1)
        self.assertEqual(set([2, 3]), s2)

    def test_copy(self):
        s = set([1, 2])
        self.assertEqual(s, s.copy())
        self.assertNotSame(s, s.copy())

    def test_update(self):
        s1, s2 = set([1, 2]), set([2, 3])
        s = s1.copy()
        s.update(s2)
        self.assertEqual(set([1, 2, 3]), s)

        s = s1.copy()
        s |= s2
        self.assertEqual(set([1, 2, 3]), s)

    def test_intersection_update(self):
        s1, s2 = set([1, 2]), set([2, 3])
        s = s1.copy()
        s.intersection_update(s2)
        self.assertEqual(set([2]), s)

        s = s1.copy()
        s &= s2
        self.assertEqual(set([2]), s)

    def test_difference_update(self):
        s1, s2 = set([1, 2]), set([2, 3])
        s = s1.copy()
        s.difference_update(s2)
        self.assertEqual(set([1]), s)

        s = s1.copy()
        s -= s2
        self.assertEqual(set([1]), s)

    def test_symmetric_difference_update(self):
        s1, s2 = set([1, 2]), set([2, 3])
        s = s1.copy()
        s.symmetric_difference_update(s2)
        self.assertEqual(set([1, 3]), s)

        s = s1.copy()
        s ^= s2
        self.assertEqual(set([1, 3]), s)

    def test_remove_discard(self):
        s = set([1, 2, 3])
        s.remove(2)
        self.assertEqual(set([1, 3]), s)
        s.remove(1)
        s.discard(3)
        self.assertEqual(set(), s)
        self.assertRaises(KeyError, lambda: s.remove(3))
        s.discard(3)
        self.assertEqual(set(), s)

    def test_pop(self):
        s = set([1, 2, 3])
        items = set()
        items.add(s.pop())
        items.add(s.pop())
        items.add(s.pop())
        self.assertEqual(0, len(s))
        self.assertEqual(set([1, 2, 3]), items)
        self.assertRaises(KeyError, lambda: s.pop())

    def test_clear(self):
        s = set([1, 2, 3])
        s.clear()
        self.assertEqual(set(), s)
        s.clear()
        self.assertEqual(set(), s)

    def assert_issubset(self, s1, s2, result):
        self.assertEqual(result, s1.issubset(s2))
        self.assertEqual(result, s1 <= s2)

    def assert_issuperset(self, s1, s2, result):
        self.assertEqual(result, s1.issuperset(s2))
        self.assertEqual(result, s1 >= s2)
