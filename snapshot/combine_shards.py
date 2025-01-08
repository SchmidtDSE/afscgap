"""
Script to combine sharded indicies into a single index usable by the pyafscgap library.

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
import fastavro

import const
import norm_util

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

NUM_ARGS = 2
USAGE_STR = 'python combine_shards.py [bucket] [key]'


def normalize_record(key: str, target: dict) -> dict:
    """Normalize a record value.

    Normalize a record value so that it can be used to generate bins of haul keys, rounding or
    truncating in an expected way.

    Args:
        key: The property key for which a value should be normalized.
        target: The record whose value should be updated.

    Returns:
        The record after its value attribute has been normalized if required or target unmodified
        if no changes made.
    """
    value = target['value']
    normalized = norm_util.normalize_value(key, value)
    target['value'] = normalized
    return target


def main():
    """Entry point for the shard combination script."""
    if len(sys.argv) != NUM_ARGS + 1:
        print(USAGE_STR)
        sys.exit(1)

    bucket = sys.argv[1]
    key = sys.argv[2]

    filename = key + '.txt'
    loc = os.path.join('index_shards', filename)
    with open(loc) as f:
        batches = [int(x.strip()) for x in f]

    access_key = os.environ['AWS_ACCESS_KEY']
    access_secret = os.environ['AWS_ACCESS_SECRET']

    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=access_secret
    )

    def get_avro(full_loc: str) -> typing.Iterable[dict]:
        """Get the contents of an Avro file as parsed dictionaries.

        Args:
            full_loc: The location where the avro file can be found within the S3 bucket.

        Returns:
            List of parsed Avro records with each element being one parsed Avro record.
        """

        def make_attempt_download() -> io.BytesIO:
            target_buffer = io.BytesIO()
            s3_client.download_fileobj(bucket, full_loc, target_buffer)
            return target_buffer

        try:
            target_buffer = make_attempt_download()
        except:
            time.sleep(const.RETRY_DELAY)
            target_buffer = make_attempt_download()

        target_buffer.seek(0)
        return list(fastavro.reader(target_buffer))  # type: ignore

    batch_locs = map(lambda x: 'index_sharded/%s_%d.avro' % (key, x), batches)
    shards = map(get_avro, batch_locs)
    combined = itertools.chain(*shards)
    normalized = map(lambda x: normalize_record(key, x), combined)

    write_buffer = io.BytesIO()
    fastavro.writer(
        write_buffer,
        INDEX_SCHEMA,
        normalized
    )
    write_buffer.seek(0)

    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=access_secret
    )
    output_loc = 'index/%s.avro' % key

    def make_attempt_upload():
        s3_client.upload_fileobj(write_buffer, bucket, output_loc)

    try:
        make_attempt_upload()
    except:
        time.sleep(const.RETRY_DELAY)
        make_attempt_upload()


if __name__ == '__main__':
    main()
