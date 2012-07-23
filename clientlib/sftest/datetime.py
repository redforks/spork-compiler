# -*- coding: utf-8 -*-
from sfunittest import TestCase
from datetime import date, MINYEAR, MAXYEAR, timedelta, datetime, \
    time
from datetime_test import setnow

class DateTests(TestCase):
    def test_constructor(self):
        def round(y, m, d):
            v = date(y, m, d)
            self.assertEqual(y, v.year)
            self.assertEqual(m, v.month)
            self.assertEqual(d, v.day)
        round(2009, 1, 2)
        round(2009, 12, 31)
        round(2009, 10, 1)
        round(2009, 10, 31)
        round(2009, 10, 24)
        round(2008, 2, 29)
        round(2010, 1, 1)

    def test_eq(self):
        d = date(2009, 10, 26)
        self.assertEqual(d, d)
        self.assertEqual(d, date(2009, 10, 26))
        self.assertNotEqual(d, date(2009, 10, 25))

    def test_class_attr(self):
        self.assertEqual(1970, MINYEAR)
        self.assertEqual(9999, MAXYEAR)
        self.assertEqual(date(1970, 1, 1), date.min)
        self.assertEqual(date(9999, 12, 31), date.max)
        self.assertEqual(timedelta(1), date.resolution)

    def test_cmp(self):
        d1 = date(2009, 12, 31)
        d2 = date(2010, 1, 1)
        assert d1 < d2
        assert d1 <= d2
        assert d2 > d1
        assert d2 >= d1

    def test_str(self):
        self.assertEqual('2007-01-02', str(date(2007, 1, 2)))

    def test_repr(self):
        self.assertEqual('datetime.date(2007, 1, 2)', repr(date(2007, 1, 2)))

    def test_replace(self):
        d = date(2009, 10, 27)
        v = d.replace(2008, 1, 3)
        self.assertEqual(date(2008, 1, 3), v)

        v = d.replace(year = 2007)
        self.assertEqual(date(2007, 10, 27), v)

        v = d.replace(month = 2)
        self.assertEqual(date(2009, 2, 27), v)

        v = d.replace(day = 2)
        self.assertEqual(date(2009, 10, 2), v)

    def test_ordinal(self):
        d = date(2009, 10, 27)
        self.assertEqual(d, date.fromordinal(d.toordinal()))

    def test_setnow(self):
        setnow(datetime(2009, 12, 29))
        self.assertEqual(date(2009, 12, 29), date.today())

    def _test_today(self):
        self.assertEqual(date(2009, 12, 28), date.today())

    def test_fromtimestamp(self):
        self.assertEqual(date(1970, 1, 1), date.fromtimestamp(0))
        self.assertEqual(date(1970, 1, 1), date.fromtimestamp(2))
        self.assertEqual(date(1970, 1, 2), date.fromtimestamp(3600*24))

    def test_weekday(self):
        d = date(2009, 10, 27)
        self.assertEqual(1, d.weekday())
        d = date(1970, 1, 1)
        self.assertEqual(3, d.weekday())

    def test_isoweekday(self):
        d = date(2009, 10, 27)
        self.assertEqual(2, d.isoweekday())
        d = date(1970, 1, 1)
        self.assertEqual(4, d.isoweekday())

    def test_isoformat(self):
        self.assertEqual('2009-10-28', date(2009, 10, 28).isoformat())
        self.assertEqual('2009-01-02', date(2009, 1, 2).isoformat())

    def test_ctime(self):
        self.assertEqual('Wed Oct 28 2009', date(2009, 10, 28).ctime())

    def test_strftime(self):
        self.assertError(lambda: date(2009, 10, 28).strftime('%z'), 
            NotImplementedError)

    def test_add(self):
        self.assertEqual(date(2009, 10, 29), date(2009, 10, 28) +
                timedelta(days=1))
        self.assertEqual(date(2009, 10, 27), date(2009, 10, 28) +
                timedelta(days=-1))

    def test_sub(self):
        self.assertEqual(date(2009, 10, 26), date(2009, 10, 28) -
                timedelta(days=2))
        self.assertEqual(timedelta(2), date(2009, 10, 28) -
                date(2009, 10, 26))
        self.assertEqual(timedelta(-3), date(2009, 10, 25) -
                date(2009, 10, 28))

    def test_hash(self):
        self.assertEqual(hash(date.min), hash(date.min))
        self.assertEqual(hash(date.min), hash(date(MINYEAR, 1, 1)))
        self.assertNotEqual(hash(date.min), hash(date.max))

    def test_bool(self):
        self.assertSame(True, bool(date.min))

class TimeDeltaTests(TestCase):
    def test_constructor(self):
        def do_test(days, seconds, microseconds, *args):
            t = timedelta(*args)
            self.assertEqual(days, t.days, str(t))
            self.assertEqual(seconds, t.seconds, str(t))
            self.assertEqual(microseconds, t.microseconds, str(t))

        do_test(0, 0, 0)
        do_test(0, 0, 1, 0, 0, 1)
        do_test(0, 1, 0, 0, 1)
        do_test(1, 0, 0, 1)
        do_test(1, 2, 0, 1, 2)
        do_test(1, 2, 3, 1, 2, 3)
        do_test(1, 2, 1003, 1, 2, 3, 1)
        do_test(1, 602, 1003, 1, 2, 3, 1, 10)
        do_test(1, 3602, 1003, 1, 2, 3, 1, 0, 1)
        do_test(8, 3602, 1003, 1, 2, 3, 1, 0, 1, 1)

    def test_str(self):
        def do_test(expected, days, seconds, microseconds):
            t = timedelta(days, seconds, microseconds)
            self.assertEqual(expected, str(t))

        do_test('0:00:00', 0, 0, 0)
        do_test('0:00:00.000001', 0, 0, 1)
        do_test('0:00:00.000100', 0, 0, 100)
        do_test('0:00:01', 0, 1, 0)
        do_test('0:01:00', 0, 60, 0)
        do_test('1:00:00', 0, 3600, 0)
        do_test('1 day, 0:00:00', 1, 0, 0)
        do_test('2 days, 0:00:00', 2, 0, 0)

    def test_repr(self):
        def do_test(expected, days, seconds, microseconds):
            t = timedelta(days, seconds, microseconds)
            self.assertEqual(expected, repr(t))

        do_test('datetime.timedelta(0)', 0, 0, 0)
        do_test('datetime.timedelta(0, 1)', 0, 1, 0)
        do_test('datetime.timedelta(0, 0, 1)', 0, 0, 1)

    def test_eq(self):
        self.assertEqual(timedelta(), timedelta())
        self.assertNotEqual(timedelta(1), timedelta())

    def test_cmp(self):
        assert timedelta.max >= timedelta.min
        assert timedelta.max > timedelta.min

    def test_classattr(self):
        self.assertEqual(timedelta(-9999), timedelta.min)
        self.assertEqual(timedelta(9999, 86399, 999999), timedelta.max)
        self.assertEqual(timedelta.resolution, timedelta(0, 0, 1))

    def test_abs(self):
        self.assertEqual(timedelta(1), abs(timedelta(1)))
        self.assertEqual(timedelta(1), abs(timedelta(-1)))

    def test_add(self):
        self.assertEqual(timedelta(), timedelta(1) + timedelta(-1))
        self.assertEqual(timedelta(33), timedelta(30) + timedelta(3))

    def test_sub(self):
        self.assertEqual(timedelta(), timedelta(1) - timedelta(1))

    def test_neg(self):
        self.assertEqual(timedelta(), -timedelta())
        self.assertEqual(timedelta(1), -timedelta(-1))

    def test_mul(self):
        self.assertEqual(timedelta(), timedelta() * 3)
        self.assertEqual(timedelta(3), timedelta(1) * 3)

    def test_div(self):
        self.assertEqual(timedelta(1), timedelta(3) / 3)
        self.assertEqual(timedelta(1), timedelta(3) // 3)

    def test_bool(self):
        self.assertSame(True, bool(timedelta(1)))
        self.assertSame(False, bool(timedelta()))

    def test_hash(self):
        self.assertEqual(hash(timedelta.min), hash(timedelta.min))
        self.assertEqual(hash(timedelta(1, 2, 3)), hash(timedelta(1, 2, 3)))
        self.assertNotEqual(hash(timedelta.min), hash(timedelta.max))

class DateTimeTests(TestCase):
    def test_constructor(self):
        def do_test(year, month, day, *args):
            attrs = ['hour', 'minute', 'second', 'microsecond']
            dt = datetime(year, month, day, *args)
            self.assertEqual(year, dt.year)
            self.assertEqual(month, dt.month)
            self.assertEqual(day, dt.day)

            for expected, attr in zip(args, attrs):
                actual = getattr(dt, attr)
                self.assertEqual(expected, actual)
            
            for attr in attrs[len(args):]:
                self.assertEqual(0, getattr(dt, attr))

        do_test(2009, 10, 30)
        do_test(2009, 10, 30, 1)
        do_test(2009, 10, 30, 1, 2)
        do_test(2009, 10, 30, 1, 2, 3)
        do_test(2009, 10, 30, 1, 2, 3, 100)

    def test_eq(self):
        self.assertEqual(datetime(2009, 10, 30), datetime(2009, 10, 30))
        self.assertNotEqual(datetime(2009, 11, 30), datetime(2009, 10, 30))
        self.assertNotEqual(datetime(2009, 10, 30, 1), datetime(2009, 10, 30))
        self.assertNotEqual(datetime(2012, 2, 1), date(2012, 2, 1))

    def test_cmp(self):
        assert datetime(2009, 10, 30) > datetime(2009, 10, 29)
        assert datetime(2009, 10, 29) < datetime(2009, 10, 30)
        assert datetime(2009, 10, 29, 1) > datetime(2009, 10, 29)
        assert datetime(2009, 10, 29) < datetime(2009, 10, 29, 1)

    def test_str(self):
        def do_test(expected, *args):
            self.assertEqual(expected, str(datetime(*args)))
        do_test('2009-10-30 00:00:00', 2009, 10, 30)
        do_test('2009-10-30 01:02:03', 2009, 10, 30, 1, 2, 3)
        do_test('2009-10-30 01:02:03.000001', 2009, 10, 30, 1, 2, 3, 1)

    def test_repr(self):
        def do_test(expected, *args):
            self.assertEqual(expected, repr(datetime(*args)))

        do_test('datetime.datetime(2009, 10, 30)', 2009, 10, 30)
        do_test('datetime.datetime(2009, 10, 30, 1)', 2009, 10, 30, 1)
        do_test('datetime.datetime(2009, 10, 30, 1, 2, 3, 4)', 
                2009, 10, 30, 1, 2, 3, 4)

    def test_classattr(self):
        self.assertEqual(datetime(MINYEAR, 1, 1), datetime.min)
        self.assertEqual(datetime(MAXYEAR, 12, 31, 23, 59, 59, 999999), 
                datetime.max)
        self.assertEqual(timedelta(0, 0, 1), datetime.resolution)

    def _test_today(self):
        today = datetime.today()
        self.assertEqual(date(2009, 11, 1), today.date())
        print str(today.time())

    def _test_now(self):
        today = datetime.now()
        self.assertEqual(date(2009, 11, 1), today.date())
        print today, today.time()
        self.assertNotEqual(0, today.microsecond)

    def test_timestamp(self):
        self.assertEqual(datetime(1970, 1, 1, 8), datetime.fromtimestamp(0))
        self.assertEqual(datetime(1970, 1, 1), datetime.utcfromtimestamp(0))
        self.assertEqual(datetime(1970, 1, 1, 0, 0, 1), 
                datetime.utcfromtimestamp(1))

    def test_totimestamp(self):
        self.assertEqual(0, datetime(1970, 1, 1, 8).totimestamp())
        self.assertEqual(1, datetime(1970, 1, 1, 8, 0, 1).totimestamp())
        self.assertEqual(3600 * 24, datetime(1970, 1, 2, 8).totimestamp())

    def test_ordinal(self):
        o = datetime(2009, 11, 1, 16, 2).toordinal()
        self.assertEqual(datetime(2009, 11, 1), datetime.fromordinal(o))

    def test_date(self):
        self.assertEqual(date(2009, 11, 1), datetime(2009, 11, 1, 1, 2).date())
        self.assertEqual(datetime(2009, 11, 1, 1, 2).date(), date(2009, 11, 1))

    def test_time(self):
        self.assertEqual(time(1, 2), datetime(2009, 11, 1, 1, 2).time())

    def test_combine(self):
        self.assertEqual(datetime(2009, 11, 1, 16, 11), datetime.combine(
            date(2009, 11, 1), time(16, 11)))

    def test_strptime(self):
        self.assertError(lambda: datetime.strptime('', '%z'), NotImplementedError)

    def test_add(self):
        self.assertEqual(datetime(2009, 11, 1), 
                datetime(2009, 10, 31) + timedelta(1))
        self.assertEqual(datetime(2009, 11, 1, 1), 
                datetime(2009, 10, 31) + timedelta(1, 3600))
        self.assertEqual(datetime(2009, 11, 1),
                datetime(2009, 11, 1, 0, 0, 1) + timedelta(0, -1))
        self.assertEqual(datetime(2009, 10, 31, 23, 59, 59),
                datetime(2009, 11, 1) + timedelta(0, -1))
        self.assertEqual(datetime(2009, 11, 2),
                datetime(2009, 11, 1, 23, 59, 59, 999999) + timedelta(0, 0, 1))

    def test_sub(self):
        self.assertEqual(timedelta(0),
                datetime(2009, 11, 1, 2) - datetime(2009, 11, 1, 2))
        self.assertEqual(timedelta(1, 1, 0), 
            datetime(2009, 11, 1, 0, 0, 2) - datetime(2009, 10, 31, 0, 0, 1))
        self.assertEqual(timedelta(0, -1, 0),
            datetime(2009, 11, 1, 0, 0, 1) - datetime(2009, 11, 1, 0, 0, 2))
        self.assertEqual(datetime(2009, 11, 1),
            datetime(2009, 11, 1, 0, 0, 1) - timedelta(0, 1, 0))

    def test_replace(self):
        d = datetime(2009, 10, 27)
        v = d.replace(2008, 1, 3)
        self.assertEqual(datetime(2008, 1, 3), v)

        v = d.replace(year = 2007)
        self.assertEqual(datetime(2007, 10, 27), v)

        v = d.replace(month = 2)
        self.assertEqual(datetime(2009, 2, 27), v)

        v = d.replace(day = 2)
        self.assertEqual(datetime(2009, 10, 2), v)

        t = datetime(2009, 11, 1, 0, 1, 2)
        eq = self.assertEqual
        eq(datetime(2009, 11, 2, 1, 2, 3, 4), 
                t.replace(2009, 11, 2, 1, 2, 3, 4))
        eq(datetime(2009, 11, 1, 3, 1, 2), t.replace(hour = 3))
        eq(datetime(2009, 11, 1, 0, 3, 2), t.replace(minute = 3))
        eq(datetime(2009, 11, 1, 0, 1, 3), t.replace(second = 3))
        eq(datetime(2009, 11, 1, 0, 1, 2, 3), t.replace(microsecond = 3))

    def test_weekday(self):
        d = datetime(2009, 10, 27)
        self.assertEqual(1, d.weekday())
        d = datetime(1970, 1, 1)
        self.assertEqual(3, d.weekday())

    def test_isoweekday(self):
        d = datetime(2009, 10, 27)
        self.assertEqual(2, d.isoweekday())
        d = datetime(1970, 1, 1)
        self.assertEqual(4, d.isoweekday())

    def test_isoformat(self):
        self.assertEqual('2009-10-28 00:00:00', 
                datetime(2009, 10, 28).isoformat())
        self.assertEqual('2009-01-02 00:00:00',
                datetime(2009, 1, 2).isoformat())
        self.assertEqual('2009-01-02 03:04:05.000006',
                datetime(2009, 1, 2, 3, 4, 5, 6).isoformat())

    def test_ctime(self):
        self.assertEqual('Wed Oct 28 2009', datetime(2009, 10, 28).ctime())
        self.assertEqual('Wed Oct 28 2009 01:02:00', datetime(2009, 10, 28, 1, 2).ctime())

    def test_strftime(self):
        self.assertError(lambda: datetime.min.strftime('%z'),
                NotImplementedError)

    def test_hash(self):
        self.assertEqual(hash(datetime.min), hash(datetime.min))
        self.assertEqual(hash(datetime(2009, 11, 2)), 
                hash(datetime(2009, 11, 2)))
        self.assertNotEqual(hash(datetime(2009, 11, 2)), 
                hash(datetime(2009, 11, 2, 0, 0, 1)))

class TimeTests(TestCase):
    def test_constructor(self):
        def do_test(hour, *args):
            t = time(hour, *args)
            attrs = ['minute', 'second', 'microsecond']
            self.assertEqual(hour, t.hour)
            for expected, attr in zip(args, attrs):
                self.assertEqual(expected, getattr(t, attr))

            for attr in attrs[len(args):]:
                self.assertEqual(0, getattr(t, attr))

        do_test(1)
        do_test(23)
        do_test(2, 1)
        do_test(2, 1, 3)
        do_test(2, 1, 3, 10000)

    def test_eq(self):
        self.assertEqual(time(1), time(1))
        self.assertNotEqual(time(2), time(0))

    def test_cmp(self):
        assert time(1) >= time(1)
        assert time(1) <= time(1)
        assert time(2) >= time(1)
        assert time(1) <= time(2)

        assert not time(1) > time(1)
        assert not time(2) < time(1)

    def test_classattr(self):
        self.assertEqual(time(0), time.min)
        self.assertEqual(time(23, 59, 59, 999999), time.max)
        self.assertEqual(timedelta(0, 0, 1), time.resolution)

    def test_str(self):
        def do_test(expected, hour, minute = 0, second = 0, microsecond = 0):
            self.assertEqual(expected, str(time(hour, minute, second,
                microsecond)))
        do_test('01:00:00', 1)
        do_test('01:02:03', 1, 2, 3)
        do_test('01:02:03.000001', 1, 2, 3, 1)

    def test_repr(self):
        def do_test(expected, hour, minute = 0, second = 0, microsecond = 0):
            self.assertEqual(expected, repr(time(hour, minute, second,
                microsecond)))

        do_test('datetime.time(1)', 1)
        do_test('datetime.time(1, 2)', 1, 2)
        do_test('datetime.time(1, 2, 3)', 1, 2, 3)
        do_test('datetime.time(1, 2, 3, 4)', 1, 2, 3, 4)

    def test_replace(self):
        t = time(0, 1, 2)
        self.assertEqual(time(1, 2, 3, 4), t.replace(1, 2, 3, 4))
        self.assertEqual(time(3, 1, 2), t.replace(hour = 3))
        self.assertEqual(time(0, 3, 2), t.replace(minute = 3))
        self.assertEqual(time(0, 1, 3), t.replace(second = 3))
        self.assertEqual(time(0, 1, 2, 3), t.replace(microsecond = 3))

    def test_isoformat(self):
        def do_test(expected, hour, minute=0, second=0, microsecond=0):
            t = time(hour, minute, second, microsecond)
            self.assertEqual(expected, t.isoformat())
        do_test('01:00:00', 1)
        do_test('01:02:03', 1, 2, 3)
        do_test('01:02:03.000001', 1, 2, 3, 1)

    def test_strftime(self):
        self.assertError(lambda: time.min.strftime('%z'), NotImplementedError)

    def test_bool(self):
        self.assertSame(True, bool(time.max))
        self.assertSame(False, bool(time.min))

    def test_hash(self):
        self.assertEqual(hash(time.min), hash(time.min))
        self.assertEqual(hash(time(1)), hash(time(1)))
        self.assertNotEqual(hash(time(1, 2, 3)), hash(time(1, 2, 4)))
