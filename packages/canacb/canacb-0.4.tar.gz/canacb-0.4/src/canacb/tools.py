#!/usr/bin/env python3

"""Tools and utilities

General purpose functions to test/manipulate dates and floats.
"""

import datetime


_cached = {}  # Time/space tradeoff: cache use -> 5x speedup on repeats


def fromisoformat(date_string: str, strict: bool = False) -> datetime.date:
    """Creates a date object from either a YYYY-MM-DD or YYYYMMDD string.

    python datetime < 3.11 has no useful isoformat method and its strptime
    method is too slow for this specific use with high volume.

    Arguments:
        date_string: a string in YYYY-MM-DD or YYYYMMDD form
        strict: True if nothing but YYYY-MM-DD will do

    Returns:
        datetime.date: the corresponding python date object,
            or None if the argument string is zero length and strict == False

    Raises:
        TypeError:  if argument is neither None nor string
        ValueError: if argument has unexpected format
    """
    if date_string is None and not strict:
        return None
    if not isinstance(date_string, str):
        raise TypeError("argument must be a string")
    date_string = date_string.strip()
    if len(date_string) == 0 and not strict:
        return None

    if date_string in _cached:
        return _cached[date_string]

    try:
        if len(date_string) == 10:
            result = datetime.date(
                int(date_string[0:4]),
                int(date_string[5:7]),
                int(date_string[8:10]),
            )
            _cached[date_string] = result
            return result
        if len(date_string) == 8 and not strict:
            result = datetime.date(
                int(date_string[0:4]),
                int(date_string[4:6]),
                int(date_string[6:8]),
            )
            _cached[date_string] = result
            return result
    except ValueError:
        pass
    raise ValueError(
        "{} not of form YYYY-MM-DD{}".format(
            date_string, "" if strict else " or YYYYMMDD"
        )
    )


def is_isoformat(date: str):
    """Returns True if the string looks like an ISO date"""
    try:
        fromisoformat(date)
        return True
    except ValueError:
        return False


def is_valid_year(year: str):
    """Returns True if the string looks like a year"""
    return len(year) == 4 and year.isnumeric()


def checked_float(item: str, test, fail_msg: str) -> float:
    """Returns the first argument if it converts to a float that passes
    the provided test.

    Raises a ValueError with the provided fail message if not.
    """
    try:
        item = float(item)
        if test(item):
            return item
    except (TypeError, ValueError):
        pass
    raise ValueError(fail_msg)


def pretty_float(
    number: float,
    min_decimals: int = 2,
    max_decimals: int = 2,
    blank_if_zero: bool = True,
) -> str:
    """Converts a float to a string with acceptable cosmetics. In particular,
    strips the usual format of trailing decimal places that are zero.

    Arguments:
        number: the floating point number to format
        min_decimals: minimum number of decimals to show
        max_decimals: maximum number of decimals to show
                      (if < min_decimals, ignored)
        blank_if_zero: True if a blank field is acceptable for a zero

    Returns:
        str: the prettiest string we can manage
    """
    try:
        if blank_if_zero and abs(2.0 * number) < pow(10, -max_decimals):
            return ""
    except TypeError:
        pass
    while max_decimals > min_decimals:
        formatted = "{:.{}f}".format(number, max_decimals)
        if formatted[-1] != "0":
            return formatted
        max_decimals -= 1
    return "{:.{}f}".format(number, min_decimals)
