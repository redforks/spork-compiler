# -*- coding: utf-8 -*-
import datetime
from sfunittest import add_reset

def reset():
    datetime._test_now = None

def setnow(val):
    datetime._test_now = val 
    add_reset(reset)

