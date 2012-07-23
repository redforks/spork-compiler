# -*- coding: utf-8 -*-

import sys, re
from traceback import format_list
from datetime import datetime

__all__ = 'TestCase', 'scan_test_classes', 'TestRunner'

def scan_test_classes(pkgname):
    ''' return all test class of package pkgname in all loaded modules'''

    from sys import modules

    pkgname += '.'
    result = []
    for mname in modules:
        if mname.startswith(pkgname):
            m = modules[mname]
            for clsname in dir(m):
                if clsname.endswith('Tests'):
                    cls = getattr(m, clsname)
                    result.append(cls)
    return result

_MAX_LENGTH = 80
def safe_repr(obj, short=False):
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if not short or len(result) < _MAX_LENGTH:
        return result
    return result[:_MAX_LENGTH] + ' [truncated]...'

class _AssertRaisesContext(object):
    def __init__(self, expected, test_case, expected_regexp=None):
        self.expected = expected
        self.failureException = AssertionError
        self.expected_regexp = expected_regexp

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            try:
                exc_name = self.expected.__name__
            except AttributeError:
                exc_name = str(self.expected)
            raise self.failureException('%s not raised' % (exc_name,))
        if exc_type != self.expected:
            return False
        self.exception = exc_value
        if self.expected_regexp is None:
            return True

        expected_regexp = self.expected_regexp
        # re.compile() is not implemented
        #if isinstance(expected_regexp, str):
            #expected_regexp = re.compile(expected_regexp)
        #if not expected_regexp.search(str(exc_value)):
        if not re.search(expected_regexp, str(exc_value)):
            raise self.failureException('"%s" does not match "%s"' %
                (expected_regexp, str(exc_value)))
        return True

class TestCase(object):
    longMessage = False
    failureException = AssertionError

    def fail(self, msg=None):
        raise self.failureException(msg)

    def assertEqual(self, expected, actual, msg=None):
        if expected != actual:
            if msg:
                raise AssertionError('expected ' + repr(expected) + \
                        ' actual ' + repr(actual) + '.\n' + msg)
            else:
                raise AssertionError('expected ' + repr(expected) + \
                        ' actual ' + repr(actual) + '.')

    def assertNotEqual(self, expected, actual, msg=''):
        if expected == actual:
            if msg:
                raise AssertionError('expected ' + repr(expected) + \
                        ' not equals ' + repr(actual) + '.\n' + msg)
            else:
                raise AssertionError('expected ' + repr(expected) + \
                        ' not equals ' + repr(actual) + '.')

    def assertSame(self, expected, actual, msg=''):
        if expected is not actual:
            if msg:
                raise AssertionError('expected same ' + repr(expected) + \
                        ' actual ' + repr(actual) + '.\n' + msg)
            else:
                raise AssertionError('expected same ' + repr(expected) + \
                        ' actual ' + repr(actual) + '.')

    def assertNotSame(self, expected, actual, msg=''):
        if expected is actual:
            raise AssertionError(msg)

    def assertTrue(self, val, msg=None):
        if not val:
            msg = self._formatMessage(msg, "%s is not True" % safe_repr(val))
            raise AssertionError(msg)

    def assertFalse(self, val, msg=None):
        if val:
            msg = self._formatMessage(msg, "%s is not False" % safe_repr(val))
            raise AssertionError(msg)

    def assertError(self, func, errcls, errmsg=None):
        try:
            func()
        except Exception as e:
            if not isinstance(e, errcls):
                raise AssertionError('expected ' + errcls.__name__ +
                        ', but ' + e.__name__ + ' raised.')
            if errmsg:
                self.assertEqual(errmsg, e.message)
            return
        raise AssertionError('expected ' + errcls.__name__ +
                ', but no exception raised.')

    def assertAlmostEqual(self, first, second, places=None, msg=None,
            delta=None):
        if first == second:
            return
        if delta is not None and places is not None:
            raise TypeError('specify delta or places not both')

        if delta is not None:
            if abs(first - second) <= delta:
                return

            standardMsg = '%s != %s within %s delta' % (safe_repr(first),
                                                        safe_repr(second),
                                                        safe_repr(delta))
        else:
            if places is None:
                places = 7

            if round(abs(second-first), places) == 0:
                return

            standardMsg = '%s != %s within %r places' % (safe_repr(first),
                                                         safe_repr(second),
                                                         places)
        msg = self._formatMessage(msg, standardMsg)
        raise self.failureException(msg)

    def assertIsNone(self, obj, msg=None):
        if obj is not None:
            standardMsg = '%s is not None' % (safe_repr(obj),)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertIsNotNone(self, obj, msg=None):
        if obj is None:
            standardMsg = 'unexpectedly None'
            self.fail(self._formatMessage(msg, standardMsg))

    def assertIsInstance(self, obj, cls, msg=None):
        if not isinstance(obj, cls):
            standardMsg = '%s is not an instance of %r' % (safe_repr(obj), cls)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertNotIsInstance(self, obj, cls, msg=None):
        if isinstance(obj, cls):
            standardMsg = '%s is an instance of %r' % (safe_repr(obj), cls)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertRaises(self, excClass, callableObj=None):
        context = _AssertRaisesContext(excClass, self)
        if callableObj is None:
            return context
        with context:
            callableObj()

    def assertRaisesRegexp(self, expected_exception, expected_regexp,
            callable_obj=None):
        context = _AssertRaisesContext(expected_exception, self,
                expected_regexp)
        if callable_obj is None:
            return context
        with context:
            callable_obj()

    def _formatMessage(self, msg, standardMsg):
        if not self.longMessage:
            return msg or standardMsg
        if msg is None:
            return standardMsg
        return '%s : %s' % (standardMsg, msg)

class TestRunner(object):
    def __init__(self, tests):
        self.tests = tests

    def run(self):
        def scan_args():
            quick_fail = False
            filter = None
            for arg in sys.argv[1:]:
                if arg == '-x':
                    quick_fail = True
                elif arg.startswith('-'):
                    pass
                else:
                    filter = arg
            return quick_fail, filter

        quick_fail, filter = scan_args()

        totalrun = 0
        fails = []
        start = datetime.now()

        def run_test(cls, method):
            try:
                o = cls()
                if hasattr(o, 'setUp'):
                    o.setUp()
                assert isinstance(o, TestCase), \
                    'test case %s is not TestCase' % o.__name__
                getattr(o, method)()
                print '.',
            except Exception as e:
                print 'F',
                fails.append([cls, method, e])
            finally:
                try:
                    if hasattr(o, 'tearDown'):
                        o.tearDown()
                except Exception as e:
                    fails.append([cls, method + ' <tearDown>', e])

        def run_case(cls):
            for name in dir(cls):
                if quick_fail and fails:
                    return

                if name.startswith('test'):
                    if filter:
                        fullname = cls.__name__ + '.' + name
                        if not fullname.startswith(filter):
                            continue

                    totalrun += 1
                    run_test(cls, name)

        for cls in self.tests:
            if quick_fail and fails:
                break

            run_case(cls)

        print 
        for idx, f in enumerate(fails):
            print str(idx + 1) + '.', f[0].__name__ + '.' + f[1], \
            f[2].__class__.__name__ + '\n', f[2].message + '\n', \
            '\n  '.join(format_list(getattr(f[2], 'stacktrace', [])))
            print

        print 
        print 'total run:', totalrun, 'fails: ', len(fails)
        span = datetime.now() - start
        span = str(span.seconds) + '.' + str(span.microseconds).rjust(6, '0')
        print 'using:', span, 'secs'
        return len(fails)

