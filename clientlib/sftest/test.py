# -*- coding: utf-8 -*-

import unittest
from unittest import *

class TestTests_disabled(TestCase):
    def test1(self):
        pass

    def test2(self):
        self.assertEqual(1, 1)

    def test3(self):
        self.assertNotEqual(1, 2)

    def test_dirs(self):
        self.assertTrue('test1' in dir(self))
        self.assertTrue('test2' in dir(TestTests))
        self.assertFalse('nottest1' in dir(self))

    def test__src__(self):
        self.assertEqual('        pass', __src__[7])

    def setUp(self):
        self._setup_hits = 1

    def test_setup(self):
        self.assertEqual(1, self._setup_hits)

    def tearDown(self):
        global _resetted
        _resetted = True

    def test_teardown1(self):
        global _resetted
        self.assertTrue(_resetted)
        _resetted = False

    test_teardown2 = test_teardown1

    def test_del_global(self):
        unittest._del_global_test = 1
        assert hasattr(unittest, '_del_global_test')
        del unittest._del_global_test
        assert not hasattr(unittest, '_del_global_test')

    def test_getattr(self):
        o = Normal()
        o.id = 3
        self.assertEqual(3, getattr(o, 'id'))

        o = HasGetAttr()
        self.assertEqual('a', o.a)
        o.a = 3
        self.assertEqual(3, o.a)

        o.b = 4
        self.assertEqual(4, o.b)

        self.assertError(lambda: getattr(None, 'abc'), AttributeError, 
            "'NoneType' object has no attribute 'abc'")

    def test_bound_function_on_set_attr_on_class(self):
        def f(self):
            return self

        n = Normal()
        self.assertFalse(hasattr(n, 'will_bound'))
        Normal.will_bound = f
        self.assertTrue(hasattr(n, 'will_bound'))
        self.assertEqual(n, n.will_bound())

        del Normal.will_bound
        self.assertFalse(hasattr(n, 'will_bound'))

    def test_unbound_function_on_set_attr_on_instance(self):
        def f(self):
            return self

        def g(self):
            return self

        n = Normal()
        self.assertFalse(hasattr(n, 'xx'))
        n.xx = f
        self.assertTrue(hasattr(n, 'xx'))
        self.assertEqual(3, n.xx(3))

        self.assertSame(f, n.xx)

    def test_hasattr(self):
        self.assertFalse(hasattr(None, 'abc'))

    def test_setattr(self):
        o = HasSetAttr()
        o.id = 3
        self.assertEqual(3, o.id)

        def f():
            o.black = 3
        self.assertError(f, AttributeError)

        self.assertError(lambda: setattr(None, 'cde', 1), AttributeError,
            "'NoneType' object has no attribute 'cde'")

    def test_del_attr(self):
        self._del_attr_test = 1
        assert hasattr(self, '_del_attr_test')
        del self._del_attr_test
        assert not hasattr(self, '_del_attr_test')

    def test_del_localvar(self):
        s = 1
        del s

    def test_untuple(self):
        def f(*args):
            return args

        self.assertEqual((), f())
        self.assertEqual((1,), f(1))
        self.assertEqual((1,), f(*(1,)))
        self.assertEqual((1, 2), f(*(1, 2)))

    def test_untuple_construstor(self):
        c = WithKarg(*(1,))
        self.assertEqual(1, c.a)
        self.assertEqual({}, c.attrs)

        c = WithKarg(*('abc',))
        self.assertEqual('abc', c.a)
        self.assertEqual({}, c.attrs)

    def test_kwarg(self):
        def f(**args):
            return args

        self.assertEqual({}, f())
        self.assertEqual({}, f(*()))
        self.assertEqual({'a': 1}, f(a=1))
        self.assertEqual({'a': 1}, f(**{'a': 1}))

        def f1(a, **args):
            return a, args

        self.assertEqual((1, {}), f1(1))
        self.assertEqual((1, {}), f1(*(1,)))
        self.assertEqual((1, {'a':3}), f1(1, a=3))

        def f2(a, b, **args):
            return a, b, args

        self.assertEqual((1, 2, {}), f2(1, 2))
        self.assertEqual((1, 2, {'a':3}), f2(1, 2, a=3))

        def f3(*args, **kwarg):
            return args, kwarg

        self.assertEqual(((), {}), f3())
        self.assertEqual(((3,), {}), f3(3))
        self.assertEqual(((3,4), {}), f3(3, 4))
        self.assertEqual(((3,4), {'a':1}), f3(3, 4, a=1))

        def f4(a, *b, **args):
           return a, b, args

        self.assertEqual((1, (), {}), f4(1))
        self.assertEqual((1, (2,), {}), f4(1, 2))
        self.assertEqual((1, (2,), {'a':3}), f4(1, 2, a=3))

    def test_undict2(self):
        def f(a, **args):
            return args

        def g(a, **args):
            return f(a, **args)

        def h(**args):
            return g('', **args)

        self.assertEqual({}, f(1))
        self.assertEqual({'b': 1, 'c': 3}, f(1,b=1, c=3))
        self.assertEqual({'b': 1, 'c': 3}, f(1,**{'b': 1, 'c': 3}))
        self.assertEqual({'b': 1, 'c': 3}, g(1,**{'b': 1, 'c': 3}))
        self.assertEqual({'b': 1, 'c': 3}, h(b = 1, c = 3))

    def test_logic_and(self):
        assert True and True
        assert not False and True
        self.assertEqual(0, 0 and 1)
        self.assertEqual(0, 1 and 0)
        assert 1 and 2
        assert not (1 and 0)

        self.assertEqual('', '' and 'a')
        self.assertEqual('', ' ' and '')
        
        emptlist = []
        self.assertSame(emptlist, emptlist and 1)
        self.assertEqual(1, [1] and 1)

    def test_logic_or(self):
        assert True or True
        assert False or True
        assert not (False or False)
        self.assertEqual(1, 0 or 1)
        self.assertEqual(1, 1 or 0)
        assert 1 or 2
        assert not (0 or 0)

        self.assertEqual('a', '' or 'a')
        self.assertEqual(' ', ' ' or '')
        
        emptlist = []
        self.assertSame(1, emptlist or 1)
        self.assertEqual([1], [1] or 1)

    def test_conditional_op(self):
        self.assertEqual(1, 1 if True else 2)
        self.assertEqual(2, 1 if False else 2)

        self.assertEqual(1, 1 if ' ' else 2)
        self.assertEqual(2, 1 if '' else 2)

        self.assertEqual(1, 1 if [1] else 2)
        self.assertEqual(2, 1 if [] else 2)

    def test_func_argcheck(self):
        def noarg():
            pass

        noarg()
        self.assertError(lambda: noarg(1), TypeError, 
                'noarg() takes exactly 0 arguments (1 given)')

        def onearg(f):
            pass
        onearg(1)
        self.assertError(lambda: onearg(1, 3), TypeError, 
                'onearg() takes exactly 1 arguments (2 given)')

    def test_func_def_argcheck(self):
        def f(a=3): pass
        self.assertError(lambda: f(1, 2), TypeError,
                'f() takes at most 1 arguments (2 given)')

        def g(a, b=3): pass
        self.assertError(lambda: g(1, 2, 3), TypeError,
                'g() takes at most 2 arguments (3 given)')

        self.assertError(lambda: g(), TypeError,
                'g() takes at least 1 arguments (0 given)')

    def test_func_vararg_check(self):
        def f(a,*b): pass
        self.assertError(lambda: f(), TypeError,
                'f() takes at least 1 arguments (0 given)')

        # use both *arg, and default arg is not supported
        #def g(a,b=3,*c): pass
        #self.assertError(lambda: g(), TypeError,
                #'g() takes at least 1 arguments (0 given)')

        #self.assertError(lambda: g(b=2), TypeError,
                #'g() takes at least 1 arguments (0 given)')

    def test_func_kwarg_call(self):
        def f(**args): return args
        self.assertEqual({}, f())
        self.assertEqual({'a':3}, f(a=3))

        def g(a,**args): pass
        self.assertError(lambda: g(), TypeError,
                'g() takes at least 1 arguments (0 given)')
        self.assertError(lambda: g(1,2,3), TypeError,
                'g() takes at most 2 arguments (3 given)')

        # use both *arg, and **karg is not supported
        #def foo(a,b=3,*args,**vargs): pass
        #self.assertError(lambda: foo(), TypeError,
                #'foo() takes at least 1 arguments (0 given)')

    def no_arg(self): pass
    def test_method_arg_check(self):
        self.assertError(lambda: self.no_arg(1), TypeError,
                'no_arg() takes exactly 0 arguments (1 given)')

    def with_def_arg(self, a, b=3): pass
    def test_method_defarg_check(self):
        self.assertError(lambda: self.with_def_arg(), TypeError,
                'with_def_arg() takes at least 1 arguments (0 given)')

    def with_var_arg(self, a, *args): pass
    def test_method_vararg_check(self):
        self.assertError(lambda: self.with_var_arg(), TypeError,
                'with_var_arg() takes at least 1 arguments (0 given)')

    def with_kwarg(self, a, **args): pass
    def test_method_vararg_check(self):
        self.assertError(lambda: self.with_kwarg(), TypeError,
                'with_kwarg() takes at least 1 arguments (0 given)')

    @staticmethod
    def static_method():pass
    def test_static_method_arg(self):
        self.static_method()
        self.assertError(lambda: self.static_method(1), TypeError,
                'static_method() takes exactly 0 arguments (1 given)')

    @classmethod
    def class_method(cls): pass
    def test_class_method_arg(self):
        self.class_method()
        self.assertError(lambda: self.class_method(1), TypeError,
                'class_method() takes exactly 0 arguments (1 given)')

    def test_init_argcheck(self):
        HasGetAttr()
        self.assertError(lambda: HasGetAttr(1), TypeError,
                '__init__() takes exactly 0 arguments (1 given)')

        Normal()
        self.assertError(lambda: Normal(1), TypeError,
                '__init__() takes exactly 0 arguments (1 given)')

    def test_import_valid(self):
        def f():
            from unittest import bad
        self.assertError(f, ImportError)

    def test_cover_global_var(self):
        global chr
        self.assertEqual(' ', chr(32))
        chr = 'b'
        self.assertEqual('b', chr)
        import __builtin__ as builtin
        self.assertEqual(' ', builtin.chr(32))

    def test_uninited_global_var(self):
        self.assertError(lambda: c, NameError, "name 'c' is not defined.")

_resetted = True

class Normal(object): pass

class HasGetAttr(object):
    def __init__(self):
        super(HasGetAttr, self).__init__()

    def __getattr__(self, name):
        return name

class HasSetAttr(object):
    def __setattr__(self, name, value):
        if name == 'black':
            raise AttributeError()
        super(HasSetAttr, self).__setattr__(name, value)

class WithKarg(object):
    def __init__(self, a, **karg):
        super(WithKarg, self).__init__()
        self.a = a
        self.attrs = karg

