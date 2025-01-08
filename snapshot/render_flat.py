"""
Script to build joined flat Avro files.

Script to build joined flat Avro files by joining across the speices list, the hauls dataset, and
the catch dataset. Catches and species without haul matches will be excluded.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import csv
import io
import itertools
import functools
import os
import sys
import time
import typing

import boto3  # type: ignore
import coiled  # type: ignore
import fastavro

import const

USAGE_STR = 'python render_flat.py [bucket] [filenames]'
NUM_ARGS = 2


OBSERVATION_SCHEMA = {
    'doc': 'Description of an observation joined across haul, catch, species.',
    'name': 'Observation',
    'namespace': 'edu.dse.afscgap',
    'type': 'record',
    'fields': [
        {'name': 'year', 'type': ['int', 'null']},
        {'name': 'srvy', 'type': ['string', 'null']},
        {'name': 'survey', 'type': ['string', 'null']},
        {'name': 'survey_name', 'type': ['string', 'null']},
        {'name': 'survey_definition_id', 'type': ['long', 'null']},
        {'name': 'cruise', 'type': ['long', 'null']},
        {'name': 'cruisejoin', 'type': ['long', 'null']},
        {'name': 'hauljoin', 'type': ['long', 'null']},
        {'name': 'haul', 'type': ['long', 'null']},
        {'name': 'stratum', 'type': ['long', 'null']},
        {'name': 'station', 'type': ['string', 'null']},
        {'name': 'vessel_id', 'type': ['long', 'null']},
        {'name': 'vessel_name', 'type': ['string', 'null']},
        {'name': 'date_time', 'type': ['string', 'null']},
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
        {'name': 'performance', 'type': ['float', 'null']},
        {'name': 'species_code', 'type': ['long', 'null']},
        {'name': 'cpue_kgkm2', 'type': ['double', 'null']},
        {'name': 'cpue_nokm2', 'type': ['double', 'null']},
        {'name': 'count', 'type': ['long', 'null']},
        {'name': 'weight_kg', 'type': ['double', 'null']},
        {'name': 'taxon_confidence', 'type': ['string', 'null']},
        {'name': 'scientific_name', 'type': ['string', 'null']},
        {'name': 'common_name', 'type': ['string', 'null']},
        {'name': 'id_rank', 'type': ['string', 'null']},
        {'name': 'worms', 'type': ['long', 'null']},
        {'name': 'itis', 'type': ['long', 'null']},
        {'name': 'complete', 'type': ['boolean', 'null']}
    ]
}

SPECIES_DICT = typing.Dict[str, dict]


def make_zero_record(species: dict, haul_record: dict) -> dict:
    """Make a zero catch record meaning that a species was not found.

    Args:
        species: Information about the species not found.
        haul_record: Information about the haul for which no specimens were found.

    Returns:
        Complete output record indicating the given species not found for the given haul.
    """
    import copy

    haul_copy = copy.deepcopy(haul_record)
    haul_copy['species_code'] = species['species_code']
    haul_copy['cpue_kgkm2'] = 0
    haul_copy['cpue_nokm2'] = 0
    haul_copy['count'] = 0
    haul_copy['weight_kg'] = 0
    haul_copy['taxon_confidence'] = None
    haul_copy['scientific_name'] = species['scientific_name']
    haul_copy['common_name'] = species['common_name']
    haul_copy['id_rank'] = species['id_rank']
    haul_copy['worms'] = species['worms']
    haul_copy['itis'] = species['itis']
    haul_copy['complete'] = True
    return haul_copy


def make_zero_catch_records(catch_records_out_realized: typing.List[dict],
    species_by_code: SPECIES_DICT, haul_record: dict) -> typing.Iterable[dict]:
    """Generate zero catch records for species not found in catches for a haul.

    Args:
        catch_records_out_realized: All catch records for a haul.
        species_by_code: Mapping from species code to information about the species such that all
            formally tracked species are in this dictionary.
        haul_record: Base record to use in generating zero catch records.

    Returns:
        Inferred zero catch records.
    """
    species_codes_found = set(map(
        lambda x: x.get('species_code', None),
        catch_records_out_realized
    ))
    species_codes_all = set(species_by_code.keys())
    speices_codes_missing = species_codes_all - species_codes_found
    speices_missing = map(lambda x: species_by_code[x], speices_codes_missing)
    catch_records_zero = map(
        lambda x: make_zero_record(x, haul_record),
        speices_missing
    )
    return catch_records_zero


def append_species_from_species_list(target: dict, species_by_code: SPECIES_DICT) -> dict:
    """Add information about a species found within a catch.

    Args:
        target: Record describing a catch within haul.
        species_by_code: Dictionary mapping from species code found in a catch to information about
            that species.

    Returns:
        Catch record with species information added.
    """
    species_code = target['species_code']

    if species_code not in species_by_code:
        return mark_incomplete(target)
    else:
        target = mark_complete(target)

    species_record = species_by_code[species_code]
    target.update(species_record)
    return target


def make_get_avro(bucket: str, s3_client) -> typing.Callable[[str], typing.List[dict]]:
    """Build a function which gets a file from a bucket using the given S3 client.

    Args:
        bucket: The name of the bucket where files should be found.
        s3_client: The S3 client to use in getting those files.

    Returns:
        Function which takes a full path and reutrns a list of parsed dictionaries from the Avro
        file at that path.
    """

    def get_avro(full_loc: str) -> typing.List[dict]:
        """Get all records from an Avro file.

        Args:
            full_loc: The full path to the avro file to be read.

        Returns:
            All records within that Avro file parsed as dictionaries.
        """
        import time

        import const

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

    return get_avro


def append_catch_haul(catch_record: dict, haul_record: dict) -> dict:
    """Combine information between a catch record and a haul record.

    Args:
        catch_record: The catch record to combine with haul information.
        haul_record: The haul information for the given catch record.

    Returns:
        Combined catch and haul information.
    """
    catch_record.update(haul_record)
    return catch_record


def complete_record(target: dict) -> dict:
    """Fill in any missing fields with None to fit edu.dse.afscgap.Observation Avro format.

    Args:
        target: Record to finish. This record may or may not be modified in place.

    Returns:
        Record with any missing fields set to None.
    """
    keys = map(lambda x: x['name'], OBSERVATION_SCHEMA['fields'])  # type: ignore
    keys_realized = list(keys)
    values = map(lambda x: target.get(x, None), keys_realized)
    return dict(zip(keys_realized, values))


def mark_incomplete(target: dict) -> dict:
    """Mark a record as incomplete.

    Args:
        target: Record on which the complete attribute should be changed. This may or may not be
            modified in-place.

    Returns:
        Record with the complete flag updated.
    """
    target['complete'] = False
    return target


def mark_complete(target: dict) -> dict:
    """Mark a record as complete.

    Args:
        target: Record on which the complete attribute should be changed. This may or may not be
            modified in-place.

    Returns:
        Record with the complete flag updated.
    """
    target['complete'] = True
    return target


def execute_full_join(haul_record: dict,
    catch_records: typing.Optional[typing.List[dict]],
    species_by_code: SPECIES_DICT) -> typing.Iterable[dict]:
    """Combine catch information with information about the haul in which that catch happened.

    Args:
        haul_record: Information about the haul in which the catch took place.
        catch_records: The catch records to be joined with haul information.
        species_by_code: Information about all tracked species indexed by species code.

    Returns:
        Updated catch records or, if no catch records provided, a single record with haul
        information marked incomplete.
    """
    if catch_records is None:
        catch_records_out = map(mark_incomplete, [haul_record])
    else:
        catch_no_species = map(
            lambda x: append_catch_haul(x, haul_record),
            catch_records
        )
        catch_records_out = map(
            lambda x: append_species_from_species_list(x, species_by_code),
            catch_no_species
        )

    return catch_records_out


def get_path_for_catches_in_haul(haul: int) -> str:
    """Get the URL where the catches associated with a haul may be found.

    Args:
        haul: The ID of the desired haul.

    Returns:
        Path to where the catches associated with the given haul may be found if there is any data
        available.
    """
    return 'catch/%d.avro' % haul


def get_meta_path_for_haul(year: int, survey: str, haul: int) -> str:
    """Get the URL for a haul's metadata given the haul location.

    Args:
        year: The year in which the haul took place like 2025.
        survey: The survey name like "Gulf of Alaska" that the haul was part of.
        haul: The haul ID for the desired haul.

    Returns:
        String path where the Avro file with haul metadata is expected.
    """
    template_vals = (year, survey, haul)
    return 'haul/%d_%s_%d.avro' % template_vals


def get_joined_path(year: int, survey: str, haul: int) -> str:
    """Get that path at which joined data is expected to be written for a haul.

    Args:
        year: The year in which the haul occurred like 2025.
        survey: The name of the survey like "Gulf of Alaska" in which the haul took place.
        haul: The ID of the haul.

    Returns:
        STring path where the Avro file with joined haul data is expected.
    """
    template_vals = (year, survey, haul)
    return 'joined/%d_%s_%d.avro' % template_vals


def make_haul_metadata_record(path: str) -> dict:
    """Parse a path into a metadata record.

    Args:
        path: The path to be parsed as a metadata record.

    Returns:
        Dictionary describing metadata for a haul.
    """
    filename_with_path = path.split('/')[-1]
    filename = filename_with_path.split('.')[0]
    components = filename.split('_')
    return {
        'loc': path,
        'year': int(components[0]),
        'survey': components[1],
        'haul': int(components[2])
    }


def process_haul(bucket: str, year: int, survey: str, haul: int,
    species_by_code: SPECIES_DICT) -> dict:
    """Distributed task to process a single haul.

    Distributed task to process a single haul, joining across species and catch datasets for that
    haul and writing out the joined file to S3.

    Args:
        bucket: The name of the bucket where catch, haul, and species information can be found.
        year: The year of the haul to be processed.
        survey: The suvey name like "Gulf of Alaska" in which the haul to bpe processed was found.
        haul: The haul ID to be processed.
        species_by_code: Information about all species formally tracked indexed by species code.

    Returns:
        Diagnostic information about the file written.
    """

    import io
    import os
    import time

    import botocore  # type: ignore
    import boto3
    import fastavro

    import const

    access_key = os.environ['AWS_ACCESS_KEY']
    access_secret = os.environ['AWS_ACCESS_SECRET']

    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=access_secret
    )

    get_avro = make_get_avro(bucket, s3_client)

    def check_file_exists(full_loc: str) -> bool:
        """Check that a file exists in S3.

        Args:
            full_loc: The location (path) within the S3 bucket.

        Returns:
            True if the file is found and false otherwise.
        """

        def attempt_head_object() -> bool:
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
            return attempt_head_object()
        except:
            time.sleep(const.RETRY_DELAY)
            return attempt_head_object()

    def convert_to_avro(records: typing.Iterable[dict]) -> io.BytesIO:
        """Convert an iterable of dictionaries to Avro bytes.

        Args:
            records: The dictionaries to convert.

        Returns:
            Bytes with Avro payload.
        """
        records_complete = map(complete_record, records)
        target_buffer = io.BytesIO()
        fastavro.writer(target_buffer, OBSERVATION_SCHEMA, records_complete)
        target_buffer.seek(0)
        return target_buffer

    def get_haul_record(year: int, survey: str, haul: int) -> typing.Optional[dict]:
        """Get the record for a haul given the haul location.

        Args:
            year: The year in which the haul took place like 2025.
            survey: The survey name like "Gulf of Alaska" that the haul was part of.
            haul: The haul ID for the desired haul.

        Returns:
            Dictionary record describing the haul or None if the haul was not found.
        """
        haul_loc = get_meta_path_for_haul(year, survey, haul)

        if not check_file_exists(haul_loc):
            return None

        haul_records = get_avro(haul_loc)
        assert len(haul_records) == 1
        haul_record = haul_records[0]
        return haul_record

    def get_catch_records(haul: int) -> typing.Optional[typing.Iterable[dict]]:
        """Get the catch records associated with a haul.

        Args:
            haul: The ID of the haul for which catch records should be returned.

        Returns:
            All catch records associated with a haul. Either None or empty list if no data could be
            found.
        """
        catch_loc = get_path_for_catches_in_haul(haul)
        if check_file_exists(catch_loc):
            return get_avro(catch_loc)
        else:
            return None

    haul_record = get_haul_record(year, survey, haul)
    catch_records_maybe = get_catch_records(haul)

    if haul_record is None or catch_records_maybe is None:
        return {
            'complete': 0,
            'incomplete': 0,
            'zero': 0,
            'loc': None
        }

    catch_records = list(catch_records_maybe)
    catch_records_out = execute_full_join(haul_record, catch_records, species_by_code)
    catch_records_out_realized = list(catch_records_out)
    catch_records_zero = make_zero_catch_records(
        catch_records_out_realized,
        species_by_code,
        haul_record
    )

    # Combine regular records with zero catch inferred records
    catch_records_all = itertools.chain(
        catch_records_out_realized,
        catch_records_zero
    )

    # Upload to S3
    catch_with_species_avro = convert_to_avro(catch_records_all)
    output_loc = get_joined_path(year, survey, haul)

    try:
        s3_client.upload_fileobj(catch_with_species_avro, bucket, output_loc)
    except:
        time.sleep(const.RETRY_DELAY)
        s3_client.upload_fileobj(catch_with_species_avro, bucket, output_loc)

    # Write out diagnostic information
    outputs_dicts = map(
        lambda x: {
            'complete': 1 if x['complete'] else 0,
            'incomplete': 0 if x['complete'] else 1,
            'zero': 1 if x.get('count', 0) == 0 else 0
        },
        catch_records_out_realized
    )
    output_dict: typing.Dict[str, int] = functools.reduce(
        lambda a, b: {
            'complete': a['complete'] + b['complete'],
            'incomplete': a['incomplete'] + b['incomplete'],
            'zero': a['zero'] + b['zero']
        },
        outputs_dicts
    )

    output_dict_with_loc: typing.Dict[str, typing.Union[str, int]] = output_dict  # type: ignore
    output_dict_with_loc['loc'] = output_loc
    return output_dict_with_loc


def get_hauls_meta(bucket: str) -> typing.Iterable[dict]:
    """Get metadata for all available hauls.

    Args:
        bucket: The bucket where hauls inforamtion can be found.

    Returns:
        Iterable over hauls metadata required to find that haul within S3.
    """
    access_key = os.environ['AWS_ACCESS_KEY']
    access_secret = os.environ['AWS_ACCESS_SECRET']

    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=access_secret
    )

    def attempt_pagination() -> typing.Iterable[dict]:
        paginator = s3_client.get_paginator('list_objects_v2')
        iterator = paginator.paginate(Bucket=bucket, Prefix='haul/')
        pages = filter(lambda x: 'Contents' in x, iterator)
        contents = map(lambda x: x['Contents'], pages)
        contents_flat = itertools.chain(*contents)
        keys = map(lambda x: x['Key'], contents_flat)
        future_results = map(make_haul_metadata_record, keys)
        return list(future_results)

    try:
        return attempt_pagination()
    except:
        time.sleep(const.RETRY_DELAY)
        return attempt_pagination()


def get_all_species(bucket: str) -> SPECIES_DICT:
    """Get information about all species formally tracked.

    Args:
        bucket: The S3 bucket name where species information can be found.

    Returns:
        Dictionary mapping from species code to information about that species.
    """
    access_key = os.environ['AWS_ACCESS_KEY']
    access_secret = os.environ['AWS_ACCESS_SECRET']

    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=access_secret
    )

    get_avro = make_get_avro(bucket, s3_client)

    def attempt_pagination() -> SPECIES_DICT:
        paginator = s3_client.get_paginator('list_objects_v2')
        iterator = paginator.paginate(Bucket=bucket, Prefix='species/')
        pages = filter(lambda x: 'Contents' in x, iterator)
        contents = map(lambda x: x['Contents'], pages)
        contents_flat = itertools.chain(*contents)
        keys = map(lambda x: x['Key'], contents_flat)
        records_nest = map(get_avro, keys)
        records_flat = itertools.chain(*records_nest)
        records_tuples = map(lambda x: (x['species_code'], x), records_flat)
        return dict(records_tuples)

    try:
        return attempt_pagination()
    except:
        time.sleep(const.RETRY_DELAY)
        return attempt_pagination()


def main():
    """Entry point for the join script."""
    if len(sys.argv) != NUM_ARGS + 1:
        print(USAGE_STR)
        sys.exit(1)

    bucket = sys.argv[1]
    file_paths_loc = sys.argv[2]
    hauls_meta = get_hauls_meta(bucket)

    cluster = coiled.Cluster(
        name='DseProcessAfscgap',
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

    hauls_meta_realized = list(hauls_meta)
    species_by_code = get_all_species(bucket)

    written_paths_future = client.map(
        lambda x: process_haul(
            bucket,
            x['year'],
            x['survey'],
            x['haul'],
            species_by_code
        ),
        hauls_meta_realized
    )
    written_paths = map(lambda x: x.result(), written_paths_future)

    with open(file_paths_loc, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'loc',
            'complete',
            'incomplete',
            'zero'
        ])
        writer.writeheader()
        writer.writerows(written_paths)

    cluster.close(force_shutdown=True)


if __name__ == '__main__':
    main()
