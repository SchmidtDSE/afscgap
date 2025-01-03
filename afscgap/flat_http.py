"""
Interfaces for cursor objects which iterate over records from prejoined flat records.

Interfaces for cursor objects which iterate over records from prejoined flat records, either those
appearing in the underlying unjoined dataset or zero catch inferred records.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import itertools
import typing

import fastavro

import afscgap.flat_index_util
import afscgap.flat_model
import afscgap.http_util

from afscgap.flat_model import HAUL_KEYS, RECORDS
from afscgap.typesdef import REQUESTOR

MAIN_INDEX_PATH = '/index/main.avro'
OPT_FILTER = typing.Optional[afscgap.flat_index_util.IndexFilter]


def build_haul_from_avro(target: dict) -> afscgap.flat_model.HaulKey:
    """Build a haul record from a dictionary parsed from avro.

    Args:
        target: The single record parsed from binary avro to be converted to a HaulKey.

    Returns:
        Parsed HaulKey record.
    """
    year = target['year']
    survey = target['survey']
    haul = target['haul']
    return afscgap.flat_model.HaulKey(year, survey, haul)


def build_requestor() -> REQUESTOR:
    """Build a requests-compatible requestor object.

    Returns:
        Create a new requestor object which is set up for streaming and other configuration as
        required for flat file iteration.
    """
    return afscgap.http_util.build_requestor(stream=True)


def get_index_urls(meta: afscgap.flat_model.ExecuteMetaParams,
    index_filter: OPT_FILTER = None) -> typing.Iterable[str]:
    """Get the URL at which an index can be found.

    Args:
        meta: Configuration object which indicates how the all hauls index should be requested. This
            can, for example, be used to configure the server from which data are streamed.
        index_filter: Information about the filter to be applied against a precomputed index. If
            None, the URL for the all hauls index is returned. Defaults to NOne.

    Returns:
        String URL at which the index can be found.
    """
    if index_filter is None:
        return [meta.get_base_url() + MAIN_INDEX_PATH]
    else:
        paths = map(lambda x: '/index/%s.avro' % x, index_filter.get_index_names())
        return map(lambda x: meta.get_base_url() + x, paths)


def determine_matching_hauls_from_index(options: typing.Iterable[dict],
    index_filter: afscgap.flat_index_util.IndexFilter) -> typing.Iterable[dict]:
    """Determine which haul keys match an index filter.

    Args:
        options: The haul keys matching different values.
        index_filter: The index filter to apply to the available hauls.

    Returns:
        Iterable of haul keys matching the filter.
    """
    dict_stream_with_value = filter(lambda x: index_filter.get_matches(x['value']), options)
    dict_stream_nested = map(lambda x: x['keys'], dict_stream_with_value)
    dict_stream = itertools.chain(*dict_stream_nested)
    return dict_stream


def get_all_hauls(meta: afscgap.flat_model.ExecuteMetaParams) -> HAUL_KEYS:
    """Get information about all hauls currently available.

    Args:
        meta: Configuration object which indicates how the all hauls index should be requested. This
            can, for example, be used to configure the server from which data are streamed.

    Returns:
        Iterator over haul information as requested from the remote server.
    """
    urls = list(get_index_urls(meta))
    assert len(urls) == 1
    url = urls[0]

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
    """Get hauls which may match a filter using precomputed indicies.

    Get all hauls which may match a filter using pre-computed Avro haul indicies which may prevent
    the query from requiring all catch data to be downloaded.

    Args:
        meta: Configuration object which indicates how the all hauls index should be requested. This
            can, for example, be used to configure the server from which data are streamed.
        index_filter: Information about the filter to be applied against a precomputed index.

    Returns:
        Iterable over haul keys which may match the specified filter.
    """
    urls = get_index_urls(meta, index_filter)

    def get_for_url(url):
        requestor_maybe = meta.get_requestor()
        requestor = requestor_maybe if requestor_maybe else build_requestor()
        response = requestor(url)

        afscgap.http_util.check_result(response)

        stream = response.raw
        all_with_value: typing.Iterable[dict] = fastavro.reader(stream)  # type: ignore
        dict_stream = determine_matching_hauls_from_index(all_with_value, index_filter)

        obj_stream = map(build_haul_from_avro, dict_stream)
        return obj_stream

    return itertools.chain(*map(get_for_url, urls))


def get_records_for_haul(meta: afscgap.flat_model.ExecuteMetaParams,
    haul: afscgap.flat_model.HaulKey) -> RECORDS:
    """Get the joined records from the hauls provided.

    Args:
        meta: Configuration object which indicates how the all hauls index should be requested. This
            can, for example, be used to configure the server from which data are streamed.
        haul: The haul for which records should be returned.

    Returns:
        All joined records for the given haul.
    """
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
