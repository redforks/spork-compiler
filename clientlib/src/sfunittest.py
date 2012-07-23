# -*- coding: utf-8 -*-
from unittest import TestCase as SysTestCase

_reset_actions = []
def add_reset(f):
    if __debug__:
        _reset_actions.append(f)

def reset():
    global _reset_actions
    for f in _reset_actions:
        f()
    _reset_actions = []

class TestCase(SysTestCase):
    def setUp(self):
        reset()
