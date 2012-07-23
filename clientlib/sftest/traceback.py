# -*- coding: utf-8 -*-

from unittest import TestCase

from traceback import extract_stack, format_stack, format_list

class TracebackTests(TestCase):
    def valid_list(self, expected, actual):
        for i in range(len(expected)):
            self.assertEqual(expected[i], actual[i])
        self.assertEqual(len(expected), len(actual), 'len')

    def _test(self):
        stack = extract_stack()
        expected = [
            'File "sftest/tests.py", line -1 jsline 20',
            '    n/a',
            'File "unittest.py", line 76 jsline 227',
            '    getattr(o, name)()',
            'File "__builtin__.py", line 375 jsline 724',
            '    return method.apply(obj,args);',
            'File "sftest/traceback.py", line 14 jsline 50',
            '    stack = extract_stack()',
            '', ''
            ]
        actual = format_list(stack)
        print '\n'.join(actual)
        self.assertEqual(expected, actual)
        self.valid_list(expected, actual)

    def _test_format_stack(self):
        expected = [
            'File "sftest/tests.py", line -1 jsline 20',
            '    n/a',
            'File "unittest.py", line 76 jsline 227',
            '    getattr(o, name)()',
            'File "__builtin__.py", line 375 jsline 724',
            '    return method.apply(obj,args);',
            'File "sftest/traceback.py", line 39 jsline 67',
            '    actual = format_stack()',
            ]
        actual = format_stack()
        self.valid_list(expected, actual)

    def _test_exception_stack(self):
        try:
            assert False
        except AssertionError as e:
            expected = [
                'File "sftest/tests.py", line -1 jsline 20',
                '    n/a',
                'File "unittest.py", line 76 jsline 227',
                '    getattr(o, name)()',
                'File "__builtin__.py", line 375 jsline 724',
                '    return method.apply(obj,args);',
                'File "sftest/traceback.py", line 44 jsline 82',
                '    assert False',
                'File "__builtin__.py", line 14 jsline 22', 
                "    raise AssertionError(msg or '')"
                ]
            actual = format_list(e.stacktrace)
            self.valid_list(expected, actual)

