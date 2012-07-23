# -*- coding: utf-8 -*-
from __spork__ import JS

MINYEAR = 1970
MAXYEAR = 9999

__YEAR_PART = 1
__MONTH_PART = 2
__DAY_PART = 3

__DAY_PER_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
__LEAP_MONTH_DAYS = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

__FOUR_YEAR_DAYS = 365 + 365 + 365 + 366

def month_days_from_year(month_days):
    result = []
    result.append(0)
    days = 0
    for d in month_days:
        days += d
        result.append(days)
    return result

__MONTH_DAYS_FROM_YEAR = month_days_from_year(__DAY_PER_MONTH)
__LEAPMONTH_DAYS_FROM_YEAR = month_days_from_year(__LEAP_MONTH_DAYS)
del month_days_from_year

def __is_leap_year(year):
    return year % 4 == 0

def __absolute_days(year, month, day):
    month_days = __LEAPMONTH_DAYS_FROM_YEAR if __is_leap_year(year) else \
        __MONTH_DAYS_FROM_YEAR
    result = month_days[month - 1]
    y = year - MINYEAR
    result += y // 4 * __FOUR_YEAR_DAYS
    y %= 4
    result += 365 * y
    return result + (day if y > 2 else day - 1)

def __pad(v, width):
    return str(v).rjust(width, '0')

class _valbase(object):
    def __cmp__(self, other):
        if self.__class__ is not other.__class__:
            return False
        return self.__val - other.__val

    def __nonzero__(self):
        return self.__val != 0

    def __hash__(self):
        return self.__val

if __debug__:
    _test_now = None

class date(_valbase):
    def __init__(self, year, month, day):
        self.__val = __absolute_days(year, month, day)

    @property
    def year(self):
        return self.__get_part(__YEAR_PART)

    def __nonzero__(self):
        return True

    def __get_part(self, part):
        leapYear = False
        daysInYear = self.__val % __FOUR_YEAR_DAYS
        if daysInYear >= 365 + 365 + 366:
            daysInYear -= 365 + 365 + 366
            year = 3
        elif daysInYear >= 365 + 365:
            leapYear = True
            daysInYear -= 365 + 365
            year = 2
        elif daysInYear >= 365:
            daysInYear -= 365
            year = 1
        else:
            year = 0
        if part == __YEAR_PART:
            return year + MINYEAR + (self.__val // __FOUR_YEAR_DAYS) * 4;

        monthDaysFromYear = __LEAPMONTH_DAYS_FROM_YEAR \
                if leapYear else __MONTH_DAYS_FROM_YEAR;
        lastm = 0
        for i, m in enumerate(monthDaysFromYear):
            if m > daysInYear:
                if part == __DAY_PART:
                    return daysInYear - lastm + 1
                else:
                    return i
            lastm = m

    @property
    def month(self):
        return self.__get_part(__MONTH_PART)

    @property
    def day(self):
        return self.__get_part(__DAY_PART)

    def replace(self, year = None, month = None, day = None):
        return date(year or self.year, month or self.month, day or self.day)

    def __str__(self):
        return '-'.join([str(self.year), __pad(self.month, 2), __pad(self.day,
            2)])

    def _repr_inner(self):
        return self.year + ', ' + self.month + ', ' + self.day

    def __repr__(self):
        return 'datetime.date(' + self._repr_inner() + ')'

    def toordinal(self):
        return self.__val + 719163

    @staticmethod
    def fromordinal(ordinal):
        ordinal -= 719163
        result = date(1, 1, 1)
        result.__val = ordinal
        return result

    @staticmethod
    def today():
        if __debug__:
            if _test_now:
                return _test_now.date()
        d = JS('new Date()')
        return date(d.getFullYear(), d.getMonth() + 1, d.getDate())

    @staticmethod
    def _timestamp_to_val(timestamp):
        return timestamp // __SECONDS_A_DAY

    @staticmethod
    def fromtimestamp(timestamp):
        result = date(1, 1, 1)
        result.__val = date._timestamp_to_val(timestamp)
        return result

    def weekday(self):
        return (self.__val + 3) % 7

    def isoweekday(self):
        return self.weekday() + 1

    def ctime(self):
        y, m, d = self.year, self.month, self.day
        return JS('new Date(y, m - 1, d).toDateString()')

    def strftime(self, format):
        raise NotImplementedError(
                'strftime() method on date object is not implemented.')

    isoformat = __str__

    def __add__(self, delta):
        return date.fromordinal(self.toordinal() + delta.days)

    def __sub__(self, other):
        if isinstance(other, timedelta):
            return date.fromordinal(self.toordinal() - other.days)
        else:
            return timedelta(self.__val - other.__val)

date.min = date(MINYEAR, 1, 1)
date.max = date(MAXYEAR, 12, 31)

__MICRO_SECS_A_SEC = 1000000 
__MICRO_SECS_A_DAY = __MICRO_SECS_A_SEC * 3600 * 24
class timedelta(_valbase):
    def __init__(self, days=0, seconds=0, microseconds=0, milliseconds=0,
            minutes=0, hours=0, weeks=0):
        seconds += minutes * 60 + hours * 3600
        days += weeks * 7
        microseconds += milliseconds * 1000
        self.__val = days * __MICRO_SECS_A_DAY + seconds * __MICRO_SECS_A_SEC\
                + microseconds

    @property
    def days(self):
        return self.__val // __MICRO_SECS_A_DAY

    @property
    def seconds(self):
        return self.__val % __MICRO_SECS_A_DAY // __MICRO_SECS_A_SEC

    def total_seconds(self):
        return self.__val // __MICRO_SECS_A_SEC

    @property
    def microseconds(self):
        return self.__val % __MICRO_SECS_A_SEC

    def __str__(self):
        microseconds = self.microseconds
        seconds = self.__val // __MICRO_SECS_A_SEC
        minute = seconds // 60
        seconds %= 60
        hour = minute // 60 % 24
        minute %= 60
        days = self.days

        if days == 0:
            result = ''
        elif days == 1:
            result = str(days) + ' day, '
        else:
            result = str(days) + ' days, '

        result += str(hour) + ':' + __pad(minute, 2) + ':' + __pad(seconds, 2)

        if microseconds:
            result += '.' + __pad(microseconds, 6)
        return result

    def __repr__(self):
        days = self.days
        seconds = self.seconds
        microseconds = self.microseconds

        result = 'datetime.timedelta(' + str(days)
        if microseconds:
            result += ', ' + str(seconds) + ', ' + str(microseconds)
        elif seconds:
            result += ', ' + str(seconds)
        return result + ')'

    def __abs__(self, other):
        if self.__val >= 0:
            return self
        else:
            return timedelta(0, 0, -self.__val)

    def __add__(self, other):
        return timedelta(0, 0, self.__val + other.__val)

    def __sub__(self, other):
        return timedelta(0, 0, self.__val - other.__val)

    def __neg__(self):
        return timedelta(0, 0, -self.__val)

    def __mul__(self, other):
        return timedelta(0, 0, self.__val * other)

    def __div__(self, other):
        return timedelta(0, 0, self.__val // other)

    __floordiv__ = __div__

timedelta.min = timedelta(-9999)
timedelta.max = timedelta(9999, 24 * 3600 - 1, 999999)
timedelta.resolution = timedelta(0, 0, 1)
date.resolution = timedelta(1)

__MICRO_SECS_A_MIN = 60 * __MICRO_SECS_A_SEC
__MICRO_SECS_A_HOUR = 60 * __MICRO_SECS_A_MIN

class time(_valbase):
    def __init__(self, hour, minute=0, second=0, microsecond=0):
        self.__val = hour * __MICRO_SECS_A_HOUR + minute * __MICRO_SECS_A_MIN \
                + second * __MICRO_SECS_A_SEC + microsecond

    @property
    def hour(self):
        return self.__val // __MICRO_SECS_A_HOUR

    @property
    def minute(self):
        return self.__val % __MICRO_SECS_A_HOUR // __MICRO_SECS_A_MIN

    @property
    def second(self):
        return self.__val % __MICRO_SECS_A_MIN // __MICRO_SECS_A_SEC

    @property
    def microsecond(self):
        return self.__val % __MICRO_SECS_A_SEC

    def replace(self, hour=None, minute=None, second=None, microsecond=None):
        return time(hour or self.hour, minute or self.minute, 
                second or self.second, microsecond or self.microsecond)

    def __str__(self):
        result = __pad(self.hour, 2) + ':' + __pad(self.minute, 2) + ':' + \
            __pad(self.second, 2)
        if self.microsecond:
            result += '.' + __pad(self.microsecond, 6)
        return result

    def _repr_inner(self):
        result = str(self.hour)
        if self.microsecond:
            result += ', ' + str(self.minute) + ', ' + \
                    str(self.second) + ', ' + str(self.microsecond)
        elif self.second:
            result += ', ' + str(self.minute) + ', ' + str(self.second)
        elif self.minute:
            result += ', ' + str(self.minute)
        return result

    def __repr__(self):
        return 'datetime.time(' + self._repr_inner() + ')'

    def strftime(self, format):
        raise NotImplementedError(
                'strftime() method on date object is not implemented.')

    isoformat = __str__

time.min = time(0)
time.max = time(23, 59, 59, 999999)
time.resolution = timedelta.resolution

__SECONDS_A_DAY = 3600 * 24

class datetime(date):
    def __init__(self, year, month, day, hour=0, minute=0, second=0, 
            microsecond=0):
        super(datetime, self).__init__(year, month, day)
        self.__time = time(hour, minute, second, microsecond)

    @property
    def hour(self):
        return self.__time.hour

    @property
    def minute(self):
        return self.__time.minute

    @property
    def second(self):
        return self.__time.second

    @property
    def microsecond(self):
        return self.__time.microsecond

    def __cmp__(self, other):
        result = super(datetime, self).__cmp__(other)
        if result == 0:
            return self.__time.__cmp__(other.__time)
        return result

    def __str__(self):
        return ''.join([str(self.year), '-', __pad(self.month, 2), '-',
                __pad(self.day, 2), ' ', str(self.__time)])

    def __repr__(self):
        result = 'datetime.datetime(' + self._repr_inner() 
        if self.__time:
            result += ', ' + self.__time._repr_inner()
        return result + ')'

    __tz_offset = JS('new Date(0).getTimezoneOffset() * 60')

    @staticmethod
    def today():
        t = JS('Date.now()')
        t -= datetime.__tz_offset * 1000
        result = datetime.utcfromtimestamp(t // 1000)
        result.__time.__val = t % (__SECONDS_A_DAY * 1000) * 1000
        return result

    now = today

    @staticmethod
    def __do_fromtimestamp(timestamp, delta, ratio=__SECONDS_A_DAY):
        timestamp -= delta
        date_val = date._timestamp_to_val(timestamp)
        result = datetime(1, 1, 1)
        result.__val = date_val
        result.__time.__val = timestamp % __SECONDS_A_DAY * __MICRO_SECS_A_SEC
        return result

    @staticmethod
    def fromtimestamp(timestamp):
        return datetime.__do_fromtimestamp(timestamp, datetime.__tz_offset)

    @staticmethod
    def fromordinal(ordinal):
        d = date.fromordinal(ordinal)
        return datetime(d.year, d.month, d.day)

    def totimestamp(self):
        ''' totimestamp() not exist in standard python '''
        timepart = self.__time.__val // __MICRO_SECS_A_SEC
        timepart += datetime.__tz_offset
        return self.__val * __SECONDS_A_DAY + timepart

    @staticmethod
    def utcfromtimestamp(timestamp):
        return datetime.__do_fromtimestamp(timestamp, 0)

    def date(self):
        return date.fromordinal(self.toordinal())

    def time(self):
        return self.__time

    @staticmethod
    def combine(date, time):
        result = datetime(date.year, date.month, date.day)
        result.__time = time
        return result

    @staticmethod
    def strptime(date_string, format):
        raise NotImplementedError(
            'strptime() method on datetime is not implemented.')

    def __add__(self, other):
        timepart = self.__time.__val + other.__val % __MICRO_SECS_A_DAY
        result = super(datetime, self).__add__(other)
        result = datetime(result.year, result.month, result.day)
        if timepart < 0:
            timepart += __MICRO_SECS_A_DAY
            result.__val -= 1
        elif timepart >= __MICRO_SECS_A_DAY:
            timepart -= __MICRO_SECS_A_DAY
            result.__val += 1
        result.__time = time(0, 0, 0, timepart)
        return result

    def __sub__(self, other):
        if isinstance(other, datetime):
            ddelta = super(datetime, self).__sub__(other)
            tdelta = self.__time.__val - other.__time.__val
            return ddelta + timedelta(0, 0, tdelta)
        elif isinstance(other, timedelta):
            return self + (-other)
        else:
            return NotImplemented

    def replace(self, year=None, month=None, day=None, hour=None, minute=None,
            second=None, microsecond=None):
        return datetime(year or self.year, month or self.month, day or
                self.day, hour or self.hour, minute or self.minute, 
                second or self.second, microsecond or self.microsecond)

    def ctime(self):
        result = super(datetime, self).ctime()
        if self.__time:
            return result + ' ' + self.__time.isoformat()
        else:
            return result

    isoformat = __str__

    def __hash__(self):
        return super(datetime, self).__hash__() + hash(self.__time)

datetime.min = datetime(MINYEAR, 1, 1)
datetime.max = datetime(MAXYEAR, 12, 31, 23, 59, 59, 999999)
datetime.resolution = time.resolution
