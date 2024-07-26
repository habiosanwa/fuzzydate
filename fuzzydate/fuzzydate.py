"""Main module containing the `fuzzydate` class."""

from __future__ import annotations

import string
from datetime import date


class fuzzydate(date):  # noqa: N801
    """Fuzzy date type.

    Allows instancing date types which can have either an unknown day, or an unknown day and month.
    In other words, a fuzzy date can represent only a year, or only a year and a month.

    The missing parts of the date are treated internally as being the first of the month or the day,
    to allow date arithmetics and functions that accepts `date` to continue functioning correctly.
    Likewise, attempting to format the string using the standard `date` methods will output month and day
    as if the date had effectively a value of 1 in those fields.

    However, the class provides additional `fuzzy_` methods that allow the fuzzy date to be converted
    to and from string using a marker character (by default '?') in place of the unknown parts of the date.
    Its `__str__` and `__repr__` magic methods are similarly overloaded to display `None`.
    """

    __slots__ = "_year", "_month", "_day", "_hashcode", "_fuzzy_month", "_fuzzy_day", "_marker"

    def __new__(cls, year: int, month: int | None = None, day: int | None = None):
        """Constructor.

        Args:
        ----
            year (int): The year part of the date.
            month (int): The month part of the date. If None, set the month as 1 internally and treat as fuzzy.
            day (int): The day part of the date. If None, set the day as 1 internally and treat as fuzzy.

        """
        fuzzy_month = month is None
        fuzzy_day = day is None
        if fuzzy_month and not fuzzy_day:
            raise ValueError(f"A date cannot have a fuzzy month and a defined day: ({year}, {month}, {day})")

        if fuzzy_month:
            month = 1
        if fuzzy_day:
            day = 1

        self = super().__new__(cls, year, month, day)
        self._fuzzy_month = fuzzy_month
        self._fuzzy_day = fuzzy_day
        return self

    @classmethod
    def fromisoformat(cls, date_string):  # noqa
        raise NotImplementedError("`fromisoformat` is not supported for fuzzy dates; use `fuzzy_fromisoformat` instead")

    @classmethod
    def fuzzy_fromisoformat(cls, date_string: str) -> fuzzydate:
        """Fuzzy equivalent of `date.fromisoformat()`.

        Validation is reimplemented and augmented rather than relying on the superclass to avoid the overhead
        of performing similar checks upstream.

        Args:
        ----
            date_string (str): The string to parse. Can contain non-digit markers to denote fuzzy month or day,
                as long as the marker character used is consistent.

        Returns:
        -------
            fuzzydate: A new fuzzy date instance.

        """
        if not isinstance(date_string, str):
            raise TypeError("fuzzy_fromisoformat: argument must be str")
        if len(date_string) != 10:  # noqa: PLR2004
            raise ValueError(f"Invalid fuzzy isoformat string: {date_string}")
        for sep in (date_string[4], date_string[7]):
            if sep != "-":
                raise ValueError(f"Invalid date separator: {sep}")

        yyyy = date_string[0:4]
        mm = date_string[5:7]
        dd = date_string[8:10]

        try:
            day = int(dd)
        except ValueError:
            if dd[0] != dd[1]:
                raise ValueError(f"Inconsistent marker usage in fuzzy date: {date_string}") from None
            day = None

        try:
            month = int(mm)
        except ValueError:
            if mm[0] != mm[1] or (day is None and mm[0] != dd[0]):
                raise ValueError(f"Inconsistent marker usage in fuzzy date: {date_string}") from None
            month = None

        try:
            year = int(yyyy)
        except ValueError:
            raise ValueError(f"Invalid year: {yyyy}") from None

        return cls(year, month, day)

    def isoformat(self):  # noqa
        raise NotImplementedError("`isoformat` is not supported for fuzzy dates; use `fuzzy_isoformat` instead")

    def fuzzy_isoformat(self, marker: str = "?") -> str:
        """Fuzzy equivalent of `date.isoformat()`.

        Args:
        ----
            marker (str): The character which will be used to display fuzzy date parts.

        Returns:
        -------
            str: A modified ISO representation with markers (e.g. '??') in place of month or date, if fuzzy.

        """
        if len(marker) != 1 or marker in string.digits:
            raise ValueError(f"Invalid fuzzy marker: {marker} (must be a single non-digit character)")

        yyyy = "%04d" % self.year
        mm = marker * 2 if self._fuzzy_month else "%02d" % self.month
        dd = marker * 2 if self._fuzzy_day else "%02d" % self.day
        return f"{yyyy}-{mm}-{dd}"

    __str__ = fuzzy_isoformat

    def __repr__(self):
        month = None if self._fuzzy_month else self.month
        day = None if self._fuzzy_day else self.day
        return f"{self.__class__.__qualname__}({self.year}, {month}, {day})"
