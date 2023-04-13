"""
Logic to convert types when interacting with the AFSC GAP REST service.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import re

from afscgap.typesdef import STR_PARAM

DATE_REGEX = re.compile('(?P<month>\\d{2})\\/(?P<day>\\d{2})\\/' + \
    '(?P<year>\\d{4}) (?P<hours>\\d{2})\\:(?P<minutes>\\d{2})\\:' + \
    '(?P<seconds>\\d{2})')
DATE_TEMPLATE = '%s/%s/%s %s:%s:%s'
ISO_8601_REGEX = re.compile('(?P<year>\\d{4})\\-(?P<month>\\d{2})\\-' + \
    '(?P<day>\\d{2})T(?P<hours>\\d{2})\\:(?P<minutes>\\d{2})\\:' + \
    '(?P<seconds>\\d{2})')
ISO_8601_TEMPLATE = '%s-%s-%sT%s:%s:%s'


def convert_from_iso8601(target: STR_PARAM) -> STR_PARAM:
    """Convert strings from ISO 8601 format to API format.

    Args:
        target: The string or dictionary in which to perform the
            transformations.

    Returns:
        If given an ISO 8601 string, will convert from ISO 8601 to the API
        datetime string format. Similarly, if given a dictionary, all values
        matching an ISO 8601 string will be converted to the API datetime string
        format. If given None, returns None.
    """
    if target is None:
        return None
    elif isinstance(target, str):
        return convert_from_iso8601_str(target)
    elif isinstance(target, dict):
        items = target.items()
        output_dict = {}

        for key, value in items:
            if isinstance(value, str):
                output_dict[key] = convert_from_iso8601_str(value)
            else:
                output_dict[key] = value

        return output_dict
    else:
        return target


def convert_from_iso8601_str(target: str) -> str:
    """Attempt converting an ISO 8601 string to an API-provided datetime.

    Args:
        target: The datetime string to try to interpret.

    Returns:
        The datetime input string as a ISO 8601 string or the original value of
        target if it could not be parsed.
    """
    match = ISO_8601_REGEX.match(target)

    if not match:
        return target

    year = match.group('year')
    month = match.group('month')
    day = match.group('day')
    hours = match.group('hours')
    minutes = match.group('minutes')
    seconds = match.group('seconds')

    return DATE_TEMPLATE % (month, day, year, hours, minutes, seconds)


def convert_to_iso8601(target: str) -> str:
    """Attempt converting an API-provided datetime to ISO 8601.

    Args:
        target: The datetime string to try to interpret.
    Returns:
        The datetime input string as a ISO 8601 string or the original value of
        target if it could not be parsed.
    """
    match = DATE_REGEX.match(target)

    if not match:
        return target

    year = match.group('year')
    month = match.group('month')
    day = match.group('day')
    hours = match.group('hours')
    minutes = match.group('minutes')
    seconds = match.group('seconds')

    return ISO_8601_TEMPLATE % (year, month, day, hours, minutes, seconds)


def is_iso8601(target: str) -> bool:
    """Determine if a string matches an expected ISO 8601 format.

    Args:
        target: The string to test.

    Returns:
        True if it matches the expected format and false otherwise.
    """
    return ISO_8601_REGEX.match(target) is not None
