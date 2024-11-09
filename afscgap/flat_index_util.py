import functools
import typing

import afscgap.convert
import afscgap.param


class IndexFilter:

    def __init__(self):
        raise NotImplementedError('Use implementor.')

    def get_index_available(self) -> bool:
        raise NotImplementedError('Use implementor.')

    def get_index_name(self) -> str:
        raise NotImplementedError('Use implementor.')

    def get_matches(self, target: typing.Union[float, int, str, None]) -> bool:
        raise NotImplementedError('Use implementor.')


class StringEqIndexFilter(IndexFilter):

    def __init__(self, index_name: str, param: afscgap.param.StrEqualsParam):
        self._index_name = index_name
        self._param = param

    def get_index_name(self) -> str:
        return self._index_name

    def get_matches(self, value) -> bool:
        return value is not None and value == self._param.get_value()


class StringRangeIndexFilter(IndexFilter):

    def __init__(self, index_name: str, param: afscgap.param.StrRangeParam):
        self._index_name = index_name
        self._param = param

    def get_index_name(self) -> str:
        return self._index_name

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

    def __init__(self, index_name: str, param: afscgap.param.IntEqualsParam):
        self._index_name = index_name
        self._param = param

    def get_index_name(self) -> str:
        return self._index_name

    def get_matches(self, value) -> bool:
        return value is not None and value == self._param.get_value()


class IntRangeIndexFilter(IndexFilter):

    def __init__(self, index_name: str, param: afscgap.param.IntRangeParam):
        self._index_name = index_name
        self._param = param

    def get_index_name(self) -> str:
        return self._index_name

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

    def __init__(self, index_name: str, param: afscgap.param.FloatEqualsParam):
        self._index_name = index_name
        self._param = param
        self._param_str = self._prep_string(self._param.get_value())

    def get_index_name(self) -> str:
        return self._index_name

    def get_matches(self, target) -> bool:
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

    def __init__(self, index_name: str, param: afscgap.param.FloatRangeParam):
        self._index_name = index_name
        self._param = param
        self._low_str = self._prep_string(self._param.get_low())
        self._high_str = self._prep_string(self._param.get_high())

    def get_index_name(self) -> str:
        return self._index_name

    def get_matches(self, target) -> bool:
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
        if target is None:
            return None
        else:
            return '%.2f' % target  # type: ignore


class DatetimeEqIndexFilter(IndexFilter):

    def __init__(self, index_name: str, param: afscgap.param.FloatEqualsParam):
        self._index_name = index_name
        self._param = param
        self._param_str = self._prep_string(self._param.get_value())

    def get_index_name(self) -> str:
        return self._index_name

    def get_matches(self, target) -> bool:
        value = self._prep_string(target)

        if value is None:
            return False
        else:
            return value == self._param_str

    def _prep_string(self, target) -> typing.Optional[str]:
        if target is None:
            return None
        else:
            return target.split('T')[0]  # type: ignore


class DatetimeRangeIndexFilter(IndexFilter):

    def __init__(self, index_name: str, param: afscgap.param.FloatRangeParam):
        self._index_name = index_name
        self._param = param
        self._low_str = self._prep_string(self._param.get_low())
        self._high_str = self._prep_string(self._param.get_high())

    def get_index_name(self) -> str:
        return self._index_name

    def get_matches(self, target) -> bool:
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
        if target is None:
            return None
        else:
            return target.split('T')[0]  # type: ignore


class UnitConversionIndexFilter(IndexFilter):

    def __init__(self, inner: IndexFilter, user_units: str, system_units: str):
        self._inner = inner
        self._user_units = user_units
        self._system_units = system_units

    def get_index_name(self) -> str:
        return self._inner.get_index_name()

    def get_matches(self, value) -> bool:
        original = float(value)
        converted = afscgap.convert.convert(original, self._system_units, self._user_units)
        return self._inner.get_matches(converted)


class LogicalOrIndexFilter(IndexFilter):

    def __init__(self, inners: typing.List[IndexFilter]):
        self._inners = inners

        names = map(lambda x: x.get_index_name(), self._inners)
        names_unique = set(names)

        if len(names_unique) != 1:
            raise RuntimeError('Logical or index filter uses exactly one index.')

        self._name = names_unique.pop()

    def get_index_name(self) -> str:
        return self._name

    def get_matches(self, value) -> bool:
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
    'area_swept_ha': ['area_swept_km'],
    'duration_hr': ['duration_hr']
}

FIELD_CONVERSIONS = {
    'cpue_kgha': {'user': 'kg/ha', 'system': 'kg/km2'},
    'cpue_kg1000km2': {'user': 'kg1000/km2', 'system': 'kg/km2'},
    'cpue_noha': {'user': 'no/ha', 'system': 'no/km2'},
    'cpue_no1000km2': {'user': 'no1000/km2', 'system': 'no/km2'},
    'area_swept_ha': {'user': 'ha', 'system': 'km'}
}

FIELD_DATA_TYPE_OVERRIDES = {'date_time': 'datetime'}

PRESENCE_ONLY_FIELDS = {'species_code', 'common_name', 'scientific_name'}


def decorate_filter(field: str, original: IndexFilter) -> IndexFilter:
    if field not in FIELD_CONVERSIONS:
        return original

    conversion = FIELD_CONVERSIONS[field]
    user_units = conversion['user']
    system_units = conversion['system']
    return UnitConversionIndexFilter(original, user_units, system_units)


def make_filters(field: str, param: afscgap.param.Param,
    presence_only: bool) -> typing.Iterable[IndexFilter]:
    if param.get_is_ignorable():
        return []

    filter_type = param.get_filter_type()
    if filter_type == 'empty':
        return []

    if (not presence_only) and (field in PRESENCE_ONLY_FIELDS):
        return []

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
