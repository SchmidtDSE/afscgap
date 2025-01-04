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

import boto3
import fastavro
import requests
import toolz.itertoolz

MIN_ARGS = 3
MAX_ARGS = 4
USAGE_STR = 'python request_source.py [type] [bucket] [location] [year]'
DOMAIN = 'https://apps-st.fisheries.noaa.gov'
ENDPOINTS = {
    'haul': '/ods/foss/afsc_groundfish_survey_haul/',
    'catch': '/ods/foss/afsc_groundfish_survey_catch/',
    'species': '/ods/foss/afsc_groundfish_survey_species/'
}

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


def get_api_request_url(type_name: str, year: int, offset: int) -> str:
    endpoint = ENDPOINTS[type_name]

    if year:
        params = '?offset=%d&limit=10000&q={"year":%d}' % (offset, year)
    else:
        params = '?offset=%d&limit=10000' % offset

    full_url = DOMAIN + endpoint + params
    return full_url


def dump_to_s3(year: int, bucket: str, loc: str, type_name: str):
    offset = 0
    done = False

    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY'],
        aws_secret_access_key=os.environ['AWS_ACCESS_SECRET']
    )

    def convert_to_avro(records: typing.Iterable[dict]) -> io.BytesIO:
        target_buffer = io.BytesIO()
        fastavro.writer(target_buffer, SCHEMAS[type_name], records)
        target_buffer.seek(0)
        return target_buffer

    def append_in_bucket(key: str, records: typing.List[dict]):
        sample_record = records[0]

        if type_name == 'haul':
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

        try:
            target_buffer = io.BytesIO()
            s3_client.download_fileobj(bucket, full_loc, target_buffer)
            target_buffer.seek(0)
            prior_records = fastavro.reader(target_buffer)
        except s3_client.exceptions.ClientError:
            prior_records = []

        records_avro = convert_to_avro(itertools.chain(prior_records, records))
        s3_client.upload_fileobj(records_avro, bucket, full_loc)

    def write_response(parsed: dict):
        items = parsed['items']
        key_name = 'species_code' if type_name == 'species' else 'hauljoin'
        by_key = toolz.itertoolz.groupby(lambda x: x[key_name], items)
        for key_tuple in by_key.items():
            key = key_tuple[0]
            records = key_tuple[1]
            append_in_bucket(key, records)

    def execute_request(offset: int):
        full_url = get_api_request_url(type_name, year, offset)
        response = requests.get(full_url)
        return response

    while not done:
        if offset % 100000 == 0:
            print('Offset: %d' % offset)

        response = execute_request(offset)
        status_code = response.status_code

        if status_code == 200:
            parsed = response.json()
            write_response(parsed)
            offset += 10000
            done = len(parsed['items']) == 0
            if done:
                print('Ending gracefully...')
        else:
            template_vals = (offset, status_code)
            print('Offset of %d with status %d. Waiting...' % template_vals)
            time.sleep(1)


def main():
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
