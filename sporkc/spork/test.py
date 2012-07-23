# -*- coding: utf-8 -*-
import os, unittest, itertools, logging

from spork.internal import _cleanup_for_test as cleanup
from spork import typeutil

def assertError(self, errcls, *args):
    class AssertError(object):
        def __init__(self, testcase, errcls, args):
            self.testcase = testcase
            self.errcls = errcls
            self.args = args
        
        def __enter__(self):
            return None

        def __exit__(self, errcls, err, traceback):
            assert err is not None, \
                _('expect raise %r, but no exception raised') % self.errcls
            assert issubclass(errcls, self.errcls), \
                _('expect raise %r, but %r raised') % (self.errcls, errcls)
            if self.args:
                self.testcase.assertEqual(self.args, err.args)
            return True
    return AssertError(self, errcls, args)

unittest.TestCase.assertError = assertError
del assertError

import spork.internal
class TestBase(unittest.TestCase):
    def setUp(self):
        assert spork.internal._test, _('should enable test mode')
        super(TestBase, self).setUp()
        cleanup()

    def tearDown(self):
        cleanup()
        super(TestBase, self).tearDown()

def enable_test_mode():
    import spork.internal
    spork.internal._test = True

def setup_spork_log(log_levels):
    for name, level in log_levels:
        logger = logging.getLogger(name)
        logger.setLevel(level)

def MyTestRunner(options):
    return unittest.TextTestRunner(failfast=options.stop)

class MyTestLoader(unittest.TestLoader):
    def loadTestsFromModule(self, module):
        def is_test_case(cls_name, cls):
            return cls_name.endswith('Test') and \
                isinstance(cls, type) and \
                issubclass(cls, unittest.TestCase)

        tests = []
        for name in typeutil.publicdir(module):
            obj = getattr(module, name)
            if is_test_case(name, obj):
                tests.append(self.loadTestsFromTestCase(obj))
        return self.suiteClass(tests)

get_tests_by_module = MyTestLoader().loadTestsFromModule

def get_tests_by_package(package):
    loader = get_tests_by_module
    return (loader(m) for m in typeutil.load_modules_of_package(package))

def parse_cmd_opt():
    import argparse
    class LogLevelAction(argparse.Action):
        def __call__(self, parser, namespaces, values, option_string=None):

            def valid_level(level):
                choices = ['DEBUG', 'WARNING', 'INFO', 'ERROR', 'FATAL', 'NOTSET']
                if level not in choices:
                    parser.error('log level must be one of: ' + str(choices))

            def translate_level(level):
                valid_level(level)
                return getattr(logging, level)

            def parse_value(value):
                name, sep, level = value.partition(':')
                if not sep:
                    level = name
                    name = 'spork'
                level = translate_level(level)
                return name, level

            namespaces.log_level.append(parse_value(values[0]))

    parser = argparse.ArgumentParser()
    parser.add_argument('-x', '--stop', default=False, action='store_true',
            help='stop running tests on first error or failure')
    parser.add_argument('-l', '--log-level', nargs=1, action=LogLevelAction,
            help='set logging level, default to spork:INFO. '
            'Multiple -l option is allowed', default=[])
    parser.add_argument('-p', '--profile', 
            help='enable profile and set report filter')
    parser.add_argument('tests', nargs='*', 
            help='package/module names that test cases resident.')

    return parser.parse_args()

def load_tests(test_names):
    def get_tests(test_name):
        if '.' in test_name:
            return get_tests_by_module(typeutil.my_import(test_name))
        else:
            return get_tests_by_package(test_name)

    tests = itertools.chain.from_iterable(get_tests(x) for x in test_names)
    return list(tests)

PROFILER_LOG = '/tmp/spork.test.profile'

def print_profile(code_prefix):
    import pstats
    stats = pstats.Stats(PROFILER_LOG)
    stats.sort_stats('cumulative')
    stats.print_stats(code_prefix, 20)

if __name__ == '__main__':
    args = parse_cmd_opt()
    enable_test_mode()
    setup_spork_log(args.log_level)

    runner = MyTestRunner(args)
    tests = load_tests(args.tests)
    if args.profile:
        import cProfile as profile
        tests = unittest.TestSuite(tests)
        profile.run('runner.run(tests)', PROFILER_LOG)
        print_profile(args.profile)
    else:
        # parallel unit test, because MySQL databasa test, can not parallel,
        # so can not enable, if setup more test database, and unit test can
        # switch test database automatically, parallel unit test is very
        # effective.
        #if os.fork() == 0:
        #    tests = tests[len(tests) // 2:]
        #else:
        #    tests = tests[:len(tests) // 2]

        tests = unittest.TestSuite(tests)
        success = runner.run(tests).wasSuccessful()
        exit(not success)

