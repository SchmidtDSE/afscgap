"""
Description of request parameters to be used with any implementing backend.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
from afscgap.typesdef import OPT_FLOAT
from afscgap.typesdef import OPT_INT
from afscgap.typesdef import OPT_STR


class Param:
    """Interface for a backend-agnotic parameter."""

    def __init__(self):
        """Create a new parameter."""
        raise NotImplementedError('Use implementor.')

    def get_is_ignorable(self) -> bool:
        """Determine if this parameter can be ignored during filtering operations.

        Returns:
            True if ignorable and false otherwise.
        """
        raise NotImplementedError('Use implementor.')

    def get_data_type(self) -> str:
        """Get the data type of field on which this parameter operates.

        Returns:
            Data type of the field like "str".
        """
        raise NotImplementedError('Use implementor.')

    def get_filter_type(self) -> str:
        """Get the type of filter being applied by this parameter.

        Returns:
            Get the type of filter like "equals" being applied.
        """
        raise NotImplementedError('Use implementor.')


class FieldParam:
    """Parameter which operates on a specific field."""

    def __init__(self, field: str, param: Param):
        """Create a new field-specific parameter."""
        self._field = field
        self._param = param

    def get_field(self) -> str:
        """Get the name of the field on which this parameter operates.

        Returns:
            Name of the field on which this parameter operates.
        """
        return self._field

    def get_param(self) -> Param:
        """Get the parameter to apply to this field.

        Returns:
            Object describing the parameter to apply to this field.
        """
        return self._param


class EmptyParam(Param):
    """Parameter indicating that all records should be included."""

    def __init__(self):
        """Create a parameter which matches all records."""
        pass

    def get_is_ignorable(self) -> bool:
        return True

    def get_data_type(self) -> str:
        return 'None'

    def get_filter_type(self) -> str:
        return 'empty'


class StrEqualsParam(Param):
    """Parameter which requires a field to have a specific string value."""

    def __init__(self, value: str):
        """Create a new string equals parameter.

        Args:
            value: The string value that the field must have in order for its parent record to be
                included in the results set.
        """
        self._value = value

    def get_value(self) -> str:
        """Get the value that needs to be matched.

        Returns:
            String value that must be matched in order ofr a record to be included.
        """
        return self._value

    def get_is_ignorable(self) -> bool:
        return False

    def get_data_type(self) -> str:
        return 'str'

    def get_filter_type(self) -> str:
        return 'equals'


class StrRangeParam(Param):
    """Parameter which requires a field to fall within an alphanumeric range."""

    def __init__(self, low: OPT_STR, high: OPT_STR):
        """Create a new string range parameter.

        Args:
            low: The minimum value that a field may have for its record to be included or None if
                no minimum to be enforced.
            high: The maximum value that a field may have for its record to be incldued or None if
                no maximum to be enforced.
        """
        self._low = low
        self._high = high

    def get_low(self) -> OPT_STR:
        """Get the minimum allowed value.

        Returns:
            The minimum value that a field may have for its record to be included or None if no
            minimum to be enforced.
        """
        return self._low

    def get_high(self) -> OPT_STR:
        """Get the maximum allowed value.

        Returns:
            The maximum value that a field may have for its record to be incldued or None if no
            maximum to be enforced.
        """
        return self._high

    def get_is_ignorable(self) -> bool:
        return False

    def get_data_type(self) -> str:
        return 'str'

    def get_filter_type(self) -> str:
        return 'range'


class IntEqualsParam(Param):
    """Parameter which requires a field to have a specific integer value."""

    def __init__(self, value: int):
        """Create a new int equals parameter.

        Args:
            value: The int value that the field must have in order for its parent record to be
                included in the results set.
        """
        self._value = value

    def get_value(self) -> int:
        """Get the value that needs to be matched.

        Returns:
            Integer value that must be matched in order ofr a record to be included.
        """
        return self._value

    def get_is_ignorable(self) -> bool:
        return False

    def get_data_type(self) -> str:
        return 'int'

    def get_filter_type(self) -> str:
        return 'equals'


class IntRangeParam(Param):
    """Parameter which requires a field to fall within an range defined by up to two integers."""

    def __init__(self, low: OPT_INT, high: OPT_INT):
        """Create a new integer range parameter.

        Args:
            low: The minimum value that a field may have for its record to be included or None if
                no minimum to be enforced.
            high: The maximum value that a field may have for its record to be incldued or None if
                no maximum to be enforced.
        """
        self._low = low
        self._high = high

    def get_low(self) -> OPT_INT:
        """Get the minimum allowed value.

        Returns:
            The minimum value that a field may have for its record to be included or None if no
            minimum to be enforced.
        """
        return self._low

    def get_high(self) -> OPT_INT:
        """Get the maximum allowed value.

        Returns:
            The maximum value that a field may have for its record to be incldued or None if no
            maximum to be enforced.
        """
        return self._high

    def get_is_ignorable(self) -> bool:
        return False

    def get_data_type(self) -> str:
        return 'int'

    def get_filter_type(self) -> str:
        return 'range'


class FloatEqualsParam(Param):
    """Parameter which requires a field to have a specific floating point value."""

    def __init__(self, value: float):
        """Create a new float equals parameter.

        Args:
            value: The float value that the field must have in order for its parent record to be
                included in the results set.
        """
        self._value = value

    def get_value(self) -> float:
        """Get the value that needs to be matched.

        Returns:
            Float value that must be matched in order ofr a record to be included.
        """
        return self._value

    def get_is_ignorable(self) -> bool:
        return False

    def get_data_type(self) -> str:
        return 'float'

    def get_filter_type(self) -> str:
        return 'equals'


class FloatRangeParam(Param):
    """Parameter which requires a field to fall within an range defined by up to two floats."""

    def __init__(self, low: OPT_FLOAT, high: OPT_FLOAT):
        """Create a new float range parameter.

        Args:
            low: The minimum value that a field may have for its record to be included or None if
                no minimum to be enforced.
            high: The maximum value that a field may have for its record to be incldued or None if
                no maximum to be enforced.
        """
        self._low = low
        self._high = high

    def get_low(self) -> OPT_FLOAT:
        """Get the minimum allowed value.

        Returns:
            The minimum value that a field may have for its record to be included or None if no
            minimum to be enforced.
        """
        return self._low

    def get_high(self) -> OPT_FLOAT:
        """Get the maximum allowed value.

        Returns:
            The maximum value that a field may have for its record to be incldued or None if no
            maximum to be enforced.
        """
        return self._high

    def get_is_ignorable(self) -> bool:
        return False

    def get_data_type(self) -> str:
        return 'float'

    def get_filter_type(self) -> str:
        return 'range'
