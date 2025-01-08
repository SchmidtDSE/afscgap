"""
Utility functions to create implementors of afscgap.model interfaces.

(c) 2024 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
from afscgap.typesdef import OPT_FLOAT
from afscgap.typesdef import OPT_INT


def get_opt_float(target) -> OPT_FLOAT:
    """Attempt to parse a value as a float, returning None if there is an error.

    Args:
        target: The value to try to interpret as a float.

    Returns:
        The value of target as a float or None if there was an issue in parsing
        like that target is None.
    """
    if target:
        try:
            return float(target)
        except ValueError:
            return None
    else:
        return None


def get_opt_int(target) -> OPT_INT:
    """Attempt to parse a value as an int, returning None if there is an error.

    Args:
        target: The value to try to interpret as an int.

    Returns:
        The value of target as an int or None if there was an issue in parsing
        like that target is None.
    """
    if target:
        try:
            return int(target)
        except ValueError:
            return None
    else:
        return None


def assert_float_present(target: OPT_FLOAT) -> float:
    """Assert that a value is non-None before returning that value.

    Args:
        target: The value to check if not None.

    Raises:
        AssertionError: Raised if target is None.

    Returns:
        The value of target if not None.
    """
    if target is None:
        raise ValueError('Encountered unexpected None.')

    return target


def assert_int_present(target: OPT_INT) -> int:
    """Assert that a value is non-None before returning that value.

    Args:
        target: The value to check if not None.

    Raises:
        AssertionError: Raised if target is None.

    Returns:
        The value of target if not None.
    """
    if target is None:
        raise ValueError('Encountered unexpected None.')

    return target
