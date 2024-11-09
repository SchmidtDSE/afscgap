import itertools

import fastavro

import afscgap.flat_index_util
import afscgap.flat_model
import afscgap.http_util

from afscgap.flat_model import HAUL_KEYS, RECORDS
from afscgap.typesdef import REQUESTOR


def build_haul_from_avro(target: dict) -> afscgap.flat_model.HaulKey:
    year = target['year']
    survey = target['survey']
    haul = target['haul']
    return afscgap.flat_model.HaulKey(year, survey, haul)


def build_requestor() -> REQUESTOR:
    return afscgap.http_util.build_requestor(stream=True)

    
def get_all_hauls(meta: afscgap.flat_model.ExecuteMetaParams) -> HAUL_KEYS:
    url = meta.get_base_url() + '/index/main.avro'
    
    requestor_maybe = meta.get_requestor()
    requestor = requestor_maybe if requestor_maybe else build_requestor()
    response = requestor(url)
    
    afscgap.http_util.check_result(response)
    
    stream = response.raw
    dict_stream = fastavro.reader(stream)  # type: ignore
    obj_stream = map(build_haul_from_avro, dict_stream)  # type: ignore
    return obj_stream


def get_hauls_for_index_filter(meta: afscgap.flat_model.ExecuteMetaParams,
    index_filter: afscgap.flat_index_util.IndexFilter) -> HAUL_KEYS:
    path = '/index/%s.avro' % index_filter.get_index_name()
    url = meta.get_base_url() + path
    
    requestor_maybe = meta.get_requestor()
    requestor = requestor_maybe if requestor_maybe else build_requestor()
    response = requestor(url)
    
    afscgap.http_util.check_result(response)
    
    stream = response.raw
    all_with_value: typing.Iterable[dict] = fastavro.reader(stream)  # type: ignore
    dict_stream_with_value = filter(lambda x: index_filter.get_matches(x['value']), all_with_value)
    dict_stream_nested = map(lambda x: x['keys'], dict_stream_with_value)
    dict_stream = itertools.chain(*dict_stream_nested)
    
    obj_stream = map(build_haul_from_avro, dict_stream)
    return obj_stream


def get_records_for_haul(meta: afscgap.flat_model.ExecuteMetaParams,
    haul: afscgap.flat_model.HaulKey) -> RECORDS:
    path = haul.get_path()
    url = meta.get_base_url() + path
    
    requestor_maybe = meta.get_requestor()
    requestor = requestor_maybe if requestor_maybe else build_requestor()
    response = requestor(url)
    
    afscgap.http_util.check_result(response)
    
    stream = response.raw
    dict_stream = fastavro.reader(stream)  # type: ignore
    obj_stream = map(lambda x: afscgap.flat_model.FlatRecord(x), dict_stream)
    return obj_stream
