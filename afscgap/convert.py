"""
Logic to convert types when interacting with the AFSC GAP REST service.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import re

from afscgap.typesdef import FLOAT_PARAM
from afscgap.typesdef import OPT_FLOAT
from afscgap.typesdef import STR_PARAM

DATE_REGEX = re.compile('(?P<month>\\d{2})\\/(?P<day>\\d{2})\\/' + \
    '(?P<year>\\d{4}) (?P<hours>\\d{2})\\:(?P<minutes>\\d{2})\\:' + \
    '(?P<seconds>\\d{2})')
DATE_TEMPLATE = '%s/%s/%s %s:%s:%s'
ISO_8601_REGEX = re.compile('(?P<year>\\d{4})\\-(?P<month>\\d{2})\\-' + \
    '(?P<day>\\d{2})T(?P<hours>\\d{2})\\:(?P<minutes>\\d{2})\\:' + \
    '(?P<seconds>\\d{2})')
ISO_8601_TEMPLATE = '%s-%s-%sT%s:%s:%s'

AREA_CONVERTERS = {
    'ha': lambda x: x,
    'm2': lambda x: x * 10000,
    'km2': lambda x: x * 0.01
}

AREA_UNCONVERTERS = {
    'ha': lambda x: x,
    'm2': lambda x: x / 10000,
    'km2': lambda x: x / 0.01
}

DISTANCE_CONVERTERS = {
    'm': lambda x: x,
    'km': lambda x: x / 1000
}

DISTANCE_UNCONVERTERS = {
    'm': lambda x: x,
    'km': lambda x: x * 1000
}

TEMPERATURE_CONVERTERS = {
    'c': lambda x: x,
    'f': lambda x: x * 9 / 5 + 32
}

TEMPERATURE_UNCONVERTERS = {
    'c': lambda x: x,
    'f': lambda x: (x - 32) * 5 / 9
}

TIME_CONVERTERS = {
    'day': lambda x: x / 24,
    'hr': lambda x: x,
    'min': lambda x: x * 60
}

TIME_UNCONVERTERS = {
    'day': lambda x: x * 24,
    'hr': lambda x: x,
    'min': lambda x: x / 60
}

WEIGHT_CONVERTERS = {
    'g': lambda x: x * 1000,
    'kg': lambda x: x
}

WEIGHT_UNCONVERTERS = {
    'g': lambda x: x / 1000,
    'kg': lambda x: x
}


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


def convert_area(target: OPT_FLOAT, units: str) -> OPT_FLOAT:
    """Convert an area.

    Args:
        target: The value to convert in hectares.
        units: Desired units.

    Returns:
        The converted value. Note that, if target is None, will return None.
    """
    if target is None:
        return None

    return AREA_CONVERTERS[units](target)


def unconvert_area(target: FLOAT_PARAM, units: str) -> FLOAT_PARAM:
    """Standardize an area to the API-native units (hectare).

    Args:
        target: The value to convert in hectares.
        units: The units of value.

    Returns:
        The converted value. Note that, if target is None, will return None.
    """
    if target is None:
        return None

    if isinstance(target, dict):
        return target

    return AREA_UNCONVERTERS[units](target)


def convert_degrees(target: OPT_FLOAT, units: str) -> OPT_FLOAT:
    """Convert targets from degrees to another units.

    Args:
        target: The value to convert which may be None.
        units: Desired units.

    Returns:
        The same value input after asserting that units are dd, the only
        supported units.
    """
    assert units == 'dd'
    return target


def unconvert_degrees(target: FLOAT_PARAM, units: str) -> FLOAT_PARAM:
    """Standardize a degree to the API-native units (degrees).

    Args:
        target: The value to convert which may be None.
        units: The units of value.

    Returns:
        The same value input after asserting that units are dd, the only
        supported units.
    """
    assert units == 'dd'
    return target


def convert_distance(target: OPT_FLOAT, units: str) -> OPT_FLOAT:
    """Convert a linear distance.

    Args:
        target: The value to convert in meters.
        units: Desired units.

    Returns:
        The converted value. Note that, if target is None, will return None.
    """
    if target is None:
        return None

    return DISTANCE_CONVERTERS[units](target)


def unconvert_distance(target: FLOAT_PARAM, units: str) -> FLOAT_PARAM:
    """Convert a linear distance to the API-native units (meters).

    Args:
        target: The value to convert in meters.
        units: The units of value.

    Returns:
        The converted value. Note that, if target is None, will return None.
    """
    if target is None:
        return None

    if isinstance(target, dict):
        return target

    return DISTANCE_UNCONVERTERS[units](target)


def convert_temperature(target: OPT_FLOAT, units: str) -> OPT_FLOAT:
    """Convert a temperature.

    Args:
        target: The value to convert in Celcius.
        units: Desired units.

    Returns:
        The converted value. Note that, if target is None, will return None.
    """
    if target is None:
        return None

    return TEMPERATURE_CONVERTERS[units](target)


def unconvert_temperature(target: FLOAT_PARAM, units: str) -> FLOAT_PARAM:
    """Convert a linear temperature to the API-native units (Celsius).

    Args:
        target: The value to convert in Celcius.
        units: The units of value.

    Returns:
        The converted value. Note that, if target is None, will return None.
    """
    if target is None:
        return None

    if isinstance(target, dict):
        return target

    return TEMPERATURE_UNCONVERTERS[units](target)


def convert_time(target: OPT_FLOAT, units: str) -> OPT_FLOAT:
    """Convert a time.

    Args:
        target: The value to convert in hours.
        units: Desired units.

    Returns:
        The converted value. Note that, if target is None, will return None.
    """
    if target is None:
        return None

    return TIME_CONVERTERS[units](target)


def unconvert_time(target: FLOAT_PARAM, units: str) -> FLOAT_PARAM:
    """Convert a time to the API-native units (hours).

    Args:
        target: The value to convert in hours.
        units: The units of value.

    Returns:
        The converted value. Note that, if target is None, will return None.
    """
    if target is None:
        return None

    if isinstance(target, dict):
        return target

    return TIME_UNCONVERTERS[units](target)


def convert_weight(target: OPT_FLOAT, units: str) -> OPT_FLOAT:
    """Convert a weight.

    Args:
        target: The value to convert in kilograms.
        units: Desired units.

    Returns:
        The converted value. Note that, if target is None, will return None.
    """
    if target is None:
        return None

    return WEIGHT_CONVERTERS[units](target)


def unconvert_weight(target: FLOAT_PARAM, units: str) -> FLOAT_PARAM:
    """Convert a weight to the API-native units (kilograms).

    Args:
        target: The value to convert in kilograms.
        units: The units of value.

    Returns:
        The converted value. Note that, if target is None, will return None.
    """
    if target is None:
        return None

    if isinstance(target, dict):
        return target

    return WEIGHT_UNCONVERTERS[units](target)
