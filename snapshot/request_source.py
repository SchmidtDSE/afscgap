"""
Scripts to request haul, catch, and species data from upstream APIs.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import io
import itertools
import os
import sys
import time
import typing

import boto3  # type: ignore
import botocore  # type: ignore
import fastavro
import requests
import toolz.itertoolz  # type: ignore

import const

MIN_ARGS = 3
MAX_ARGS = 4
USAGE_STR = 'python request_source.py [type] [bucket] [location] [year]'
DOMAIN = 'https://apps-st.fisheries.noaa.gov'
ENDPOINTS = {
    'haul': '/ods/foss/afsc_groundfish_survey_haul/',
    'catch': '/ods/foss/afsc_groundfish_survey_catch/',
    'species': '/ods/foss/afsc_groundfish_survey_species/'
}
YEAR_ENDPOINTS = {'haul'}

HAUL_SCHEMA = {
    'doc': 'Description of a haul',
    'name': 'Haul',
    'namespace': 'edu.dse.afscgap',
    'type': 'record',
    'fields': [
        {'name': 'year', 'type': 'int'},
        {'name': 'srvy', 'type': 'string'},
        {'name': 'survey', 'type': 'string'},
        {'name': 'survey_name', 'type': 'string'},
        {'name': 'survey_definition_id', 'type': ['long', 'null']},
        {'name': 'cruise', 'type': ['long', 'null']},
        {'name': 'cruisejoin', 'type': 'long'},
        {'name': 'hauljoin', 'type': 'long'},
        {'name': 'haul', 'type': ['long', 'null']},
        {'name': 'stratum', 'type': ['long', 'null']},
        {'name': 'station', 'type': ['string', 'null']},
        {'name': 'vessel_id', 'type': ['long', 'null']},
        {'name': 'vessel_name', 'type': ['string', 'null']},
        {'name': 'date_time', 'type': 'string'},
        {'name': 'latitude_dd_start', 'type': ['double', 'null']},
        {'name': 'longitude_dd_start', 'type': ['double', 'null']},
        {'name': 'latitude_dd_end', 'type': ['double', 'null']},
        {'name': 'longitude_dd_end', 'type': ['double', 'null']},
        {'name': 'bottom_temperature_c', 'type': ['double', 'null']},
        {'name': 'surface_temperature_c', 'type': ['double', 'null']},
        {'name': 'depth_m', 'type': ['double', 'null']},
        {'name': 'distance_fished_km', 'type': ['double', 'null']},
        {'name': 'duration_hr', 'type': ['double', 'null']},
        {'name': 'net_width_m', 'type': ['double', 'null']},
        {'name': 'net_height_m', 'type': ['double', 'null']},
        {'name': 'area_swept_km2', 'type': ['double', 'null']},
        {'name': 'performance', 'type': ['float', 'null']}
    ]
}

CATCH_SCHEMA = {
    'doc': 'Description of a catch',
    'name': 'Catch',
    'namespace': 'edu.dse.afscgap',
    'type': 'record',
    'fields': [
        {'name': 'hauljoin', 'type': 'long'},
        {'name': 'species_code', 'type': 'long'},
        {'name': 'cpue_kgkm2', 'type': ['double', 'null']},
        {'name': 'cpue_nokm2', 'type': ['double', 'null']},
        {'name': 'count', 'type': ['long', 'null']},
        {'name': 'weight_kg', 'type': ['double', 'null']},
        {'name': 'taxon_confidence', 'type': ['string', 'null']}
    ]
}

SPECIES_SCHEMA = {
    'doc': 'Description of a species',
    'name': 'Species',
    'namespace': 'edu.dse.afscgap',
    'type': 'record',
    'fields': [
        {'name': 'species_code', 'type': 'long'},
        {'name': 'scientific_name', 'type': ['string', 'null']},
        {'name': 'common_name', 'type': ['string', 'null']},
        {'name': 'id_rank', 'type': ['string', 'null']},
        {'name': 'worms', 'type': ['long', 'null']},
        {'name': 'itis', 'type': ['long', 'null']}
    ]
}

SCHEMAS = {
    'haul': HAUL_SCHEMA,
    'catch': CATCH_SCHEMA,
    'species': SPECIES_SCHEMA
}

DEFAULT_LIMIT = 5000


def get_api_request_url(type_name: str, year: typing.Optional[int], offset: int,
    limit: int = DEFAULT_LIMIT) -> str:
    """Get the URL where an API endoping can be found for a given set of records.

    Get the URL where an API endoping can be found for a given set of records, raising an exception
    if an invalid request is provided like if year is provided but not supported by the endpoint.

    Args:
        type_name: The type of record requested like "catch" for catch records.
        year: The year like 2025 for which records are requested. If None, will request without a
            year filter. Ignored by some endpoints.
        offset: The offset into this year / type combination.
        limit: The maximum number of records to return.

    Returns:
        String URL where the requested records can be found.
    """
    endpoint = ENDPOINTS[type_name]

    if year:
        if type_name not in YEAR_ENDPOINTS:
            raise RuntimeError('Provided a year filter to an endpoint that does not support it.')

        params = '?offset=%d&limit=%d&q={"year":%d}' % (offset, limit, year)
    else:
        if type_name in YEAR_ENDPOINTS:
            raise RuntimeError('Did not provide a year filter to an endpoint that supports it.')

        params = '?offset=%d&limit=%d' % (offset, limit)

    full_url = DOMAIN + endpoint + params
    return full_url


def dump_to_s3(year: typing.Optional[int], bucket: str, loc: str, type_name: str):
    """Dump a set of records to an S3 bucket for later processing / joining.

    Dump a set of records to an S3 bucket. These may be saved for later processing such as joining
    across record types. This will perform pagination until all records saved, making multiple API
    requests. Raises an exception if year is provided but not supported.

    Args:
        year: The year for which records should be dumped. This is ignored by some endpoints and
            None may be passed.
        bucket: The name of the bucket within S3 in which they should be dumped.
        loc: The location within the bucket where they should be written.
        type_name: The type of record to dump like "catch" for catch records.
    """
    offset = 0
    done = False

    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY'],
        aws_secret_access_key=os.environ['AWS_ACCESS_SECRET']
    )

    def convert_to_avro(records: typing.Iterable[dict]) -> io.BytesIO:
        """Convert a set of records to Avro.

        Args:
            records: The records to convert to Avro.

        Returns:
            The provided records as binary.
        """
        target_buffer = io.BytesIO()
        fastavro.writer(target_buffer, SCHEMAS[type_name], records)
        target_buffer.seek(0)
        return target_buffer

    def append_in_bucket(key: str, records: typing.List[dict]):
        """Append to a file within an S3 bucket, making the file if it does not exist.

        Args:
            key: The path to the file to be appended.
            records: The records to be appended as Avro.
        """
        sample_record = records[0]

        if type_name == 'haul':
            assert year is not None
            template_vals = (
                year,
                sample_record['survey'],
                sample_record['hauljoin']
            )
            full_loc = loc + '/%d_%s_%d.avro' % template_vals
        elif type_name == 'catch':
            full_loc = loc + '/%d.avro' % sample_record['hauljoin']
        elif type_name == 'species':
            full_loc = loc + '/%d.avro' % sample_record['species_code']

        def read_prior_records() -> typing.Iterable[dict]:
            """Get the records already at the target file.

            Returns:
                Iterable over records if prior contents found or an empty iterable if the file does
                not exist.
            """
            def get_prior_exists() -> bool:
                try:
                    s3_client.head_object(Bucket=bucket, Key=full_loc)
                    return True
                except botocore.exceptions.ClientError as e:
                    error_code = e.response['Error']['Code']
                    error_code_cast = int(error_code)
                    if error_code_cast == 404:
                        return False
                    else:
                        raise RuntimeError('Unexpected S3 head code: %d' % error_code)

            def get_prior_exists_with_retry() -> bool:
                try:
                    return get_prior_exists()
                except:
                    time.sleep(const.RETRY_DELAY)
                    return get_prior_exists()

            def download_prior() -> typing.Iterable[dict]:
                target_buffer = io.BytesIO()
                s3_client.download_fileobj(bucket, full_loc, target_buffer)
                target_buffer.seek(0)
                return fastavro.reader(target_buffer)  # type: ignore

            def download_prior_with_retry() -> typing.Iterable[dict]:
                try:
                    return download_prior()
                except:
                    time.sleep(const.RETRY_DELAY)
                    return download_prior()

            if get_prior_exists_with_retry():
                return download_prior_with_retry()
            else:
                return []

        prior_records = read_prior_records()
        records_avro = convert_to_avro(itertools.chain(prior_records, records))

        try:
            s3_client.upload_fileobj(records_avro, bucket, full_loc)
        except:
            time.sleep(const.RETRY_DELAY)
            s3_client.upload_fileobj(records_avro, bucket, full_loc)

    def write_response(parsed: dict):
        """Write the result of an API call to S3.

        Args:
            parsed: The record returned from the API.
        """
        items = parsed['items']
        key_name = 'species_code' if type_name == 'species' else 'hauljoin'
        by_key = toolz.itertoolz.groupby(lambda x: x[key_name], items)
        for key_tuple in by_key.items():
            key = key_tuple[0]
            records = key_tuple[1]
            append_in_bucket(key, records)

    def execute_request(offset: int):
        """Execute a single request for records given an offset into the result set.

        Args:
            offset: The number of records to skip at the start of the result set. Used for
                pagination.

        Returns:
            Unparsed response from a requests-like object.
        """
        full_url = get_api_request_url(type_name, year, offset, limit=DEFAULT_LIMIT)
        response = requests.get(full_url)
        return response

    def execute_request_with_retry(offset: int):
        original_response = None
        retry_required = False

        try:
            original_response = execute_request(offset)
            retry_required = original_response.status_code != 200
        except:
            retry_required = True

        if retry_required:
            time.sleep(const.RETRY_DELAY)
            return execute_request
        else:
            assert original_response is not None
            return original_response

    while not done:
        if offset % (DEFAULT_LIMIT * 5) == 0:
            print('Offset: %d' % offset)

        response = execute_request_with_retry(offset)
        status_code = response.status_code

        if status_code == 200:
            parsed = response.json()
            write_response(parsed)
            offset += DEFAULT_LIMIT
            done = len(parsed['items']) == 0
            if done:
                print('Ending gracefully...')
        else:
            template_vals = (offset, status_code)
            print('Offset of %d with status %d. Waiting...' % template_vals)
            time.sleep(1)


def main():
    """Entrypoint to the request source script."""
    if len(sys.argv) < MIN_ARGS + 1 or len(sys.argv) > MAX_ARGS + 1:
        print(USAGE_STR)
        sys.exit(1)

    type_name = sys.argv[1]
    bucket = sys.argv[2]
    loc = sys.argv[3]

    if len(sys.argv) > 4:
        year = int(sys.argv[4])
    else:
        year = None

    dump_to_s3(year, bucket, loc, type_name)


if __name__ == '__main__':
    main()
