# -*- coding: utf-8 -*-

from unittest import TestCase

class StringTests(TestCase):
    def test_concat(self):
        self.assertEqual('a', 'a' + '')
        self.assertEqual('汉bc', '汉' + 'bc')
        self.assertEqual(u'汉bc', u'汉' + u'bc')

    def test_str_constructor(self):
        self.assertEqual('', str(''))
        self.assertEqual('2', str(2))
        self.assertEqual('2.3', str(2.3))

    def test_multiply(self):
        self.assertEqual('  ', ' ' * 2)
        self.assertEqual('abcabcabc', 'abc' * 3)
        s = 'ab'
        s *= 3
        self.assertEqual('ababab', s)

    def test_mod(self):
        self.assertEqual('', '%s' % '')
        self.assertEqual('abc', '%s' % 'abc')
        self.assertEqual('1 + 2', '%d + %d' % (1, 2))
        s = '%s'
        s %= 4
        self.assertEqual('4', s)

    def test_in(self):
        self.assertTrue('a' in 'abc')
        self.assertTrue('ab' in 'abc')
        self.assertFalse('abc' in 'ab')
        self.assertFalse('a' not in 'abc')
        self.assertFalse('ab' not in 'abc')
        self.assertTrue('abc' not in 'ab')

    def test_subscription(self):
        self.assertEqual('b', 'abc'[1])
        self.assertEqual('c', 'abc'[-1])
        self.assertEqual('bc', 'abc'[1:])
        self.assertEqual('b', 'ab'[1:])
        s = '+1'
        self.assertEqual(s, s[0] + s[1:])
        self.assertEqual(s, s[0:])
        self.assertEqual('1', '-1'[1:])
        self.assertEqual('', '-1'[:0])
        self.assertEqual('12', '[12]'[1:-1])
        self.assertEqual('ac', 'abc'[::2])
        self.assertEqual('a', 'abc'[::3])
        
    def test_len(self):
        self.assertEqual(0, len(''))
        self.assertEqual(1, len('a'))
        self.assertEqual(3, len(u'a汉子'))

    def test_min_max(self):
        self.assertEqual('a', min('abc'))
        self.assertEqual('c', max('abc'))

    def test_startswith(self):
        self.assertTrue(''.startswith(''))
        self.assertTrue('abc'.startswith(''))
        self.assertTrue('abc'.startswith('a'))
        self.assertTrue(u'汉子'.startswith(u'汉'))
        self.assertFalse(''.startswith('a'))

    def test_endswith(self):
        self.assertTrue(''.endswith(''))
        self.assertTrue('a'.endswith(''))
        self.assertTrue('abc'.endswith('c'))
        self.assertTrue(u'汉子'.endswith(u'子'))
        self.assertFalse(''.endswith('a'))

    def test_capitalize(self):
        self.assertEqual('What a lovely day.', 
            'what a lovely day.'.capitalize())
        self.assertEqual('Aaa', 'AAA'.capitalize())

    def test_center(self):
        self.assertEqual('a', 'a'.center(1), '1');
        self.assertEqual(' a ', 'a'.center(3), '3');
        self.assertEqual(u' 汉 ', u'汉'.center(3));

    def test_count(self):
        e = getattr(self, 'assertEqual')
        e(0, 'abc'.count('d'))
        e(1, 'abc'.count('a'))
        e(2, 'abcab'.count('ab'))

    def test_index(self):
        self.assertEqual(0, 'a'.index('a'))
        self.assertEqual(2, 'bca'.index('a'))
        self.assertError(lambda: 'a'.index('b'), ValueError)
        self.assertEqual(3, '/ab/c'.index('/', 2))
        self.assertEqual(3, '/ab/c'.index('/', 3))

    def test_isalnum(self):
        self.assertTrue('1234567890abcdefghijklmnopqrstuvwxyz'.isalnum())
        self.assertTrue('ABCDEFGHIJKLMNOPQRSTUVWXYZ'.isalnum())
        self.assertFalse(''.isalnum())
        self.assertFalse('334@3'.isalnum())

    def test_isalpha(self):
        self.assertFalse(''.isalpha())
        self.assertFalse('abc1233dd'.isalpha())
        self.assertTrue('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQ'.isalpha())

    def test_isdigit(self):
        self.assertTrue('1234567890'.isdigit())
        self.assertFalse('1234567890a'.isdigit())
        self.assertFalse(''.isdigit())

    def test_islower(self):
        self.assertFalse(''.islower())
        self.assertTrue('1a'.islower())
        self.assertFalse('aA'.islower())

    def test_isspace(self):
        self.assertTrue(' '.isspace())
        self.assertFalse(''.isspace())
        self.assertFalse(' \ta'.isspace())

    def test_istitle(self):
        self.assertFalse(''.istitle())
        self.assertFalse('abc cd'.istitle())
        self.assertTrue('Abc'.istitle())
        self.assertTrue(' Abc '.istitle())
        self.assertTrue('Abc Cde'.istitle())
        self.assertFalse('Abc cde'.istitle())
        self.assertFalse('aAbc'.istitle())

    def test_isupper(self):
        self.assertFalse(''.isupper())
        self.assertFalse('1a'.isupper())
        self.assertFalse('aA'.isupper())
        self.assertTrue('ABCDE E1'.isupper())

    def test_join(self):
        self.assertEqual('', ' '.join([]))
        self.assertEqual('abc', ''.join('abc'))
        self.assertEqual('a b c', ' '.join('abc'))
        self.assertEqual('abc;cd', ';'.join(['abc', 'cd']))
        self.assertRaises(TypeError, lambda: ''.join(1))

    def test_ljust(self):
        self.assertEqual('abc', 'abc'.ljust(2))
        self.assertEqual('abc ', 'abc'.ljust(4))
        self.assertEqual('abc::', 'abc'.ljust(5, ':'))

    def test_lower(self):
        self.assertEqual('abc', 'aBc'.lower())

    def test_lstrip(self):
        self.assertEqual('abc ', '   abc '.lstrip())
        self.assertEqual('bc ', 'abc '.lstrip('a'))

    def test_replace(self):
        self.assertEqual('', ''.py_replace('a', 'A'))
        self.assertEqual('AbcAd', 'abcad'.py_replace('a', 'A'))

    def test_rfind(self):
        self.assertEqual(-1, ''.rfind('a'))
        self.assertEqual(3, 'aaaa'.rfind('a'))

    def test_rindex(self):
        self.assertEqual(3, 'aaaa'.rindex('a'))
        self.assertError(lambda: 'a'.rindex('b'), ValueError)

    def test_rjust(self):
        self.assertEqual('abc', 'abc'.rjust(1))
        self.assertEqual(' abc', 'abc'.rjust(4), '2')
        self.assertEqual('::abc', 'abc'.rjust(5, ':'), '3')

    def test_rstrip(self):
        self.assertEqual(' abc', ' abc '.rstrip())
        self.assertEqual(' ab', ' abc'.rstrip('c'))

    def test_split(self):
        self.assertEqual(['a'], 'a'.py_split())
        self.assertEqual(['a', 'b'], ' a\tb '.py_split())
        self.assertEqual(['a', 'b'], 'a:b'.py_split(':'))
        self.assertEqual(['a', 'b:c'], 'a:b:c'.py_split(':', 1))
        self.assertEqual(['a:b:c'], 'a:b:c'.py_split(':', 0))
        self.assertEqual(['abc'], 'abc'.py_split(':'))
        self.assertEqual([''], ''.py_split(':'))
        self.assertEqual([''], ''.py_split(':', 0))
        self.assertEqual([], ''.py_split())
        self.assertEqual([''], ''.py_split('\n'))

    def test_splitlines(self):
        self.assertEqual(['a'], 'a'.splitlines())
        self.assertEqual(['a', 'b'], 'a\nb'.splitlines())
        msg = 'keepends argument of str.splitlines() is not supported'
        self.assertError(lambda:'a\nb'.splitlines(True), NotImplementedError,
                msg)

    def test_strip(self):
        self.assertEqual('', '  \t '.strip())
        self.assertEqual('a b', '  a b\t '.strip())

    def test_swapcase(self):
        self.assertEqual('', ''.swapcase())
        self.assertEqual('12#', '12#'.swapcase())
        self.assertEqual('12aBc', '12AbC'.swapcase())

    def test_title(self):
        self.assertEqual('', ''.title())
        self.assertEqual('A', 'a'.title())
        self.assertEqual('Ab1  Cd*', 'ab1  cd*'.title())
        self.assertEqual('Aaa', 'AAA'.title())

    def test_translate(self):
        self.assertError(lambda: ''.translate(' ' * 256),
            NotImplementedError, 'str.translate() is not supported.')

    def test_upper(self):
        self.assertEqual('AER34', 'aeR34'.upper())

    def test_zfill(self):
        self.assertEqual('abc', 'abc'.zfill(1))
        self.assertEqual('00a', 'a'.zfill(3))
        self.assertEqual('001', '1'.zfill(3))
        self.assertEqual('-01', '-1'.zfill(3))
