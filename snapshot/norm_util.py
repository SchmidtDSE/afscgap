"""
Logic to consistently normalize values for indicies.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import typing

import const

T = typing.TypeVar('T')


def normalize_value(key: str, value: typing.Optional[T]) -> typing.Optional[T]:
    """Normalize a record value.

    Normalize a record value so that it can be used to generate bins of haul keys, rounding or
    truncating in an expected way.

    Args:
        key: The property key for which a value should be normalized.
        target: The record whose value should be updated.

    Returns:
        The record after its value attribute has been normalized if required or target unmodified
        if no changes made.
    """
    if value is None:
        return None
    else:
        if key in const.REQUIRES_ROUNDING:
            return '%.2f' % value  # type: ignore
        elif key in const.REQUIRES_DATE_ROUND:
            return value.split('T')[0]  # type: ignore
        else:
            return value
