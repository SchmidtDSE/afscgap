import functools

import afscgap.flat_model
import afscgap.param

from afscgap.flat_model import PARAMS_DICT


class LocalFilter:
    
    def __init__(self):
        raise NotImplementedError('Use implementor.')
    
    def matches(self, target: afscgap.flat_model.FlatRecord) -> bool:
        raise NotImplementedError('Use implementor.')


class EqualsLocalFilter(LocalFilter):
    
    def __init__(self, accessor, value):
        self._accessor = accessor
        self._value = value
    
    def matches(self, target: afscgap.flat_model.FlatRecord) -> bool:
        candidate = self._accessor(target)
        return self._value == candidate


class RangeLocalFilter(LocalFilter):
    
    def __init__(self, accessor, low_value, high_value):
        self._accessor = accessor
        self._low_value = low_value
        self._high_value = high_value
    
    def matches(self, target: afscgap.flat_model.FlatRecord) -> bool:
        candidate = self._accessor(target)
        satisfies_low = (self._low_value is None) or (candidate >= self._low_value)
        satisifes_high = (self._high_value is None) or (candidate <= self._high_value)
        return satisfies_low and satisfies_high


class LogicalAndLocalFilter(LocalFilter):
    
    def __init__(self, inner_filters: typing.List[LocalFilter]):
        self._inner_filters = inner_filters
    
    def matches(self, target: afscgap.flat_model.FlatRecord) -> bool:
        individual_values = map(lambda x: x.matches(target), self._inner_filters)
        return functools.reduce(lambda a, b: a and b, individual_values, True)


ACCESSORS = {
    'year': lambda x: x.get_year(),
    'srvy': lambda x: x.get_srvy(),
    'survey': lambda x: x.get_survey(),
    'survey_id': lambda x: x.get_survey_id(),
    'cruise': lambda x: x.get_cruise(),
    'haul': lambda x: x.get_haul(),
    'stratum': lambda x: x.get_stratum(),
    'station': lambda x: x.get_station(),
    'vessel_name': lambda x: x.get_vessel_name(),
    'vessel_id': lambda x: x.get_vessel_id(),
    'date_time': lambda x: x.get_date_time(),
    'latitude_dd': lambda x: x.get_latitude(units='dd'),
    'longitude_dd': lambda x: x.get_longitude(units='dd'),
    'species_code': lambda x: x.get_species_code(),
    'common_name': lambda x: x.get_common_name(),
    'scientific_name': lambda x: x.get_scientific_name(),
    'taxon_confidence': lambda x: x.get_taxon_confidence(),
    'cpue_kgha': lambda x: x.get_cpue_weight_maybe(units='kg/ha'),
    'cpue_kgkm2': lambda x: x.get_cpue_weight_maybe(units='kg/km2'),
    'cpue_kg1000km2': lambda x: x.get_cpue_weight_maybe(units='kg1000/km2'),
    'cpue_noha': lambda x: x.get_cpue_count_maybe(units='no/ha'),
    'cpue_nokm2': lambda x: x.get_cpue_count_maybe(units='no/km2'),
    'cpue_no1000km2': lambda x: x.get_cpue_count_maybe(units='no1000/km2'),
    'weight_kg': lambda x: x.get_weight_maybe(units='kg'),
    'count': lambda x: x.get_count_maybe(),
    'bottom_temperature_c': lambda x: x.get_bottom_temperature_maybe(units='c'),
    'surface_temperature_c': lambda x: x.get_surface_temperature_maybe(units='c'),
    'depth_m': lambda x: x.get_depth(units='m'),
    'distance_fished_km': lambda x: x.get_depth(units='km'),
    'net_width_m': lambda x: x.get_net_width(units='m'),
    'net_height_m': lambda x: x.get_net_height(units='m'),
    'area_swept_ha': lambda x: x.get_area_swept(units='ha'),
    'duration_hr': lambda x: x.get_duration(units='hr')
}


def build_individual_filter(field: str, param: afscgap.param.Param) -> LocalFilter:
    accessor = ACCESSORS[field]
    
    filter_type = param.get_filter_type()
    if filter_type == 'equals':
        return EqualsLocalFilter(accessor, param.get_value())  # type: ignore
    elif filter_type == 'range':
        return EqualsLocalFilter(accessor, param.get_low(), param.get_high())   # type: ignore
    else:
        raise RuntimeError('Unsupported filter type: %s' % filter_type)


def build_filter(params: PARAMS_DICT) -> LocalFilter:
    params_flat = params.items()
    params_keyed = map(lambda x: {'field': x[0], 'param': x[1]}, params_flat)
    params_required = filter(lambda x: not x['param'].get_is_ignorable(), params_keyed)
    individual_filters = map(build_individual_filter, params_required)
    individual_filters_realized = list(individual_filters)
    return LogicalAndLocalFilter(individual_filters_realized)
