# -*- coding: utf-8 -*-
from unittest import TestCase

class DictTests(TestCase):
    def test_empty(self):
        d = {}
        self.assertEqual(0, len(d))
        d = dict()
        self.assertEqual(0, len(d))
        self.assertFalse(d)

    def _test_cmp(self):
        def do_cmp(expected, x, y):
            self.assertEqual(expected, cmp(x, y))
        pass
        do_cmp(0, {}, {})
        do_cmp(1, {1:1}, {})
        do_cmp(-1, {}, {1:1})
        
    def test_eq(self):
        d1 = {}
        d2 = {}
        self.assertEqual(d1, d2)

        d1['a'] = 1
        self.assertNotEqual(d1, d2)
        d2['c'] = 1
        self.assertNotEqual(d1, d2)

        del d2['c']
        d2['a'] = 2
        self.assertNotEqual(d1, d2)

        d2['a'] = 1
        self.assertEqual(d1, d2)

    def test_hash(self):
        self.assertRaises(TypeError, lambda: hash({}))

    def _test_create_by_keywords(self):
        d = dict(a='one')
        self.assertEqual(1, len(d))

    def test_create_by_pair(self):
        d = dict([('a', 1), ('b', 2)])
        self.assertEqual(2, len(d))
        self.assertEqual(1, d['a'])
        self.assertEqual(2, d['b'])

    def test_get_set(self):
        d = {'a': 3, 'b': 4}
        self.assertEqual(3, d['a'])
        d['a'] = 4
        self.assertEqual(4, d['a'])
        self.assertError(lambda: d['c'], KeyError, "'c'")

    def test_del(self):
        d = {'a': 1, 'b': 5}
        del d['a']
        self.assertEqual(1, len(d))
        del d['b']
        self.assertEqual(0, len(d))

        def del_item():
            del d['a']
        self.assertRaises(KeyError, del_item)

    def test_bool(self):
        self.assertFalse({})
        self.assertTrue({'a': 1})

    def test_in(self):
        self.assertFalse(1 in {})
        self.assertTrue(1 in {1: 2})
        self.assertFalse(2 in {1:2})
        self.assertTrue(1 not in {})
        self.assertFalse(1 not in {1: 2})
        self.assertTrue(2 not in {1:2})

    def test_iterkeys(self):
        self.assertEqual([], list({}.iterkeys()))
        self.assertEqual([1, 2], list({1:2,2:3}.iterkeys()))

    def test_clear(self):
        d = {1: 2, 2:3}
        d.clear()
        self.assertEqual(0, len(d))

    def test_copy(self):
        d1 = {}
        d2 = d1.copy() 
        d2['a'] = 3
        self.assertFalse(d1)
        self.assertTrue(d2)

        d1 = d2.copy()
        self.assertEqual(3, d1['a'])

    def test_fromkeys(self):
        d = dict.fromkeys([1, 2, 3])
        self.assertEqual(3, len(d))

    def test_get(self):
        d = {}
        self.assertEqual(None, d.get(3))
        self.assertEqual('a', d.get(3, 'a'))
        
    def test_items(self):
        self.assertEqual([], {}.items())
        self.assertEqual([(1,'a'), (2,'b')], {1:'a', 2:'b'}.items())

    def test_iteritems(self):
        self.assertEqual([], list({}.iteritems()))
        self.assertEqual([(1,'a'), (2,'b')], list({1:'a', 2:'b'}.iteritems()))

    def test_iterkeys(self):
        self.assertEqual([], list({}.iterkeys()))
        self.assertEqual([1, 2], list({1:'a', 2:'b'}.iterkeys()))

    def test_itervalues(self):
        self.assertEqual([], list({}.itervalues()))
        self.assertEqual(['a', 'b'], list({1:'a', 2:'b'}.itervalues()))

    def test_keys(self):
        self.assertEqual([], {}.keys())
        self.assertEqual([1, 2], {1:'a', 2:'b'}.keys())

    def test_pop(self):
        d = {3: 'c'}
        self.assertEqual('c', d.pop(3))
        self.assertError(lambda: d.pop(3), KeyError, '3')
        self.assertEqual('c', d.pop(3, 'c'))

    def test_popitem(self):
        d = {3: 'c'}
        self.assertEqual((3, 'c'), d.popitem())
        self.assertError(lambda: d.popitem(), KeyError, 
            'popitem(): dictionary is empty')

    def test_setdefault(self):
        d = {}
        self.assertEqual(None, d.setdefault('a'))
        self.assertEqual(3, d.setdefault('b', 3))
        self.assertEqual(3, d['b'])
        self.assertEqual(None, d['a'])

    def test_values(self):
        self.assertEqual([], {}.values())
        self.assertEqual(['a', 'b'], {1:'a', 2:'b'}.values())

    def test_update(self):
        d = {}
        d.update({})
        self.assertEqual({}, d)

        d = {1: 'a', 2: 'c'}
        d.update({2: 'b', 3: 'c'})
        self.assertEqual({1:'a', 2:'b', 3:'c'}, d)

    def test_str(self):
        self.assertEqual('{}', str({}))
        self.assertEqual('{1: 2}', str({1: 2}))
        self.assertEqual('{1: 2, 3: 4}', str({1: 2, 3: 4}))
        self.assertEqual('{}', repr({}))
        self.assertEqual('{1: 2}', repr({1: 2}))
        self.assertEqual('{1: 2, 3: 4}', repr({1: 2, 3: 4}))
