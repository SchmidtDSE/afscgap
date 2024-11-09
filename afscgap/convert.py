"""
Logic to convert types when interacting with the AFSC GAP REST service.

(c) 2024 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import re

from afscgap.typesdef import OPT_FLOAT

ISO_8601_REGEX = re.compile('(?P<year>\\d{4})\\-(?P<month>\\d{2})\\-' + \
    '(?P<day>\\d{2})T(?P<hours>\\d{2})\\:(?P<minutes>\\d{2})\\:' + \
    '(?P<seconds>\\d{2})')

CONVERTERS = {
    'area': {
        'ha': lambda x: x,
        'm2': lambda x: x * 10000,
        'km2': lambda x: x * 0.01
    },
    'distance': {
        'm': lambda x: x,
        'km': lambda x: x / 1000
    },
    'temperature': {
        'c': lambda x: x,
        'f': lambda x: x * 9 / 5 + 32
    },
    'time': {
        'day': lambda x: x / 24,
        'hr': lambda x: x,
        'min': lambda x: x * 60
    },
    'weight': {
        'g': lambda x: x * 1000,
        'kg': lambda x: x
    },
    'degrees': {
        'dd': lambda x: x
    },
    'effortWeight': {
        'kg/ha': lambda x: x / 100,
        'kg1000/km2': lambda x: x / 0.1,
        'kg/km2': lambda x: x
    },
    'effortCount': {
        'no/ha': lambda x: x / 100,
        'no1000/km2': lambda x: x / 0.1,
        'no/km2': lambda x: x,
        'count/ha': lambda x: x / 100,
        'count1000/km2': lambda x: x / 0.1,
        'count/km2': lambda x: x
    }
}

UNCONVERTERS = {
    'area': {
        'ha': lambda x: x,
        'm2': lambda x: x / 10000,
        'km2': lambda x: x / 0.01
    },
    'distance': {
        'm': lambda x: x,
        'km': lambda x: x * 1000
    },
    'temperature': {
        'c': lambda x: x,
        'f': lambda x: (x - 32) * 5 / 9
    },
    'time': {
        'day': lambda x: x * 24,
        'hr': lambda x: x,
        'min': lambda x: x / 60
    },
    'weight': {
        'g': lambda x: x / 1000,
        'kg': lambda x: x
    },
    'degrees': {
        'dd': lambda x: x
    },
    'effortWeight': {
        'kg/ha': lambda x: x * 100,
        'kg1000/km2': lambda x: x * 0.1,
        'kg/km2': lambda x: x
    },
    'effortCount': {
        'no/ha': lambda x: x * 100,
        'no1000/km2': lambda x: x * 0.1,
        'no/km2': lambda x: x,
        'count/ha': lambda x: x * 100,
        'count1000/km2': lambda x: x * 0.1,
        'count/km2': lambda x: x
    }
}

UNIT_TYPES = {
    'ha': 'area',
    'm2': 'area',
    'km2': 'area',
    'm': 'distance',
    'km': 'distance',
    'c': 'temperature',
    'f': 'temperature',
    'day': 'time',
    'hr': 'time',
    'min': 'time',
    'g': 'weight',
    'kg': 'weight',
    'dd': 'degrees',
    'kg/ha': 'effortWeight',
    'kg1000/km2': 'effortWeight',
    'kg/km2': 'effortWeight',
    'no/ha': 'effortCount',
    'no1000/km2': 'effortCount',
    'no/km2': 'effortCount',
    'count/ha': 'effortCount',
    'count1000/km2': 'effortCount',
    'count/km2': 'effortCount'
}


def is_iso8601(target: str) -> bool:
    """Determine if a string matches an expected ISO 8601 format.

    Args:
        target: The string to test.

    Returns:
        True if it matches the expected format and false otherwise.
    """
    return ISO_8601_REGEX.match(target) is not None


def convert(target: OPT_FLOAT, source: str, destination: str) -> OPT_FLOAT:
    """Convert a value.

    Args:
        target: The value to convert.
        source: Original units.
        destination: Target units.

    Returns:
        The converted value. Note that, if target is None, will return None.
    """
    if target is None:
        return None

    if source not in UNIT_TYPES:
        raise RuntimeError('Unknown units: %s' % source)

    if destination not in UNIT_TYPES:
        raise RuntimeError('Unknown units: %s' % destination)

    source_type = UNIT_TYPES[source]
    destination_type = UNIT_TYPES[destination]

    if source_type != destination_type:
        raise RuntimeError('Cannot convert from %s to %s' % (source, destination))

    source_converter = UNCONVERTERS[source_type][source]
    destination_converter = CONVERTERS[destination_type][destination]

    unconverted = source_converter(target)
    converted = destination_converter(unconverted)

    return converted
