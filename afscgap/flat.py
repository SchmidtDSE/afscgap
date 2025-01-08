"""
Entrypoint for logic to use prejoined Avro flat files.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import functools
import itertools
import warnings

import afscgap.cursor
import afscgap.flat_http
import afscgap.flat_local_filter
import afscgap.flat_model
import afscgap.flat_cursor

from afscgap.flat_model import HAUL_KEYS, PARAMS_DICT, RECORDS

WARNING_THRESHOLD = 3000

LARGE_WARNING = ' '.join([
    'Your query may return a very large amount of records.',
    'Be sure to interact with results in a memory efficient way.'
])


def get_hauls(params: PARAMS_DICT, meta: afscgap.flat_model.ExecuteMetaParams) -> HAUL_KEYS:
    """Get the hauls matching a set of parameters.

    Args:
        params: Set of parameters to apply when determining which records should be included in the
            results set.
        meta: Set of configuration parameters to use when making requests for Avro flat files.

    Returns:
        Iterable over matching hauls. All relevant results will be included in this iterable but it
        may also include irrelevant results, requiring further local filtering.
    """
    presence_only = meta.get_presence_only()

    params_flat = params.items()
    params_keyed = map(lambda x: afscgap.param.FieldParam(x[0], x[1]), params_flat)
    params_required = filter(lambda x: not x.get_param().get_is_ignorable(), params_keyed)
    index_filters_nest = map(lambda x: afscgap.flat_index_util.make_filters(
        x.get_field(),
        x.get_param(),
        presence_only
    ), params_required)

    index_filters = itertools.chain(*index_filters_nest)
    index_filters_realized = list(index_filters)

    if len(index_filters_realized) == 0:
        return afscgap.flat_http.get_all_hauls(meta)

    haul_iterables = map(
        lambda x: afscgap.flat_http.get_hauls_for_index_filter(meta, x),
        index_filters_realized
    )
    haul_sets = map(lambda x: set(x), haul_iterables)
    return functools.reduce(lambda a, b: a.intersection(b), haul_sets)  # type: ignore


def check_warning(hauls: HAUL_KEYS, meta: afscgap.flat_model.ExecuteMetaParams):
    """Check if a large payload warning should be emitted.

    Check if a large payload warning should be emitted, creating that warning through the method
    indicated by the provided meta parameter if meeting criteria specified by that same parameter.

    Args:
        hauls: Iterable over haul keys to be downloaded.
        meta: Set of configuration parameters to use when making requests for Avro flat files.
    """
    if meta.get_suppress_large_warning():
        return

    num_hauls = sum(map(lambda x: 1, hauls))

    if num_hauls > WARNING_THRESHOLD:
        warn_func = meta.get_warn_func()
        warn_func_realized = warnings.warn if warn_func is None else warn_func
        warn_func_realized(LARGE_WARNING)  # type: ignore


def execute(param_dict: PARAMS_DICT,
    meta: afscgap.flat_model.ExecuteMetaParams) -> afscgap.cursor.Cursor:
    """Execute a AFSC GAP request using prejoined flat Avro files.

    Args:
        param_dict: Dictionary describing the parameters with which to execute this request.
        meta: Set of configuration parameters to use when making requests for Avro flat files.

    Returns:
        Iterable over matching results.
    """
    local_filter = afscgap.flat_local_filter.build_filter(param_dict)
    hauls = get_hauls(param_dict, meta)

    hauls_realized = list(hauls)
    check_warning(hauls_realized, meta)

    candidate_records_nested = map(
        lambda x: afscgap.flat_http.get_records_for_haul(meta, x),
        hauls_realized
    )
    candidate_records: RECORDS = itertools.chain(*candidate_records_nested)
    records: RECORDS = filter(lambda x: local_filter.matches(x), candidate_records)

    limit = meta.get_limit()
    raw_cursor = afscgap.flat_cursor.FlatCursor(records)

    no_incomplete = meta.get_filter_incomplete()
    filter_cursor = afscgap.flat_cursor.CompleteCursor(raw_cursor) if no_incomplete else raw_cursor

    limit = meta.get_limit()
    cursor = afscgap.flat_cursor.LimitCursor(filter_cursor, limit) if limit else filter_cursor

    return cursor
