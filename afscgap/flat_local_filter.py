"""
Utilities to describe and execute filters over downloaded results.

Utilities to describe and execute filters over downloaded results, typically after approximate
filters on precomputed indicies.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import functools
import typing

import afscgap.flat_model
import afscgap.model
import afscgap.param

from afscgap.flat_model import PARAMS_DICT


class LocalFilter:
    """Interface for a locally applied filter."""

    def __init__(self):
        """Create a new local filter."""
        raise NotImplementedError('Use implementor.')

    def matches(self, target: afscgap.model.Record) -> bool:
        """Determine if a value matches this filter.

        Args:
            target: The record to check for inclusion in results given this filter.

        Returns:
            True if the given record matches this filter so should be included in the results set
            and false otherwise.
        """
        raise NotImplementedError('Use implementor.')


class EqualsLocalFilter(LocalFilter):
    """A locally applied filter to check if an attribute matches an expected value."""

    def __init__(self, accessor, value):
        """Create a new equality filter which is applied locally.

        Args:
            accessor: Strategy (function) which, when given a afscgap.model.Record, returns the
                value to be tested.
            value: The expected value such that matching this value means that the record is
                included in the results.
        """
        self._accessor = accessor
        self._value = value

    def matches(self, target: afscgap.model.Record) -> bool:
        candidate = self._accessor(target)
        return self._value == candidate


class RangeLocalFilter(LocalFilter):
    """A locally applied filter to check if an attribute falls within a range."""

    def __init__(self, accessor, low_value, high_value):
        """Create a new locally applied range filter.

        Args:
            accessor: Strategy (function) which, when given a afscgap.model.Record, returns the
                value to be tested.
            low_value: The minimum value such that values lower are excluded from the results set or
                None if no minimum should be enforced.
            high_value: The maximum value such that values lower are excluded from the results set
                or None if no maximum should be enforced.
        """
        self._accessor = accessor
        self._low_value = low_value
        self._high_value = high_value

    def matches(self, target: afscgap.model.Record) -> bool:
        candidate = self._accessor(target)

        if candidate is None:
            return False

        satisfies_low = (self._low_value is None) or (candidate >= self._low_value)
        satisfies_high = (self._high_value is None) or (candidate <= self._high_value)
        return satisfies_low and satisfies_high


class LogicalAndLocalFilter(LocalFilter):
    """Filter which applies a logical and across one or more filters."""

    def __init__(self, inner_filters: typing.List[LocalFilter]):
        """Create a new logical and local filter.

        Create a new logical and local filter such that

        Args:
            inner_filters: The filter to place into a logical and relationship.
        """
        self._inner_filters = inner_filters

    def matches(self, target: afscgap.model.Record) -> bool:
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

FILTER_STRATEGIES = {
    'empty': lambda accessor, param: None,
    'equals': lambda accessor, param: EqualsLocalFilter(accessor, param.get_value()),
    'range': lambda accessor, param: RangeLocalFilter(accessor, param.get_low(), param.get_high())
}


def build_filter(params: PARAMS_DICT) -> LocalFilter:
    """Build a filter which describes a set of parameters.

    Args:
        params: The parameters dictionary for which to build a local filter.

    Returns:
        New filter which implements the given parameters into a local filter.
    """
    params_flat = params.items()
    params_keyed = map(lambda x: afscgap.param.FieldParam(x[0], x[1]), params_flat)
    params_required = filter(
        lambda x: not x.get_param().get_is_ignorable(),
        params_keyed
    )
    individual_filters_maybe = map(
        lambda x: build_individual_filter(x.get_field(), x.get_param()),
        params_required
    )
    individual_filters = filter(lambda x: x is not None, individual_filters_maybe)
    individual_filters_realized = list(individual_filters)
    return LogicalAndLocalFilter(individual_filters_realized)  # type: ignore


def build_individual_filter(field: str, param: afscgap.param.Param) -> typing.Optional[LocalFilter]:
    """Create a single filter which helps implement a param dict into a local index filter.

    Create a single filter which helps implement a param dict into a local index filter by operating
    on a single attribute.

    Args:
        field: The name of the field for which a filter is being bulit.
        param: The parameter to implement into a local filter.

    Returns:
        A local filter handling the given field.
    """
    filter_type = param.get_filter_type()

    if field not in ACCESSORS:
        raise RuntimeError('Unsupported or unknown field: %s' % field)

    if filter_type not in FILTER_STRATEGIES:
        raise RuntimeError('Unsupported filter type: %s' % filter_type)

    accessor = ACCESSORS[field]
    strategy = FILTER_STRATEGIES[filter_type]
    return strategy(accessor, param)
