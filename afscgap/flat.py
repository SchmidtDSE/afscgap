import functools
import itertools
import typing

import afscgap.cursor
import afscgap.flat_http
import afscgap.flat_model
import afscgap.flat_cursor

from afscgap.flat_model import HAUL_KEYS, PARAMS_DICT, RECORDS

WARNING_THRESHOLD = 3000

LARGE_WARNING = ' '.join([
    'Your query may return a very large amount of records.',
    'Be sure to interact with results in a memory efficient way.'
])


def get_hauls(params: PARAMS_DICT, meta: afscgap.flat_model.ExecuteMetaParams) -> HAUL_KEYS:
    presence_only = meta.get_presence_only()
    
    params_flat = param_dict.items()
    params_keyed = map(lambda x: {'field': x[0], 'param': x[1]}, params_flat)
    params_required = filter(lambda x: not x['param'].get_is_ignorable(), params_keyed)
    index_filters_nest = map(
        lambda x: afscgap.flat_index_util.make_filters(x['field'], x['param'], presence_only),
        params_required
    )
    
    index_filters = itertools.chain(*index_filters_nest)
    index_filters_realized = list(index_filters)
    
    if len(index_filters_realized) == 0:
        return afscgap.flat_http.get_all_hauls(meta)
        
    haul_iterables = map(
        lambda x: afscgap.flat_http.get_hauls_for_index_filter(meta, x),
        index_filters_realized
    )
    haul_sets = map(lambda x: set(x), haul_iterables)
    return functools.reduce(lambda a, b: a.intersection(b), haul_sets)


def check_warning(hauls: HAUL_KEYS, meta: afscgap.flat_model.ExecuteMetaParams):
    if meta.get_suppress_large_warnin():
        return
    
    num_hauls = sum(map(lambda x: 1, hauls))

    if num_hauls > WARNING_THRESHOLD:
        meta.get_warn_func(LARGE_WARNING)
    

def execute(param_dict: PARAMS_DICT,
    meta: afscgap.flat_model.ExecuteMetaParams) -> afscgap.cursor.Cursor:
    local_filter = afscgap.flat_local_filter.build_filter(param_dict)
    hauls = get_hauls(param_dict, meta)
    
    hauls_realized = list(hauls)
    check_warning(hauls_realized, meta)
    
    candidate_records_nested = map(
        lambda x: get_records_for_haul(meta, x),
        hauls_realized
    )
    candidate_records = itertools.chain(*candidate_records_nested)
    records = filter(lambda x: local_filter.matches(x), candidate_records)
    
    limit = meta.get_limit()
    filtering_incomplete = meta.get_filter_incomplete()
    inner_cursor = afscgap.flat_cursor.FlatCursor(records, limit, filtering_incomplete)
    
    limit = meta.get_limit()
    cursor = afscgap.flat_cursor.LimitCursor(limit, inner_cursor) if limit else inner_cursor
    return cursor
