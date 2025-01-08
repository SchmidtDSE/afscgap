"""
Script to ensure that Avro files written are readable and expected.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import itertools
import os
import sys
import time
import typing

import boto3  # type: ignore
import coiled  # type: ignore
import fastavro  # type: ignore

import const

NUM_ARGS = 2
USAGE_STR = 'python check_read.py [bucket] [type]'

PATHS = {
    'index': 'index/',
    'joined': 'joined/'
}

MAIN_FIELDS = ['year', 'survey', 'haul']
MAIN_PATH = 'index/main.avro'

FIELDS = {
    'index': [
        'value',
        'keys'
    ],
    'joined': [
        'year',
        'srvy',
        'survey',
        'survey_name',
        'survey_definition_id',
        'cruise',
        'cruisejoin',
        'hauljoin',
        'haul',
        'stratum',
        'station',
        'vessel_id',
        'vessel_name',
        'date_time',
        'latitude_dd_start',
        'longitude_dd_start',
        'latitude_dd_end',
        'longitude_dd_end',
        'bottom_temperature_c',
        'surface_temperature_c',
        'depth_m',
        'distance_fished_km',
        'duration_hr',
        'net_width_m',
        'net_height_m',
        'area_swept_km2',
        'performance',
        'species_code',
        'cpue_kgkm2',
        'cpue_nokm2',
        'count',
        'weight_kg',
        'taxon_confidence',
        'scientific_name',
        'common_name',
        'id_rank',
        'worms',
        'itis',
        'complete'
    ]
}


def list_files(s3_client, bucket: str, prefix: str) -> typing.Iterable[str]:
    """List all of the files with the given prefix.

    Args:
        s3_client: The client to use to execute the pagination requset.
        bucket: The name of the bucket where the files are located.
        prefix: The directory where the files are to be found.

    Returns:
        Iterable over key names.
    """
    def attempt_pagination() -> typing.Iterable[str]:
        paginator = s3_client.get_paginator('list_objects_v2')
        iterator = paginator.paginate(Bucket=bucket, Prefix='%s/' % prefix)
        pages = filter(lambda x: 'Contents' in x, iterator)
        contents = map(lambda x: x['Contents'], pages)
        contents_flat = itertools.chain(*contents)
        keys = map(lambda x: x['Key'], contents_flat)
        return list(keys)

    try:
        return attempt_pagination()
    except:
        time.sleep(const.RETRY_DELAY)
        return attempt_pagination()


def check_file(bucket: str, path: str,
    expected_fields: typing.Iterable[str]) -> typing.Optional[str]:
    """Read a file and ensure it is parsable with expected keys.

    Args:
        s3_client: The client to use to download the file.
        bucket: The bucket where the file is to be found.
        path: The path at which the file can be found.
        expected_fields: The names of the fields which are required on the downloaded file.
    """
    import io
    import os
    import time

    import boto3  # type: ignore

    access_key = os.environ['AWS_ACCESS_KEY']
    access_secret = os.environ['AWS_ACCESS_SECRET']

    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=access_secret
    )

    def attempt_download() -> io.BytesIO:
        target_buffer = io.BytesIO()
        s3_client.download_fileobj(bucket, path, target_buffer)
        target_buffer.seek(0)
        return target_buffer

    try:
        target_buffer = attempt_download()
    except:
        time.sleep(const.RETRY_DELAY)

        try:
            target_buffer = attempt_download()
        except:
            return 'Failed to get payload.'

    results: typing.Iterable[dict] = list(fastavro.reader(target_buffer))  # type: ignore
    for result in results:

        # TODO: Need to find a better way to split this
        expected_fields_actual = MAIN_FIELDS if path == MAIN_PATH else expected_fields

        for field in expected_fields_actual:
            if field not in result:
                available = ','.join(result.keys())
                return 'Could not find %s among %s.' % (field, available)

    return None


def main():
    """Entrypoint into the check read script."""
    if len(sys.argv) != NUM_ARGS + 1:
        print(USAGE_STR)
        sys.exit(1)

    bucket = sys.argv[1]
    type_name = sys.argv[2]

    if type_name not in PATHS:
        raise RuntimeError('Path not known for %s.' % type_name)

    if type_name not in FIELDS:
        raise RuntimeError('Fields not known for %s.' % type_name)

    path = PATHS[type_name]
    fields = FIELDS[type_name]

    access_key = os.environ['AWS_ACCESS_KEY']
    access_secret = os.environ['AWS_ACCESS_SECRET']

    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=access_secret
    )

    files = list_files(s3_client, bucket, path)

    if type_name != 'index':
        cluster = coiled.Cluster(
            name='DseProcessAfscgapCheck',
            n_workers=10,
            worker_vm_types=['m7a.medium'],
            scheduler_vm_types=['m7a.medium'],
            environ={
                'AWS_ACCESS_KEY': os.environ.get('AWS_ACCESS_KEY', ''),
                'AWS_ACCESS_SECRET': os.environ.get('AWS_ACCESS_SECRET', ''),
                'SOURCE_DATA_LOC': os.environ.get('SOURCE_DATA_LOC', '')
            }
        )
        cluster.adapt(minimum=10, maximum=500)
        client = cluster.get_client()

        results = client.map(
            lambda x: check_file(bucket, x, fields),
            files
        )
        results_realized = map(lambda x: x.result(), results)
    else:
        results_realized = map(lambda x: check_file(bucket, x, fields), files)

    for result in results_realized:
        if result is not None:
            raise RuntimeError(result)

    if type_name != 'index':
        cluster.close(force_shutdown=True)


if __name__ == '__main__':
    main()
