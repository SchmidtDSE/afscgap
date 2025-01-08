"""
Utilities to describe and execute filters over precomputed indicies.

Utilities to describe and execute filters over precomputed indicies which, provided in Avro, may
help avoid requesting unnecessary catches.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import functools
import itertools
import typing

import afscgap.convert
import afscgap.param

MATCH_TARGET = typing.Union[float, int, str, None]
STRS = typing.Iterable[str]


class IndexFilter:
    """Interface for a filter against a precomupted index."""

    def __init__(self):
        """Create a new index filter."""
        raise NotImplementedError('Use implementor.')

    def get_index_names(self) -> STRS:
        """Get the name of the precomputed index to use to filter results.

        Returns:
            The name of the precomputed index which can be used to execute this filter.
        """
        raise NotImplementedError('Use implementor.')

    def get_matches(self, target: MATCH_TARGET) -> bool:
        """Determine a value matches this filter.

        Args:
            target: The value to test if matches this filter.

        Returns:
            True if this matches this filter's critera for being included in results for False
            otherwise.
        """
        raise NotImplementedError('Use implementor.')


class StringEqIndexFilter(IndexFilter):
    """Precomputed index filter that checks for string equality."""

    def __init__(self, index_name: str, param: afscgap.param.StrEqualsParam):
        """Create a new string equals filter.

        Args:
            index_name: The name of the precomputed index filter to use for finding results.
            param: The string equals parameter to apply to the precomputed index.
        """
        self._index_name = index_name
        self._param = param

    def get_index_names(self) -> STRS:
        return [self._index_name]

    def get_matches(self, value) -> bool:
        return value is not None and value == self._param.get_value()


class StringRangeIndexFilter(IndexFilter):
    """Precomputed index filter that checks for string within alphanumeric range."""

    def __init__(self, index_name: str, param: afscgap.param.StrRangeParam):
        """Create a new string range filter.

        Args:
            index_name: The name of the precomputed index filter to use for finding results.
            param: The string range parameter to apply to the precomputed index.
        """
        self._index_name = index_name
        self._param = param

    def get_index_names(self) -> STRS:
        return [self._index_name]

    def get_matches(self, value) -> bool:
        if value is None:
            return False

        if self._param.get_low() is not None:
            satisfies_low = value >= self._param.get_low()
        else:
            satisfies_low = True

        if self._param.get_high() is not None:
            satisfies_high = value <= self._param.get_high()
        else:
            satisfies_high = True

        return satisfies_low and satisfies_high


class IntEqIndexFilter(IndexFilter):
    """Precomputed index filter that checks for integer equality."""

    def __init__(self, index_name: str, param: afscgap.param.IntEqualsParam):
        """Create a new integer equals filter.

        Args:
            index_name: The name of the precomputed index filter to use for finding results.
            param: The integer equals parameter to apply to the precomputed index.
        """
        self._index_name = index_name
        self._param = param

    def get_index_names(self) -> STRS:
        return [self._index_name]

    def get_matches(self, value) -> bool:
        return value is not None and value == self._param.get_value()


class IntRangeIndexFilter(IndexFilter):
    """Precomputed index filter that checks for an integer in a range."""

    def __init__(self, index_name: str, param: afscgap.param.IntRangeParam):
        """Create a new integer range filter.

        Args:
            index_name: The name of the precomputed index filter to use for finding results.
            param: The integer range parameter to apply to the precomputed index.
        """
        self._index_name = index_name
        self._param = param

    def get_index_names(self) -> STRS:
        return [self._index_name]

    def get_matches(self, value) -> bool:
        if value is None:
            return False

        if self._param.get_low() is not None:
            satisfies_low = value >= self._param.get_low()
        else:
            satisfies_low = True

        if self._param.get_high() is not None:
            satisfies_high = value <= self._param.get_high()
        else:
            satisfies_high = True

        return satisfies_low and satisfies_high


class FloatEqIndexFilter(IndexFilter):
    """Precomputed index filter that checks for float approximate equality."""

    def __init__(self, index_name: str, param: afscgap.param.FloatEqualsParam):
        """Create a new float approximate equals filter.

        Args:
            index_name: The name of the precomputed index filter to use for finding results.
            param: The float equals parameter to apply to the precomputed index.
        """
        self._index_name = index_name
        self._param = param
        self._param_str = self._prep_string(self._param.get_value())

    def get_index_names(self) -> STRS:
        return [self._index_name]

    def get_matches(self, target: MATCH_TARGET) -> bool:
        value = self._prep_string(target)

        if value is None:
            return False
        else:
            return value == self._param_str

    def _prep_string(self, target) -> typing.Optional[str]:
        if target is None:
            return None
        else:
            return '%.2f' % target  # type: ignore


class FloatRangeIndexFilter(IndexFilter):
    """Precomputed index filter that checks for an floating point value in a range.

    Precomputed index filter that checks for an floating point value in a range, using an
    approximation. This will require local filtering to apply precision.
    """

    def __init__(self, index_name: str, param: afscgap.param.FloatRangeParam):
        """Create a new float approximate range filter.

        Args:
            index_name: The name of the precomputed index filter to use for finding results.
            param: The float range parameter to apply to the precomputed index.
        """
        self._index_name = index_name
        self._param = param
        self._low_str = self._prep_string(self._param.get_low())
        self._high_str = self._prep_string(self._param.get_high())

    def get_index_names(self) -> STRS:
        return [self._index_name]

    def get_matches(self, target: MATCH_TARGET) -> bool:
        value = self._prep_string(target)

        if value is None:
            return False

        if self._low_str is not None:
            satisfies_low = value >= self._low_str
        else:
            satisfies_low = True

        if self._high_str is not None:
            satisfies_high = value <= self._high_str
        else:
            satisfies_high = True

        return satisfies_low and satisfies_high

    def _prep_string(self, target) -> typing.Optional[str]:
        """Get a string which matches approximation / rounding used in the precomputed index.

        Args:
            target: The value to be converted to the index approximation / rounding.

        Returns:
            String describing the approximation / rounding of the input value which would be found
            in the precomputed index.
        """
        if target is None:
            return None
        else:
            return '%.2f' % target  # type: ignore


class DatetimeEqIndexFilter(IndexFilter):
    """Precomputed index filter that checks for approximate datetime equality."""

    def __init__(self, index_name: str, param: afscgap.param.FloatEqualsParam):
        """Create a new datetime approximate equals filter.

        Args:
            index_name: The name of the precomputed index filter to use for finding results.
            param: The float equals parameter to apply to the precomputed index.
        """
        self._index_name = index_name
        self._param = param
        self._param_str = self._prep_string(self._param.get_value())

    def get_index_names(self) -> STRS:
        return [self._index_name]

    def get_matches(self, target: MATCH_TARGET) -> bool:
        value = self._prep_string(target)

        if value is None:
            return False
        else:
            return value == self._param_str

    def _prep_string(self, target) -> typing.Optional[str]:
        """Get a string which matches approximation / rounding used in the precomputed index.

        Args:
            target: The value to be converted to the index approximation / rounding.

        Returns:
            String describing the approximation / rounding of the input value which would be found
            in the precomputed index.
        """
        if target is None:
            return None
        else:
            return target.split('T')[0]  # type: ignore


class DatetimeRangeIndexFilter(IndexFilter):
    """Precomputed index filter that checks for a datetime value in a range.

    Precomputed index filter that checks for an datetime value in a range, using an approximation.
    This will require local filtering to apply precision.
    """

    def __init__(self, index_name: str, param: afscgap.param.FloatRangeParam):
        """Create a new datetime approximate range filter.

        Args:
            index_name: The name of the precomputed index filter to use for finding results.
            param: The datetime range parameter to apply to the precomputed index.
        """
        self._index_name = index_name
        self._param = param
        self._low_str = self._prep_string(self._param.get_low())
        self._high_str = self._prep_string(self._param.get_high())

    def get_index_names(self) -> STRS:
        return [self._index_name]

    def get_matches(self, target: MATCH_TARGET) -> bool:
        value = self._prep_string(target)

        if value is None:
            return False

        if self._low_str is not None:
            satisfies_low = value >= self._low_str
        else:
            satisfies_low = True

        if self._high_str is not None:
            satisfies_high = value <= self._high_str
        else:
            satisfies_high = True

        return satisfies_low and satisfies_high

    def _prep_string(self, target) -> typing.Optional[str]:
        """Get a string which matches approximation / rounding used in the precomputed index.

        Args:
            target: The value to be converted to the index approximation / rounding.

        Returns:
            String describing the approximation / rounding of the input value which would be found
            in the precomputed index.
        """
        if target is None:
            return None
        else:
            return target.split('T')[0]  # type: ignore


class UnitConversionIndexFilter(IndexFilter):
    """Index filter decorator which performs a unit conversion prior to applying an inner filter."""

    def __init__(self, inner: IndexFilter, user_units: str, system_units: str):
        """Create a new decorator which applies a unit conversion prior to calling an inner filter.

        Args:
            inner: The underlying filter to decorate.
            user_units: Units exepected by the inner filter.
            system_units: Original units within the underlying data.
        """
        self._inner = inner
        self._user_units = user_units
        self._system_units = system_units

    def get_index_names(self) -> typing.Iterable[str]:
        return self._inner.get_index_names()

    def get_matches(self, value: MATCH_TARGET) -> bool:
        if value is None:
            converted = None
        else:
            original = float(value)  # type: ignore
            converted = afscgap.convert.convert(original, self._system_units, self._user_units)

        return self._inner.get_matches(converted)


class LogicalOrIndexFilter(IndexFilter):
    """A composite index filter which applies a logical or between multiple inner filters."""

    def __init__(self, inners: typing.List[IndexFilter]):
        """Create a new logical or index filter.

        Args:
            inners: The filters to apply, reporting True if any match or False if none match.
        """
        self._inners = inners

        names = itertools.chain(*map(lambda x: x.get_index_names(), self._inners))
        names_unique = set(names)

        if len(names_unique) == 0:
            raise RuntimeError('Logical or index filter requires one or more index.')

        self._names = list(names_unique)

    def get_index_names(self) -> STRS:
        return self._names

    def get_matches(self, value: MATCH_TARGET) -> bool:
        matches = map(lambda x: x.get_matches(value), self._inners)
        return functools.reduce(lambda a, b: a or b, matches)


STRATEGIES = {
    'str': {
        'equals': StringEqIndexFilter,
        'range': StringRangeIndexFilter
    },
    'int': {
        'equals': IntEqIndexFilter,
        'range': IntRangeIndexFilter
    },
    'float': {
        'equals': FloatEqIndexFilter,
        'range': FloatRangeIndexFilter
    },
    'datetime': {
        'equals': DatetimeEqIndexFilter,
        'range': DatetimeRangeIndexFilter
    }
}

INDICIES = {
    'year': ['year'],
    'srvy': ['srvy'],
    'survey': ['survey'],
    'stratum': ['stratum'],
    'station': ['station'],
    'vessel_name': ['vessel_name'],
    'vessel_id': ['vessel_id'],
    'date_time': ['date_time'],
    'latitude_dd': ['latitude_dd_start', 'latitude_dd_end'],
    'longitude_dd': ['longitude_dd_start', 'longitude_dd_end'],
    'species_code': ['species_code'],
    'common_name': ['common_name'],
    'scientific_name': ['scientific_name'],
    'taxon_confidence': ['taxon_confidence'],
    'cpue_kgha': ['cpue_kgkm2'],
    'cpue_kgkm2': ['cpue_kgkm2'],
    'cpue_kg1000km2': ['cpue_kgkm2'],
    'cpue_noha': ['cpue_nokm2'],
    'cpue_nokm2': ['cpue_nokm2'],
    'cpue_no1000km2': ['cpue_nokm2'],
    'weight_kg': ['weight_kg'],
    'count': ['count'],
    'bottom_temperature_c': ['bottom_temperature_c'],
    'surface_temperature_c': ['surface_temperature_c'],
    'depth_m': ['depth_m'],
    'distance_fished_km': ['distance_fished_km'],
    'net_width_m': ['net_width_m'],
    'net_height_m': ['net_height_m'],
    'area_swept_ha': ['area_swept_km2'],
    'duration_hr': ['duration_hr']
}

FIELD_CONVERSIONS = {
    'cpue_kgha': {'user': 'kg/ha', 'system': 'kg/km2'},
    'cpue_kg1000km2': {'user': 'kg1000/km2', 'system': 'kg/km2'},
    'cpue_noha': {'user': 'no/ha', 'system': 'no/km2'},
    'cpue_no1000km2': {'user': 'no1000/km2', 'system': 'no/km2'},
    'area_swept_ha': {'user': 'ha', 'system': 'km2'}
}

FIELD_DATA_TYPE_OVERRIDES = {'date_time': 'datetime'}

# These fields, when indexed, ignore zero values. If not presence only, these need to be included.
PRESENCE_ONLY_FIELDS = {'species_code', 'common_name', 'scientific_name'}


def decorate_filter(field: str, original: IndexFilter) -> IndexFilter:
    """Decorate a filter for unit conversion or other preprocessing if required.

    Args:
        field: The name of the underlying field for which decoration should be applied.
        original: The undeocrated index filter.

    Returns:
        Decorated filter if decoration was required or original if not.
    """
    if field not in FIELD_CONVERSIONS:
        return original

    conversion = FIELD_CONVERSIONS[field]
    user_units = conversion['user']
    system_units = conversion['system']
    return UnitConversionIndexFilter(original, user_units, system_units)


def determine_if_ignorable(field: str, param: afscgap.param.Param, presence_only: bool) -> bool:
    """Determine if a field parameter is ignored for pre-filtering.

    Determine if a field parameter is ignored for pre-filtering, turning it into a noop because
    pre-filtering isn't possible or precomputed indicies are not available.

    Args:
        field: The name of the field for which filters should be made.
        param: The parameter to apply for the field.
        presence_only: Flag indicating if the query is for presence so zero inference records can be
            excluded.

    Returns:
        True if ignorable and false otherwise.
    """
    if param.get_is_ignorable():
        return True

    # If the field index is presence only and this isn't a presence only request, the index must be
    # ignored (cannot be used to pre-filter results).
    zero_inference_required = not presence_only
    field_index_excludes_zeros = field in PRESENCE_ONLY_FIELDS
    if zero_inference_required and field_index_excludes_zeros:
        return True

    filter_type = param.get_filter_type()
    if filter_type == 'empty':
        return True

    return False


def make_filters(field: str, param: afscgap.param.Param,
    presence_only: bool) -> typing.Iterable[IndexFilter]:
    """Make filters for a field describing a backend-agnostic parameter.

    Args:
        field: The name of the field for which filters should be made.
        param: The parameter to apply for the field.
        presence_only: Flag indicating if the query is for presence so zero inference records can be
            excluded.

    Returns:
        Iterable over filters which implement the given parameter for precomputed indicies. This may
        be approximated such that all matching results are included in results but some results may
        included may not match, requiring re-evaluation locally.
    """
    if determine_if_ignorable(field, param, presence_only):
        return []

    filter_type = param.get_filter_type()

    if field in FIELD_DATA_TYPE_OVERRIDES:
        data_type = FIELD_DATA_TYPE_OVERRIDES[field]
    else:
        data_type = param.get_data_type()

    data_type_strategies = STRATEGIES.get(data_type, None)
    if data_type_strategies is None:
        raise RuntimeError('Could not find filter strategy for type %s.' % data_type)

    init_strategy = data_type_strategies.get(filter_type, None)
    if init_strategy is None:
        raise RuntimeError('Could not find filter strategy for type %s.' % filter_type)

    indicies = INDICIES.get(field, [])
    if len(indicies) == 0:
        return []

    undecorated_filters = map(lambda x: init_strategy(x, param), indicies)
    decorated_filters = map(lambda x: decorate_filter(field, x), undecorated_filters)
    decorated_filters_realized = list(decorated_filters)
    return [LogicalOrIndexFilter(decorated_filters_realized)]
