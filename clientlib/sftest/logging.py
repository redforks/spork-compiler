# -*- coding: utf-8 -*-

from logging import *
from unittest import TestCase

class LoggingTests(TestCase):
    def test_call(self):
        ' ensure calling logging functions do not cause run time error'
        log('msg')
        debug('msg')
        info('msg')
        warning('msg')
        error('msg')
