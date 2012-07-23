# -*- coding: utf-8 -*-
from unittest import TestRunner, scan_test_classes
from __spork__ import gen_home_html
import sftest.bool
import sftest.test
import sftest.list
import sftest.string
import sftest.float
import sftest.int
import sftest.range
import sftest.tuple
import sftest.dict
import sftest.sys
import sftest.traceback
import sftest.re
import sftest.atstartup
import sftest.builtinfuncs
import sftest.adv_obj
import sftest.datetime
import sftest.withstat
import sftest.logging
import sftest.set
import sftest.comprehension
import sftest.itertools
import sftest.random
import sftest.math
from atstartup import register

gen_home_html()

r = None
def run():
    global r
    tests = scan_test_classes('sftest')
    r = TestRunner(tests).run()

register(run)
