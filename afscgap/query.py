def interpret_query_to_ords(target: dict) -> dict:
    target_items = target.items()

    def interpret_value(value):
        if not isinstance(value, tuple):
            return value

        if len(value) != 2:
            raise RuntimeError('Range param given without 2 elements.')

        if value[0] == None and value[1] == None:
            return None
        elif value[0] == None:
            return {"$lte": value[1]}
        elif value[1] == None:
            return {"$gte": value[0]}
        else:
            return {"$between": value}

    target_transform_items = map(
        lambda x: (x[0], interpret_value(x[1])),
        target_items
    )
    return dict(target_transform_items)


def interpret_query_to_py(target: dict) -> dict:
    target_items = target.items()

    def interpret_value(value):
        if isinstance(value, dict):
            raise RuntimeError('No ORDS params for presence_only=False.')

        if not isinstance(value, tuple):
            return lambda x: x == value

        if len(value) != 2:
            raise RuntimeError('Range param given without 2 elements.')

        if value[0] == None and value[1] == None:
            return lambda x: True
        elif value[0] == None:
            return lambda x: x <= value[1]
        elif value[1] == None:
            return lambda x: x >= value[0]
        else:
            return lambda x: x >= value[0] and x <= value[1]

    target_transform_items = map(
        lambda x: (x[0], interpret_value(x[1])),
        target_items
    )
    return dict(target_transform_items)
