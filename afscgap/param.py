from afscgap.typesdef import OPT_FLOAT
from afscgap.typesdef import OPT_INT
from afscgap.typesdef import OPT_STR


class Param:

    def __init__(self):
        raise NotImplementedError('Use implementor.')

    def get_is_ignorable(self) -> bool:
        raise NotImplementedError('Use implementor.')

    def get_data_type(self) -> str:
        raise NotImplementedError('Use implementor.')

    def get_filter_type(self) -> str:
        raise NotImplementedError('Use implementor.')


class FieldParam:

    def __init__(self, field: str, param: Param):
        self._field = field
        self._param = param

    def get_field(self) -> str:
        return self._field

    def get_param(self) -> Param:
        return self._param


class EmptyParam(Param):

    def get_is_ignorable(self) -> bool:
        return True

    def get_data_type(self) -> str:
        return 'None'

    def get_filter_type(self) -> str:
        return 'empty'


class StrEqualsParam(Param):

    def __init__(self, value: str):
        self._value = value

    def get_value(self) -> str:
        return self._value

    def get_is_ignorable(self) -> bool:
        return False

    def get_data_type(self) -> str:
        return 'str'

    def get_filter_type(self) -> str:
        return 'equals'


class StrRangeParam(Param):

    def __init__(self, low: OPT_STR, high: OPT_STR):
        self._low = low
        self._high = high

    def get_low(self) -> OPT_STR:
        return self._low

    def get_high(self) -> OPT_STR:
        return self._high

    def get_is_ignorable(self) -> bool:
        return False

    def get_data_type(self) -> str:
        return 'str'

    def get_filter_type(self) -> str:
        return 'range'


class IntEqualsParam(Param):

    def __init__(self, value: int):
        self._value = value

    def get_value(self) -> int:
        return self._value

    def get_is_ignorable(self) -> bool:
        return False

    def get_data_type(self) -> str:
        return 'int'

    def get_filter_type(self) -> str:
        return 'equals'


class IntRangeParam(Param):

    def __init__(self, low: OPT_INT, high: OPT_INT):
        self._low = low
        self._high = high

    def get_low(self) -> OPT_INT:
        return self._low

    def get_high(self) -> OPT_INT:
        return self._high

    def get_is_ignorable(self) -> bool:
        return False

    def get_data_type(self) -> str:
        return 'int'

    def get_filter_type(self) -> str:
        return 'range'


class FloatEqualsParam(Param):

    def __init__(self, value: int):
        self._value = value

    def get_value(self) -> int:
        return self._value

    def get_is_ignorable(self) -> bool:
        return False

    def get_data_type(self) -> str:
        return 'int'

    def get_filter_type(self) -> str:
        return 'equals'


class FloatRangeParam(Param):

    def __init__(self, low: OPT_FLOAT, high: OPT_FLOAT):
        self._low = low
        self._high = high

    def get_low(self) -> OPT_FLOAT:
        return self._low

    def get_high(self) -> OPT_FLOAT:
        return self._high

    def get_is_ignorable(self) -> bool:
        return False

    def get_data_type(self) -> str:
        return 'float'

    def get_filter_type(self) -> str:
        return 'range'
