"""
Script to generate sharded indicies which indicate in which hauls values can be found.

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
import dask  # type: ignore
import dask.bag  # type: ignore

import const
import norm_util

USAGE_STR = 'python render_flat.py [bucket] [keys] [terminate]'
NUM_ARGS = 3

T = typing.TypeVar('T')


def build_index_record(record: dict, key: str, year: int, survey: str, haul: int) -> dict:
    """Build an index record.

    Args:
        record: The record to index.
        key: The key (attribute name) being indexed.
        year: The year of the haul represented by the record.
        survey: The survey in which the haul took place.
        haul: The ID of the haul which produced the data to index.

    Returns:
        Dictionary describing the index record which can be combined through a reduce operation.
    """
    value = record[key]
    key_pieces = [year, survey, haul]
    key_pieces_str = map(lambda x: str(x), key_pieces)
    key_output = '\t'.join(key_pieces_str)
    return {
        'value': value,
        'keys': set([key_output])
    }


def is_non_zero(target: dict) -> bool:
    """Determine if the record is a zeroed record.

    Determine if the record is a zeroed record, potentially indicating absence according to the
    ZEROABLE_FIELDS.

    Args:
        target: The record to check.

    Returns:
        False if the record is zeroed and true otherwise.
    """

    def is_field_non_zero(field: str) -> bool:
        value = target[field]
        return (value is not None) and (value > 0)

    fields = const.ZEROABLE_FIELDS
    flags = map(is_field_non_zero, fields)
    flags_positive = filter(lambda x: x is True, flags)
    num_flags_positive = sum(map(lambda x: 1, flags_positive))
    return num_flags_positive > 0


def process_file(bucket: str, year: int, survey: str, haul: int, key: str) -> typing.List[dict]:
    """Process a single flattened joined file remotely.

    Args:
        bucket: The name of the bucket where the file can be found.
        year: The year of the haul represented in the file.
        survey: The survey in which the haul took place for the file.
        haul: The ID of the haul which produced the data to process.
        key: The key (attribute name) being indexed.

    Returns:
        Dictionary with index records from the given file.
    """
    import io
    import os
    import time

    import botocore  # type: ignore
    import boto3  # type: ignore
    import fastavro

    import const

    access_key = os.environ['AWS_ACCESS_KEY']
    access_secret = os.environ['AWS_ACCESS_SECRET']

    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=access_secret
    )

    def get_avro(full_loc: str) -> typing.Optional[typing.List[dict]]:
        """Get all the records from a file within S3.

        Args:
            full_loc: The location (path) within the S3 bucket.

        Returns:
            List of records found at the given location or None if there is an error in reading like
            the file is not found.
        """

        def attempt_download() -> io.BytesIO:
            target_buffer = io.BytesIO()
            s3_client.download_fileobj(bucket, full_loc, target_buffer)
            target_buffer.seek(0)
            return target_buffer

        try:
            target_buffer = attempt_download()
        except:
            time.sleep(const.RETRY_DELAY)
            target_buffer = attempt_download()

        return list(fastavro.reader(target_buffer))  # type: ignore

    def check_file_exists(full_loc: str) -> bool:
        """Check that a file exists in S3.

        Args:
            full_loc: The location (path) within the S3 bucket.

        Returns:
            True if the file is found and false otherwise.
        """
        def make_head_attempt() -> bool:
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

        try:
            return make_head_attempt()
        except:
            time.sleep(5)
            return make_head_attempt()

    def infer_index_record(record: dict) -> dict:
        """Build an index record.

        Args:
            record: The record to index.

        Returns:
            Dictionary describing the index record which can be combined through a reduce operation.
        """
        return build_index_record(record, key, year, survey, haul)

    template_vals = (year, survey, haul)
    flat_loc = 'joined/%d_%s_%d.avro' % template_vals

    if not check_file_exists(flat_loc):
        return []

    flat_records_all = get_avro(flat_loc)
    flat_records = filter(lambda x: x is not None, flat_records_all)  # type: ignore
    flat_records_allowed = get_flat_records_allowed(flat_records, key)

    index_records = map(infer_index_record, flat_records_allowed)

    return list(index_records)


def build_output_record(target: dict) -> dict:
    """Convert an index record to a JSON serializable dictionary which can be written to S3.

    Args:
        target: The index record to be converted for serialization.

    Returns:
        A JSON-serializable version of target.
    """

    def process_key(key_str: str) -> dict:
        """Parse a key into a dictionary which will be saved as an object in JSON.

        Args:
            key_str: The string description of the key to parse.

        Returns:
            The key string interpreted as a dictionary with separated fields.
        """
        key_pieces = key_str.split('\t')
        year = int(key_pieces[0])
        survey = key_pieces[1]
        haul = int(key_pieces[2])
        return {'year': year, 'survey': survey, 'haul': haul}

    return {
        'value': target['value'],
        'keys': [process_key(x) for x in target['keys']]
    }


def get_observations_meta(bucket: str) -> typing.Iterable[dict]:
    """Get keys for all available joined data inside a bucket.

    Args:
        bucket: The bucket at which the data are to be found.

    Returns:
        Records of all data available within the bucket inside the "joined" directory.
    """
    access_key = os.environ['AWS_ACCESS_KEY']
    access_secret = os.environ['AWS_ACCESS_SECRET']

    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=access_secret
    )

    def make_haul_metadata_record(path: str) -> dict:
        """Create a key object (dict) given a path to data for that haul.

        Args:
            path: The path within the s3 bucket.

        Returns:
            Dictionary representing a haul key for the given path.
        """
        filename_with_path = path.split('/')[-1]
        filename = filename_with_path.split('.')[0]
        components = filename.split('_')
        return {
            'path': path,
            'year': int(components[0]),
            'survey': components[1],
            'haul': int(components[2])
        }

    def make_pagination_attempt() -> typing.Iterable[dict]:
        paginator = s3_client.get_paginator('list_objects_v2')
        iterator = paginator.paginate(Bucket=bucket, Prefix='joined/')
        pages = filter(lambda x: 'Contents' in x, iterator)
        contents = map(lambda x: x['Contents'], pages)
        contents_flat = itertools.chain(*contents)
        keys = map(lambda x: x['Key'], contents_flat)
        future_results = map(make_haul_metadata_record, keys)
        return list(future_results)

    try:
        return make_pagination_attempt()
    except:
        time.sleep(const.RETRY_DELAY)
        return make_pagination_attempt()


def write_sample(key: str, bucket: str, sample: typing.Iterable[dict]) -> typing.Optional[int]:
    """Write an index shard.

    Args:
        key: The key (attribute name) being indexed.
        bucket: The bucket in which the shard should be written.
        sample: The contents of the shared to be written.

    Returns:
        Random index number given to the shard. Client code should ensure that there were no
        collisions.
    """
    import io
    import os
    import random
    import time

    import boto3
    import fastavro

    import const

    INDEX_SCHEMA = {
        'doc': 'Index from a value to an observations flat file.',
        'name': 'Index',
        'namespace': 'edu.dse.afscgap',
        'type': 'record',
        'fields': [
            {'name': 'value', 'type': ['string', 'long', 'double', 'null']},
            {'name': 'keys', 'type': {
                'type': 'array',
                'items': {
                    'name': 'Key',
                    'type': 'record',
                    'fields': [
                        {'name': 'year', 'type': 'int'},
                        {'name': 'survey', 'type': 'string'},
                        {'name': 'haul', 'type': 'long'}
                    ]
                }
            }}
        ]
    }

    sample_realized = list(sample)
    if len(sample_realized) == 0:
        return None

    batch = random.randint(0, 1000000)

    access_key = os.environ.get('AWS_ACCESS_KEY', '')
    access_secret = os.environ.get('AWS_ACCESS_SECRET', '')

    target_buffer = io.BytesIO()
    fastavro.writer(
        target_buffer,
        INDEX_SCHEMA,
        sample_realized
    )
    target_buffer.seek(0)

    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=access_secret
    )
    output_loc = 'index_sharded/%s_%d.avro' % (key, batch)

    try:
        s3_client.upload_fileobj(target_buffer, bucket, output_loc)
    except:
        time.sleep(const.RETRY_DELAY)
        s3_client.upload_fileobj(target_buffer, bucket, output_loc)

    return batch


def normalize_value(target: dict, key: str) -> typing.Optional[T]:
    """Normalize a value for indexing.

    Args:
        target: Record from which a normalized value for indexing is requested.
        key: The name of the attribute being indexed.

    Returns:
        Normalized value to use for indexing.
    """
    value = target['value']
    return norm_util.normalize_value(key, value)


def combine_records(a: dict, b: dict) -> dict:
    """Combine index records.

    Args:
        a: The first index record to combine.
        b: The second index record to combine.

    Returns:
        New index record indicating the cobination of the two records.
    """
    return {'value': a['value'], 'keys': a['keys'].union(b['keys'])}


def get_flat_records_allowed(records: typing.Iterable[dict], key: str) -> typing.Iterable[dict]:
    """Get records which are permitted to be indexed.

    Args:
        records: Candidate records.
        key: The name of the attribute being indexed.

    Returns:
        Records which can be indexed, excluding zero catch records in some circumstances.
    """
    if key in const.IGNORE_ZEROS:
        return filter(is_non_zero, records)
    else:
        return records


def main():
    """Entry point for the shareded index generation script."""
    if len(sys.argv) != NUM_ARGS + 1:
        print(USAGE_STR)
        sys.exit(1)

    bucket = sys.argv[1]
    keys = sys.argv[2].split(',')
    terminate = sys.argv[3].lower() in ['y', 'yes', 't', 'true', '1']
    hauls_meta = list(get_observations_meta(bucket))

    access_key = os.environ.get('AWS_ACCESS_KEY', '')
    access_secret = os.environ.get('AWS_ACCESS_SECRET', '')
    cluster = coiled.Cluster(
        name='DseProcessAfscgap',
        n_workers=100,
        worker_vm_types=['m7a.medium'],
        scheduler_vm_types=['m7a.medium'],
        environ={
            'AWS_ACCESS_KEY': access_key,
            'AWS_ACCESS_SECRET': access_secret
        }
    )
    client = cluster.get_client()

    def execute_for_key(key: str):
        """Execute sharded index generation for a single attribute.

        Args:
            key: The name of the attribute to be indexed.
        """
        hauls_meta_realized = dask.bag.from_sequence(hauls_meta)
        index_records_nest = hauls_meta_realized.map(
            lambda x: process_file(
                bucket,
                x['year'],
                x['survey'],
                x['haul'],
                key
            )
        )
        index_records = index_records_nest.flatten()

        def key_record(target: dict):
            """Get a normalized value for indexing.

            Args:
                target: Record from which a normalized value for indexing is requested.
                key: The name of the attribute being indexed.

            Returns:
                Normalized value to use for indexing.
            """
            return normalize_value(target, key)

        if key in const.REQUIRES_FLAT:
            index_records_output = index_records.map(build_output_record)
        else:
            index_records_grouped_nest = index_records.foldby(
                key=key_record,
                binop=combine_records
            )
            index_records_grouped = index_records_grouped_nest.map(lambda x: x[1])
            index_records_output = index_records_grouped.map(build_output_record)

        repartitioned = index_records_output.repartition(npartitions=20)
        incidies_future = repartitioned.map_partitions(
            lambda x: write_sample(key, bucket, x)
        )

        indicies_all = incidies_future.compute(scheduler=client)
        indicies = filter(lambda x: x is not None, indicies_all)
        indicies_strs = list(map(lambda x: str(x), indicies))
        assert len(indicies_strs) == len(set(indicies_strs))

        loc = os.path.join('index_shards', key + '.txt')
        with open(loc, 'w') as f:
            f.write('\n'.join(indicies_strs))

    for key in keys:
        print('Executing for %s...' % key)
        execute_for_key(key)

    if terminate:
        cluster.close(force_shutdown=True)


if __name__ == '__main__':
    main()
