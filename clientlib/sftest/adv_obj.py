# -*- coding: utf-8 -*-
from unittest import TestCase

class B(object):
    def __init__(self):
        super(B, self).__init__()
        self.b = 1
        self._id = 1

    def get_b(self):
        return b

    @staticmethod
    def create(val):
        result = B()
        result.b = val
        return result

    @classmethod
    def cls_method(cls):
        if not hasattr(cls, '_cls1'):
            cls._cls1 = 0
        cls._cls1 += 1

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    def with_args(self, *args):
        return args

class C(B):
    def __init__(self):
        super(C, self).__init__()
        self.c = 2

class AdvObjTests(TestCase):
    def test_super_func(self):
        c = C()
        self.assertEqual(1, c.b)
        self.assertEqual(2, c.c)

    def test_staticmethod(self):
        b = B.create(2)
        assert isinstance(b, B)
        self.assertEqual(2, b.b)
        b = b.create(3)
        assert isinstance(b, B)
        self.assertEqual(3, b.b)

        b = C.create(3)
        assert isinstance(b, B)
        self.assertEqual(3, b.b)

    def test_classmethod(self):
        B.cls_method()
        self.assertEqual(1, B._cls1)

        b = B()
        self.assertEqual(1, b._cls1)

        b.cls_method()
        self.assertEqual(2, b._cls1)

        C.cls_method()
        self.assertEqual(1, C._cls1)
        C.cls_method()
        self.assertEqual(2, C._cls1)

        C().cls_method()
        self.assertEqual(3, C._cls1)

    def test_property(self):
        b = B()
        self.assertEqual(1, b.id)
        b.id = 2
        self.assertEqual(2, b.id)
        self.assertEqual(2, b._id)

        b = C()
        self.assertEqual(1, b.id)
        self.assertEqual(1, b._id)
        b.id = 2
        self.assertEqual(2, b.id)
        self.assertEqual(2, b._id)

    def test_untuple(self):
        b = B()
        self.assertEqual((), b.with_args())
        self.assertEqual((1,), b.with_args(1))
        self.assertEqual((1,2), b.with_args(1,2))

    def test_unbind_method(self):
        with self.assertRaises(NotImplementedError):
            get = B.get_b

    def test_get_static_method(self):
        a = B.create
