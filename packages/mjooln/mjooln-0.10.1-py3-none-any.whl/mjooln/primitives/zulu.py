# Copyright (c) 2020 Vemund Halmø Aarstrand
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import datetime
import re
from dateutil.parser import parse as dateparser  # type: ignore[import-untyped]

import dateutil  # type: ignore[import-untyped]
import pytz  # type: ignore[import-untyped]
from collections import namedtuple

from mjooln.exception import ZuluError
from mjooln.core import Seed, Glass


class Zulu(datetime.datetime, Seed, Glass):
    # TODO: Round to millisecond etc. And floor. Check Arrow how its done

    """
    Timezone aware datetime objects in UTC

    Create using constructor::

        Zulu() or Zulu.now()
            Zulu(2020, 5, 21, 20, 5, 31, 930343)

        Zulu(2020, 5, 12)
            Zulu(2020, 5, 12)

        Zulu(2020, 5, 21, 20, 5, 31)
            Zulu(2020, 5, 21, 20, 5, 31)

    :meth:`Seed.seed` is inherited from :class:`Seed` and returns a string
    on the format ``<date>T<time>u<microseconds>Z``, and is \'designed\'
    to be file name and double click friendly, as well as easily recognizable
    within some string when using regular expressions.
    Printing a Zulu object returns seed, and Zulu can be created using
    :meth:`from_seed`::

        z = Zulu(2020, 5, 12)
        print(z)
            20200512T000000u000000Z

        z.seed()
            '20200512T000000u000000Z'

        str(z)
            '20200512T000000u000000Z'

        Zulu.from_seed('20200512T000000u000000Z')
            Zulu(2020, 5, 12)

    For an `ISO 8601 <https://en.wikipedia.org/wiki/ISO_8601>`_
    formatted string, use custom function::

        z = Zulu('20200521T202041u590718Z')
        z.iso()
            '2020-05-21T20:20:41.590718+00:00'

    Similarly, Zulu can be created from ISO string::

        Zulu.from_iso('2020-05-21T20:20:41.590718+00:00')
            Zulu(2020, 5, 21, 20, 20, 41, 590718)


    Inputs or constructors may vary, but Zulu objects are *always* UTC. Hence
    the name Zulu.

    Constructor also takes regular datetime objects, provided they have
    timezone info::

        dt = datetime.datetime(2020, 5, 23, tzinfo=pytz.utc)
        Zulu(dt)
            Zulu(2020, 5, 23, 0, 0, tzinfo=<UTC>)

        dt = datetime.datetime(2020, 5, 23, tzinfo=dateutil.tz.tzlocal())
        Zulu(dt)
            Zulu(2020, 5, 22, 22, 0, tzinfo=<UTC>)

    Zulu has element access like datetime, in addition to string convenience
    attributes::

        z = Zulu()
        print(z)
            20200522T190137u055918Z
        z.month
            5
        z.str.month
            '05'
        z.str.date
            '20200522'
        z.str.time
            '190137'

    Zulu has a method :meth:`delta` for timedelta, as well as :meth:`add`
    for adding timedeltas directly to generate a new Zulu::

        Zulu.delta(hours=1)
            datetime.timedelta(seconds=3600)

        z = Zulu(2020, 1, 1)
        z.add(days=2)
            Zulu(2020, 1, 3)

    For more flexible ways to create a Zulu object, see :meth:`Zulu.elf`

    """

    _ZuluStr = namedtuple(
        "_ZuluStr",
        [
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "second",
            "microsecond",
            "date",
            "time",
            "seed",
        ],
    )

    _FORMAT = "%Y%m%dT%H%M%Su%fZ"
    REGEX = r"\d{8}T\d{6}u\d{6}Z"
    LENGTH = 23

    ISO_REGEX_STRING = (
        r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-"
        r"(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):"
        r"([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-]"
        r"(?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
    )
    ISO_REGEX = re.compile(ISO_REGEX_STRING)

    ############################################################################
    # String methods
    ############################################################################

    @classmethod
    def is_iso(cls, st: str):
        """
        Check if input string is
        `ISO 8601 <https://en.wikipedia.org/wiki/ISO_8601>`_

        Check is done using regex :data:`Zulu.ISO_REGEX`

        :param st: Maybe an ISO formatted string
        :return: True if input string is iso, False if not
        :rtype: bool
        """

        return cls.ISO_REGEX.match(st) is not None

    ############################################################################
    # Timezone methods
    ############################################################################

    @classmethod
    def all_timezones(cls):
        """
        Returns a list of all allowed timezone names

        Timezone \'local\' will return a datetime object with local timezone,
        but is not included in this list

        Wrapper for :meth:`pytz.all_timezones`

        :return: List of timezones
        :rtype: list
        """
        return pytz.all_timezones

    @classmethod
    def _to_utc(cls, ts):
        return ts.astimezone(pytz.utc)

    @classmethod
    def _tz_from_name(cls, tz="utc"):
        if tz == "local":
            tz = dateutil.tz.tzlocal()  # type: ignore
        else:
            try:
                tz = pytz.timezone(tz)
            except pytz.exceptions.UnknownTimeZoneError:
                raise ZuluError(
                    f"Unknown timezone: '{tz}'. "
                    f"Use Zulu.all_timezones() for a list "
                    f"of actual timezones"
                )
        return tz

    ############################################################################
    # Create methods
    ############################################################################

    @classmethod
    def now(cls, tz=None):
        """
        Overrides ``datetime.datetime.now()``. Equivalent to ``Zulu()``

        :raise ZuluError: If parameter ``tz`` has a value. Even if value is UTC
        :param tz: Do not use. Zulu is always UTC
        :return: Zulu
        """
        if tz:
            raise ZuluError(
                "Zulu.now() does not allow input time zone info. "
                "Zulu is always UTC. Hence the name"
            )
        return cls()

    @classmethod
    def _from_unaware(cls, ts, tz=None):
        if not tz:
            raise ZuluError(
                "No timezone info. Set timezone to use "
                "with 'tz=<timezone string>'. 'local' will "
                "use local timezone info. Use "
                "Zulu.all_timezones() for a list of actual "
                "timezones"
            )
        return ts.replace(tzinfo=cls._tz_from_name(tz))

    @classmethod
    def _elf(cls, ts, tz=None):
        # Takes a datetime.datetime object and adds the input tzinfo if
        # none is present
        if not ts.tzinfo:
            ts = cls._from_unaware(ts, tz=tz)
        return ts

    @classmethod
    def from_unaware(cls, ts, tz="utc"):
        """Create Zulu from timezone unaware datetime

        :param ts: Unaware time stamp
        :type ts: datetime.datetime
        :param tz: Time zone, with 'utc' as default.
            'local' will use local time zone
        :rtype: Zulu
        """
        if ts.tzinfo:
            raise ZuluError(
                f"Input datetime already has "
                f"time zone info: {ts}. "
                f"Use constructor or Zulu.elf()"
            )
        else:
            ts = cls._from_unaware(ts, tz=tz)
        return cls(ts)

    @classmethod
    def from_unaware_local(cls, ts):
        """
        Create Zulu from timezone unaware local timestamp

        :param ts: Timezone unaware datetime
        :type ts: datetime.datetime
        :rtype: Zulu
        """
        return cls.from_unaware(ts, tz="local")

    @classmethod
    def from_unaware_utc(cls, ts):
        """
        Create Zulu from timezone unaware UTC timestamp

        :param ts: Timezone unaware datetime
        :type ts: datetime.datetime
        :rtype: Zulu
        """
        return cls.from_unaware(ts, tz="utc")

    @classmethod
    def _parse_iso(cls, iso: str):
        ts = dateparser(iso)
        if ts.tzinfo and str(ts.tzinfo) == "tzutc()":
            ts = ts.astimezone(pytz.utc)
        return ts

    @classmethod
    def from_iso(cls, str_: str, tz=None):
        """
        Create Zulu object from ISO 8601 string

        :param str_: ISO 8601 string
        :param tz: Timezone string to use if missing in ts_str
        :return: Zulu
        :rtype: Zulu
        """
        ts = cls._parse_iso(str_)
        if tz and not ts.tzinfo:
            ts = cls._from_unaware(ts, tz)
        elif ts.tzinfo and tz:
            raise ZuluError(
                "Timezone info found in ISO string as well as "
                "input timezone argument (tz). Keep tz=None, "
                "or use Zulu.elf()"
            )
        elif not tz and not ts.tzinfo:
            raise ZuluError("No timezone info in neither ISO string nor tz argument")
        return cls(ts)

    @classmethod
    def _parse(cls, ts_str: str, pattern: str):
        return datetime.datetime.strptime(ts_str, pattern)

    @classmethod
    def parse(cls, ts_str: str, pattern: str, tz=None):
        """Parse time stamp string with the given pattern

        :param ts_str: Timestamp string
        :type ts_str: str
        :param pattern: Follows standard
            `python strftime reference <https://strftime.org/>`_
        :param tz: Timezone to use if timestamp does not have timezone info
        :return: Zulu
        """
        ts = cls._parse(ts_str, pattern)
        if not ts.tzinfo:
            ts = cls._from_unaware(ts, tz=tz)
        elif tz:
            raise ZuluError(
                "Cannot have an input timezone argument when "
                "input string already has timezone information"
            )
        return cls(ts)

    @classmethod
    def from_seed(cls, seed: str):
        """
        Create Zulu object from seed string

        :param seed: Seed string
        :rtype: Zulu
        """
        if not cls.is_seed(seed):
            raise ZuluError(f"String is not Zulu seed: {seed}")
        ts = cls._parse(seed, cls._FORMAT)
        ts = cls._from_unaware(ts, tz="utc")
        return cls(ts)

    @classmethod
    def _from_epoch(cls, epoch):
        return datetime.datetime.fromtimestamp(epoch, datetime.UTC)
        # return datetime.datetime.utcfromtimestamp(epoch).replace(tzinfo=pytz.UTC)

    @classmethod
    def from_epoch(cls, epoch):
        """
        Create Zulu object from UNIX Epoch

        :param epoch: Unix epoch
        :type epoch: float
        :return: Zulu instance
        :rtype: Zulu
        """
        ts = cls._from_epoch(epoch)
        return cls(ts)

    @classmethod
    def _fill_args(cls, args):
        if len(args) < 8:
            # From date
            args = list(args)
            args += (8 - len(args)) * [0]
            if args[1] == 0:
                args[1] = 1
            if args[2] == 0:
                args[2] = 1
            args = tuple(args)

        if args[-1] not in [None, 0, pytz.utc]:
            raise ZuluError(f"Zulu can only be UTC. Invalid timezone: {args[-1]}")

        args = list(args)
        args[-1] = pytz.utc
        return tuple(args)

    @classmethod
    def glass(cls, *args, **kwargs):
        if len(kwargs) == 0 and len(args) == 1:
            if isinstance(args[0], Zulu):
                return args[0]
            elif isinstance(args[0], str):
                return cls.from_str(args[0])
        else:
            return cls(*args, **kwargs)

    @classmethod
    def elf(cls, *args, tz="local"):
        """
        General input Zulu constructor

        Takes the same inputs as constructor, and also allows Zulu
        objects to pass through. If timeozone is missing it will assume the input
        timezone ``tz``, which is set to local as default

        It takes both seed strings and iso strings::

            Zulu.elf('20201112T213732u993446Z')
                Zulu(2020, 11, 12, 21, 37, 32, 993446)

            Zulu.elf('2020-11-12T21:37:32.993446+00:00')
                Zulu(2020, 11, 12, 21, 37, 32, 993446)

        It takes UNIX epoch::

            e = Zulu(2020, 1, 1).epoch()
            e
                1577836800.0
            Zulu.elf(e)
                Zulu(2020, 1, 1)

        It will guess the missing values if input integers are not a full date
        and/or time::

            Zulu.elf(2020)
                Zulu(2020, 1, 1)

            Zulu.elf(2020, 2)
                Zulu(2020, 2, 1)

            Zulu.elf(2020,1,1,10)
                Zulu(2020, 1, 1, 10, 0, 0)

        .. warning:: Elves are fickle

        :raise AngryElf: If an instance cannot be created from the given input
        :param args: Input arguments
        :param tz: Time zone to assume if missing. 'local' will use local
            time zone. Use :meth:`all_timezones` for a list of actual
            timezones. Default is 'local'
        :return: Best guess Zulu object
        :rtype: Zulu
        """
        ts = None
        if len(args) == 0:
            return cls()
        elif len(args) > 1:
            args = cls._fill_args(args)
            ts = datetime.datetime(*args)
            if not ts.tzinfo:
                ts = cls._from_unaware(ts, tz)
        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg, Zulu):
                return arg
            elif isinstance(arg, datetime.datetime):
                # Add timzone if missing
                ts = cls._elf(arg, tz=tz)
                return cls(ts)
            elif isinstance(arg, float):
                return cls.from_epoch(arg)
            elif isinstance(arg, int):
                # Instantiate as start of year
                return cls(arg, 1, 1)
            elif isinstance(arg, str):
                if cls.is_seed(arg):
                    return cls.from_seed(arg)
                elif cls.is_iso(arg):
                    ts = cls._parse_iso(arg)
                    # Add timzone if missing
                    ts = cls._elf(ts, tz=tz)
                else:
                    raise ZuluError(
                        f"String is neither zulu, nor ISO: {arg}. "
                        f"Use Zulu.parse() and enter the format "
                        f"yourself"
                    )
            else:
                raise ZuluError(
                    f"Found no way to interpret input "
                    f"argument as Zulu: {arg} [{type(arg)}]"
                )
        return cls(ts)

    @classmethod
    def range(cls, start=None, n=10, delta=datetime.timedelta(hours=1)):
        """Generate a list of Zulu of fixed intervals

        .. note:: Mainly for dev purposes. There are far better
            ways of creating a range of timestamps, such as using pandas.

        :param start: Start time Zulu, default is *now*
        :type start: Zulu
        :param n: Number of timestamps in range, with default 10
        :type n: int
        :param delta: Time delta between items, with default one hour
        :type delta: datetime.timedelta
        :rtype: [Zulu]
        """
        if not start:
            start = cls()
        return [Zulu.elf(start + x * delta) for x in range(n)]

    def __new__(cls, *args, **kwargs):
        if len(args) == 0 and len(kwargs) == 0:
            ts = datetime.datetime.now(datetime.UTC)
        elif len(args) == 1 and len(kwargs) == 0:
            arg = args[0]
            if isinstance(arg, str):
                raise ZuluError(
                    "Cannot instantiate Zulu with a string. Use "
                    "Zulu.from_iso(), Zulu.from_seed(), "
                    "Zulu.from_string() or Zulu.parse()"
                )
            elif isinstance(arg, float):
                raise ZuluError(
                    f"Cannot create Zulu object from a float: "
                    f"{arg}; If float is unix epoch, "
                    f"use Zulu.from_epoch()"
                )
            elif isinstance(arg, Zulu):
                raise ZuluError(
                    f"Input argument is already Zulu: {arg}. "
                    f"Use Zulu.glass() to allow passthrough"
                )
            elif isinstance(arg, datetime.datetime):
                ts = arg
                if not ts.tzinfo:
                    raise ZuluError(
                        "Cannot create Zulu from datetime if "
                        "datetime object does not have timezone "
                        "info. Use Zulu.from_unaware()"
                    )
                ts = ts.astimezone(pytz.UTC)
            else:
                raise ZuluError(
                    f"Unable to interpret input argument: {arg} [{type(arg).__name__}]"
                )
        else:
            # Handle input as regular datetime input (year, month, day etc)
            try:
                ts = datetime.datetime(*args)
            except TypeError as te:
                raise ZuluError from te
            # Add timezone info if missing (assume utc, of course)
            if not ts.tzinfo:
                ts = ts.replace(tzinfo=pytz.UTC)

        # Create actual object
        args = tuple(
            [
                ts.year,
                ts.month,
                ts.day,
                ts.hour,
                ts.minute,
                ts.second,
                ts.microsecond,
                ts.tzinfo,
            ]
        )
        self = super().__new__(cls, *args)
        seed = self.strftime(self._FORMAT)
        self.str = self._ZuluStr(  # type: ignore
            year=seed[:4],
            month=seed[4:6],
            day=seed[6:8],
            hour=seed[9:11],
            minute=seed[11:13],
            second=seed[13:15],
            microsecond=seed[16:22],
            date=seed[:8],
            time=seed[9:15],
            seed=seed,
        )
        return self

    def __str__(self):
        return self.str.seed  # type: ignore

    def __repr__(self):
        times = [self.hour, self.minute, self.second]
        has_micro = self.microsecond > 0
        has_time = sum(times) > 0
        nums = [self.year, self.month, self.day]
        if has_time or has_micro:
            nums += times
        if has_micro:
            nums += [self.microsecond]
        numstr = ", ".join([str(x) for x in nums])
        return f"Zulu({numstr})"

    def epoch(self):
        """
        Get UNIX epoch (seconds since January 1st 1970)

        Wrapper for :meth:`datetime.datetime.timestamp`

        :return: Seconds since January 1st 1970
        :rtype: float
        """
        return self.timestamp()

    @classmethod
    def from_str(cls, st: str):
        """
        Converts seed or iso string to Zulu

        :param st: Seed or iso string
        :rtype: Zulu
        """
        if cls.is_seed(st):
            return cls.from_seed(st)
        elif cls.is_iso(st):
            return cls.from_iso(st)
        else:
            raise ZuluError(
                f"Unknown string format (neither seed nor iso): "
                f"{st}; "
                f"Use Zulu.parse() to specify format pattern and "
                f"timezone"
            )

    def iso(self, full=False):
        """Create `ISO 8601 <https://en.wikipedia.org/wiki/ISO_8601>`_ string

        Example::

            z = Zulu(2020, 5, 21)
            z.iso()
                '2020-05-21T00:00:00+00:00'

            z.iso(full=True)
                '2020-05-21T00:00:00.000000+00:00'

        :param full: If True, pad isostring to full length when microsecond is
            zero, so that all strings returned will have same length (has
            proved an issue with a certain document database tool, which
            was not able to parse varying iso string length without help)
        :type full: bool
        :return: str
        """
        iso = self.isoformat()
        if full:
            if len(iso) == 25:
                iso = iso.replace("+", ".000000+")
        return iso

    def format(self, pattern):
        """
        Format Zulu to string with the given pattern

        Wrapper for :meth:`datetime.datetime.strftime`

        :param pattern: Follows standard
            `Python strftime reference <https://strftime.org/>`_
        :return: str
        """
        return self.strftime(pattern)

    def to_unaware(self):
        """
        Get timezone unaware datetime object in UTC

        :return: Timezone unaware datetime
        :rtype: datetime.datetime
        """
        ts = datetime.datetime.utcfromtimestamp(self.epoch()).replace(tzinfo=pytz.UTC)
        return ts.replace(tzinfo=None)

    def to_tz(self, tz="local"):
        """Create regular datetime with input timezone

        For a list of timezones use :meth:`.Zulu.all_timezones()`.
        'local' is also allowed, although not included in the list

        :param tz: Time zone to use. 'local' will return the local time zone.
            Default is 'local'
        :rtype: datetime.datetime
        """
        # ts_utc = datetime.datetime.utcfromtimestamp(self.epoch()).replace(tzinfo=pytz.UTC)
        ts_utc = datetime.datetime.fromtimestamp(self.epoch(), datetime.UTC)
        return ts_utc.astimezone(self._tz_from_name(tz))

    def to_local(self):
        """Create regular datetime with local timezone

        :rtype: datetime.datetime
        """
        return self.to_tz(tz="local")

    def round_to_ms(self, floor=False):
        """Round to nearest millisecond

        :rtype: Zulu
        """
        mod = self.microsecond % 1000
        if mod == 0:
            return self
        elif floor or mod < 500:
            return self.add(microseconds=-mod)
        else:
            return self.add(microseconds=1000 - mod)

    def floor_to_ms(self):
        return self.round_to_ms(floor=True)

    def round_to_s(self, floor=False):
        """Round to nearest second

        :rtype: Zulu
        """
        if self.microsecond == 0:
            return self
        elif floor or self.microsecond < 50000:
            return self.add(microseconds=-self.microsecond)
        else:
            return self.add(seconds=1, microseconds=-self.microsecond)

    def floor_to_s(self):
        return self.round_to_s(floor=True)

    @classmethod
    def delta(cls, days=0, hours=0, minutes=0, seconds=0, microseconds=0, weeks=0):
        """Wrapper for :meth:`datetime.timedelta`

        :param days: Number of days
        :param hours: Number of hours
        :param minutes: Number of minutes
        :param seconds: Number of seconds
        :param microseconds: Number of microseconds
        :param weeks: Number of weeks
        :return: datetime.timedelta
        """
        return datetime.timedelta(
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            microseconds=microseconds,
            weeks=weeks,
        )

    def add(self, days=0, hours=0, minutes=0, seconds=0, microseconds=0, weeks=0):
        """
        Adds the input to current Zulu object and returns a new one

        :param days: Number of days
        :param hours: Number of hours
        :param minutes: Number of minutes
        :param seconds: Number of seconds
        :param microseconds: Number of microseconds
        :param weeks: Number of weeks

        :return: Current object plus added delta
        :rtype: Zulu
        """
        delta = self.delta(
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            microseconds=microseconds,
            weeks=weeks,
        )
        return self + delta
