# -*- coding: utf-8 -*-

from unittest import TestCase
from __spork__ import JS

class A(object):
    pass

class BuiltinFuncTests(TestCase):
    def test_abs(self):
        self.assertEqual(1, abs(1))
        self.assertEqual(1.3, abs(-1.3))

    def test_all(self):
        assert all([])
        assert all([True])
        assert all([1, 2])
        assert not all([1, 2, 0])

    def test_any(self):
        assert not any([])
        assert any([True])
        assert any([1, 2])
        assert any([1, 2, 0])
        assert not any([0, False, '', ()])

    def test_chr(self):
        self.assertEqual('a', chr(97))

    def test_ord(self):
        self.assertEqual(97, ord('a'))
        self.assertError(lambda: ord('ab'), TypeError,
                'ord() expected a character, but string of length 2 found')
        self.assertError(lambda: ord(1), TypeError,
                'ord() expected string')

    def test_cmp(self):
        self.assertEqual(0, cmp(1, 1))
        assert cmp(2, 0) > 0
        assert cmp(0, 2) < 0

    def test_complex(self):
        self.assertError(lambda: complex(1, 1), NotImplementedError, 
                'complex() is not implemented.')

    def test_delattr(self):
        self.delattr_test = 1
        assert hasattr(self, 'delattr_test')
        delattr(self, 'delattr_test')
        assert not hasattr(self, 'delattr_test')
        self.assertError(lambda: delattr(self, 'delattr_test'),
                AttributeError, 'delattr_test')
        self.assertRaises(AttributeError, lambda: delattr(self, 'test_delattr'))
        self.assertRaises(AttributeError, lambda: delattr(None, 'prop'))

    def test_dir(self):
        a = A()
        a.b = 3
        assert 'b' in dir(a)
        del a.b
        assert 'b' not in dir(a)

    def test_divmod(self):
        q, r = divmod(3, 2)
        self.assertEqual(1, q)
        self.assertEqual(1, r)

    def test_filter(self):
        self.assertEqual([], filter(lambda x: False, range(3)))
        self.assertEqual([1], filter(lambda x: x==1, range(3)))

    def test_float(self):
        self.assertEqual(1.0, float(1))

    def test_getattr_setattr(self):
        a = A()
        self.assertEqual(4, getattr(a, 'b', 4))
        a.b = 3
        self.assertEqual(3, getattr(a, 'b'))
        self.assertError(lambda: getattr(a, 'not_exist'), AttributeError,
                'can not found attr not_exist on <A object>')

        JS('a.$const$=44;')
        self.assertEqual(44, getattr(a, 'const'))

        setattr(a, 'const', 32)
        self.assertEqual(32, getattr(a, 'const'))

    def test_hasattr(self):
        a = A()
        assert not hasattr(a, 'a')
        a.a = 3
        assert hasattr(a, 'a')

        a.const = None
        assert hasattr(a, 'const')
        del a.const
        assert not hasattr(a, 'const')

        assert not hasattr(NotImplemented, 'a')
        assert not hasattr(None, 'a')

    def test_hash(self):
        self.assertEqual(1, hash(1))
        self.assertEqual(0, hash(None))

    def test_hex(self):
        self.assertEqual('0x1', hex(1))
        self.assertEqual('-0x1', hex(-1))
        self.assertError(lambda: hex('1'),
                TypeError, "hex() argument can't be converted to hex")

    def test_oct(self):
        self.assertEqual('010', oct(8))
        self.assertEqual('-010', oct(-8))
        self.assertError(lambda: oct('1'),
                TypeError, "oct() argument can't be converted to hex")

    def test_unsupported(self):
        def do_test(func, funcname):
            self.assertError(func, NotImplementedError,
                    funcname + '() is not implemented.')

        do_test(lambda: id(1), 'id')
        do_test(lambda: globals(), 'globals')
        do_test(lambda: frozenset([]), 'frozenset')
        do_test(lambda: file('t.py'), 'file')
        do_test(lambda: open('t.py'), 'open')
        do_test(lambda: execfile('t.py'), 'execfile')
        do_test(lambda: eval('1'), 'eval')
        do_test(lambda: compile('1', 't.py', 'exec'), 'compile')
        do_test(lambda: callable(int), 'callable')
        do_test(lambda: input('p'), 'input')
        do_test(lambda: issubclass(int, object), 'issubclass')
        do_test(lambda: locals(), 'locals')
        do_test(lambda: sorted([]), 'sorted')
        do_test(lambda: unichr(65), 'unichr')
        do_test(lambda: unicode(65), 'unicode')
        do_test(lambda: vars(), 'vars')

    def test_type(self):
        self.assertSame(int, type(1))
        self.assertSame(bool, type(True))
        self.assertSame(bool, type(False))
        self.assertSame(NoneType, type(None))
        self.assertSame(NotImplementedType, type(NotImplemented))
        self.assertSame(str, type(''))
        self.assertSame(float, type(1.1))
        self.assertSame(object, type(object()))
        self.assertSame(BuiltinFuncTests, type(self))
        self.assertSame(list, type([]))
        self.assertSame(dict, type({}))
        self.assertSame(tuple, type(()))
        self.assertSame(TypeType, type(BuiltinFuncTests))
        self.assertSame(TypeType, type(int))
        self.assertSame(TypeType, type(str))
        self.assertSame(TypeType, type(bool))
        self.assertSame(TypeType, type(float))
        self.assertSame(TypeType, type(list))
        self.assertSame(TypeType, type(tuple))
        self.assertSame(TypeType, type(dict))

    def test_vars(self):
        class A(object): pass

        a = A()
        d = vars(a)
        self.assertIsInstance(d, dict)
        self.assertEqual(0, len(d))
        a.a = 3
        self.assertEqual({'a': 3}, vars(a))

        self.assertRaises(TypeError, lambda: vars(None))

    def test_reduce(self):
        self.assertEqual(0, reduce(lambda x, y: x + y, (), 0))
        self.assertEqual(1, reduce(lambda x, y: x + y, (1,)))
        self.assertEqual(6, reduce(lambda x, y: x + y, (1, 2, 3)))
        self.assertEqual(0, reduce(lambda x, y: x + y, (1, 2, 3), -6))

    def test_isinstance(self):
        assert isinstance(1, int)
        assert isinstance('1', str)
        assert isinstance(True, bool)
        assert isinstance(False, bool)
        assert not isinstance(1, str)
        assert isinstance(self, BuiltinFuncTests)
        assert isinstance((), tuple)
        assert isinstance([], list)
        assert isinstance(1, (int,))
        assert isinstance('2', (int, str))

    def test_len(self):
        self.assertEqual(1, len([1]))
        self.assertEqual(1, len((1,)))
        self.assertEqual(1, len('a'))

    def test_long(self):
        self.assertEqual(1L, long(1))

    def test_map(self):
        self.assertEqual([], map(lambda x: x, []))
        self.assertEqual(['1', '2'], map(str, [1, 2]))

    def test_max(self):
        self.assertEqual(2, max(1, 2))
        self.assertEqual(2, max([1, 2]))
        self.assertError(lambda: max(1), TypeError, 
                "object is not iterable")
        self.assertError(lambda: max([]), ValueError, 
                'max() arg is an empty sequence.')
        self.assertEqual(1, max([1, 2], key=lambda x:-x))

    def test_min(self):
        self.assertEqual(1, min(1, 2))
        self.assertEqual(1, min([1, 2]))
        self.assertError(lambda: min(1), TypeError, 
                "object is not iterable")
        self.assertError(lambda: min([]), ValueError, 
                'min() arg is an empty sequence.')
        self.assertEqual(2, min([1, 2], key=lambda x:-x))

    def test_iter(self):
        it = iter(range(2))
        self.assertEqual([0, 1], list(it))
        self.assertError(lambda: iter(1), TypeError,
            "object is not iterable")

    def test_next(self):
        self.assertEqual(0, next(iter(range(2))))
        self.assertError(lambda: next(range(2)), TypeError,
                'object is not an iterator')
        self.assertEqual(0, next(iter(range(2)), 100))
        self.assertEqual(100, next(iter(()), 100))

    def test_pow(self):
        self.assertEqual(1000, pow(10, 3))
        self.assertEqual(0.001, pow(10, -3))

    def _test_raw_input(self):
        back = raw_input("please input `abc': ")
        self.assertEqual('abc', back)

    def test_reversed(self):
        self.assertEqual([], list(reversed([])))
        self.assertEqual([3, 2, 1], list(reversed((1, 2, 3))))

    def test_round(self):
        self.assertEqual(1, round(0.5))
        self.assertEqual(-1, round(-0.5))
        self.assertEqual(1.2, round(1.234, 1))
        self.assertEqual(1.23, round(1.234, 2))
        self.assertEqual(10, round(12.34, -1))
        self.assertEqual(0, round(12.34, -2))
        self.assertEqual(100, round(123.4, -2))

    def test_slice(self):
        s = slice(3, 10, 1)
        self.assertEqual(3, s.start)
        self.assertEqual(10, s.stop)
        self.assertEqual(1, s.step)
        
        self.assertEqual((3, 10, 1), s.indices(100))
        self.assertEqual((0, 0, 1), s.indices(0))
        self.assertEqual((3, 4, 1), s.indices(4))

    def test_sum(self):
        self.assertEqual(0, sum([]))
        self.assertEqual(6, sum(range(4)))
        self.assertEqual(8, sum(range(4), 2))

    def test_zip(self):
        self.assertEqual([], zip())
        self.assertEqual([(0,),(1,),(2,)], zip(range(3)))
        self.assertEqual([(0,1,0),(1,2,1),(2,3,2)], zip(range(3), range(1, 4),
            range(3)))
        self.assertEqual([(0,1),(1,2)], zip(range(3), range(1, 3)))

    def test_isinstance(self):
        assert not isinstance(None, BuiltinFuncTests)

    def test_import_not_exist_module(self):
        def f1():
            import bad
        self.assertError(f1, ImportError, 'No module named bad')

        def f2():
            from bad import wow
        self.assertError(f2, ImportError, 'No module named bad')

    def test_str_None(self):
        self.assertEqual('None', str(None))

    def test_repr_None(self):
        self.assertEqual('None', repr(None))

    def test_NotImplented(self):
        self.assertEqual('NotImplemented', str(NotImplemented))

