"""
(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.
"""
import numbers


def interpret_query_to_ords(target: dict) -> dict:
    """Convert a description of a query to ORDS syntax.

    Args:
        target: The "native Python structures" version of the query.

    Returns:
        Dicitionary encoding the ORDS-expected query format.
    """
    target_items = target.items()

    def interpret_value(value):
        if value is None:
            return None

        if not (isinstance(value, tuple) or isinstance(value, list)):
            return value

        if len(value) != 2:
            raise RuntimeError('Range param given without 2 elements.')

        lower_limit_given = value[0] is not None
        upper_limit_given = value[1] is not None
        lower_limit_infinity = not lower_limit_given
        upper_limit_infinity = not upper_limit_given

        if lower_limit_infinity and upper_limit_infinity:
            return None
        elif lower_limit_infinity:
            return {"$lte": value[1]}
        elif upper_limit_infinity:
            return {"$gte": value[0]}
        else:
            return {"$between": value}

    target_transform_items = map(
        lambda x: (x[0], interpret_value(x[1])),
        target_items
    )
    return dict(target_transform_items)


def interpret_query_to_py(target: dict) -> dict:
    """Emulate a query in Python.

    Args:
        target: The "native Python structures" format of the query.

    Returns:
        Dictionary mapping from key to function which returns if a candidate
        value for that field satisfies the criteria described for that field.
    """
    target_items = target.items()

    def interpret_value(value):
        if value is None:
            return None

        if isinstance(value, dict):
            raise RuntimeError('No ORDS params for presence_only=False.')

        if isinstance(value, numbers.Number):
            return lambda x: abs(x - value) < 0.00001

        if not isinstance(value, tuple):
            return lambda x: x == value

        if len(value) != 2:
            raise RuntimeError('Range param given without 2 elements.')

        lower_limit_given = value[0] is not None
        upper_limit_given = value[1] is not None
        lower_limit_infinity = not lower_limit_given
        upper_limit_infinity = not upper_limit_given

        if lower_limit_infinity and upper_limit_infinity:
            return lambda x: True
        elif lower_limit_infinity:
            return lambda x: x <= value[1]
        elif upper_limit_infinity:
            return lambda x: x >= value[0]
        else:
            return lambda x: x >= value[0] and x <= value[1]

    target_transform_items = map(
        lambda x: (x[0], interpret_value(x[1])),
        target_items
    )
    return dict(target_transform_items)
