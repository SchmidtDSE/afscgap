"""Script to build a sqlite database with geohashed presence information.

Script / command line utility which builds a sqlite database with geohashed
presence information. Note that this is not required for use of the afscgap
library and, instead, is part of the deployment pipeline for a web application
used for geohash based visualization. For continued development, this is
considered to be client code of the afscgap library.

See build_database.sh for example.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.txt.
"""
import contextlib
import os
import pathlib
import re
import sqlite3
import sys
import time
import typing

import afscgap
import afscgap.model
import geolib.geohash  # type: ignore
import toolz.itertoolz  # type: ignore

import model

INVALID_GEOHASH_STR = 'Expected geohash size to be an integer between 1 - 12.'
SLEEP_TIME = 5
SURVEYS = [
    'NBS',
    'EBS',
    'BSS',
    'GOA'
]
USAGE_BASE_NUM_ARGS = 1
USAGE_BASE_STR = 'python build_database.py '
USAGE_COMMANDS_STR = '[create_db | download]'
USAGE_CREATE_DB_COMMAND = 'create_db'
USAGE_CREATE_DB_NUM_ARGS = 1
USAGE_CREATE_DB_STR = 'create_db [sqlite file]'
USAGE_DOWNLOAD_COMMAND = 'download'
USAGE_DOWNLOAD_NUM_ARGS = 3
USAGE_DOWNLOAD_STR = 'download [year range] [sqlite file] [geohash size]'
YEAR_PATTERN = re.compile('(?P<start>\\d{4})-(?P<end>\\d{4})')
YEAR_RANGE_STR = 'Year range should be like 2000-2023.'

OPT_SIMPLIFIED_RECORD = typing.Optional[model.SimplifiedRecord]
SIMPLIFIED_RECORDS = typing.Iterable[model.SimplifiedRecord]


def try_parse_int(target: str) -> typing.Optional[int]:
    """Try parsing an integer provided by the user on the command line.

    Args:
        target: The string value provided by the user.

    Returns:
        The string provided by the user as an int or None if it could not be
        parsed.
    """
    try:
        return int(target)
    except ValueError:
        return None


def try_parse_range(target: str) -> typing.Optional[typing.Tuple[int, int]]:
    """Try parsing a string describing a range of years provided by the user.

    Args:
        target: String from the CLI which describes a range of years.

    Returns:
        Tuple with the start year and end year or None if it could not be
        parsed.
    """
    match = YEAR_PATTERN.match(target)
    if match is None:
        return None
    else:
        return (int(match.group('start')), int(match.group('end')))


def simplify_record(target: afscgap.model.Record,
    geohash_size: int) -> OPT_SIMPLIFIED_RECORD:
    """Generate a smaller record with relevant information and geohash.

    Args:
        target: The Record to be summarized.
        geohash_size: The length (number of characters) for the geohash to be
            generated for target.

    Returns:
        Record with information needed for the web application.
    """
    latitude = target.get_latitude_dd()
    longitude = target.get_longitude_dd()
    geohash = geolib.geohash.encode(latitude, longitude, geohash_size)

    surface_temperature_c_maybe = target.get_surface_temperature_c_maybe()
    if surface_temperature_c_maybe is None:
        return None

    bottom_temperature_c_maybe = target.get_bottom_temperature_c_maybe()
    if bottom_temperature_c_maybe is None:
        return None

    weight_kg_maybe = target.get_weight_kg_maybe()
    if weight_kg_maybe is None:
        return None

    count_maybe = target.get_count_maybe()
    if count_maybe is None:
        return None

    return model.SimplifiedRecord(
        round(target.get_year()),
        target.get_srvy(),
        target.get_scientific_name(),
        target.get_common_name(),
        geohash,
        surface_temperature_c_maybe,
        bottom_temperature_c_maybe,
        weight_kg_maybe,
        count_maybe,
        target.get_area_swept_ha(),
        1
    )


def combine_record(a: dict, b: dict) -> dict:
    """Combine two SimplifiedRecords with their keys.

    Combine two SimplifiedRecords with their keys when those two records come
    in the form of {"key": x.get_key(), "record": x} where x is a
    SimplifiedRecord. This is done to support toolz-based reduce by key.

    Args:
        a: The first record to be combined. Expected to be a dictionary with
            keys including "key" and "record" where the value of "key"
            identifies the metadata of "record" and the value of "record"
            is a SimplifiedRecord.
        b: The second record to be combined. Expected to be a dictionary with
            keys including "key" and "record" where the value of "key"
            identifies the metadata of "record" and the value of "record"
            is a SimplifiedRecord.

    Raises:
        AssertionError: Raised if the keys for a and b do not match.

    Returns:
        New dictionary of form {"key": key from a and b, "record": a combined
        with b}.
    """
    assert a['key'] == b['key']
    return {
        'key': a['key'],
        'record': a['record'].combine(b['record'])
    }


def get_year(survey: str, year: int, geohash_size: int) -> SIMPLIFIED_RECORDS:
    """Get simplified records from a year for a survey.

    Get simplified records from a year for a survey while using zero catch
    record inference.

    Args:
        survey: The short name for the survey of interest (like GOA).
        year: The year to be downloaded like 2023.
        geohash_size: The number of characters to include in the geohash.

    Returns:
        Iterable over SimplifiedRecords generated / downloaded.
    """
    results = afscgap.query(
        srvy=survey,
        year=year,
        presence_only=False
    )

    simplified_records_maybe = map(
        lambda x: simplify_record(x, geohash_size),
        results
    )
    simplified_records = filter(
        lambda x: x is not None,
        simplified_records_maybe
    )
    keyed_records = map(
        lambda x: {'key': x.get_key(), 'record': x},  # type: ignore
        simplified_records
    )
    records_by_geohash = toolz.reduceby(
        'key',
        combine_record,
        keyed_records
    )

    return map(lambda x: x['record'], records_by_geohash.values())


def get_sql(script_name: str) -> str:
    """Get the contents of a SQL file at afscgapviz/sql.

    Args:
        script_name: The name of the sql file like "create_table"

    Returns:
        The string contents of the file requested like the contents of
        afscgapviz/sql/create_table.sql.
    """
    parent_dir = pathlib.Path(__file__).parent.absolute()
    data_dir = os.path.join(parent_dir, 'sql')
    full_path = os.path.join(data_dir, script_name + '.sql')

    with open(full_path) as f:
        contents = f.read()

    return contents


def record_to_tuple(target: model.SimplifiedRecord) -> typing.Tuple:
    """Convert a SimplifiedRecord to a tuple for db persistence.

    Args:
        target: The record to be converted.

    Returns:
        Tuple representation that can be used with
        afscgap/viz/insert_record.sql.
    """
    return (
        target.get_year(),
        target.get_survey(),
        target.get_species(),
        target.get_common_name(),
        target.get_geohash(),
        target.get_surface_temperature(),
        target.get_bottom_temperature(),
        target.get_weight(),
        target.get_count(),
        target.get_area_swept(),
        target.get_num_records_aggregated()
    )


def download_and_persist_year(survey: str, year: int, cursor: sqlite3.Cursor,
    geohash_size: int):
    """Download the data for a year within a survey and write to sqlite db.

    Args:
        survey: The short form name of the survey for which data should be
            downloaded like "GOA".
        year: The year that should be downloaded like 2023.
        cursor: The Cursor for the sqlite database into which the database
            should be persisted.
        geohash_size: The number of characters to include in the geohash.
    """
    records = get_year(survey, year, geohash_size)

    persist_sql = get_sql('insert_record')
    records_tuples = map(record_to_tuple, records)

    cursor.executemany(persist_sql, records_tuples)


def create_db_main(args):
    """Main entry point for creating the database.

    Args:
        args: Indexable collection of string arguments provided by the CLI
            specific to this command.
    """
    if len(args) != USAGE_CREATE_DB_NUM_ARGS:
        print(USAGE_BASE_STR + USAGE_CREATE_DB_STR)
        return

    filepath = args[0]
    sql = get_sql('create_table')

    # Thanks https://stackoverflow.com/questions/19522505
    with contextlib.closing(sqlite3.connect(filepath)) as con:
        with con as cur:
            for sub_sql in sql.split(';'):
                cur.execute(sub_sql)


def download_main(args):
    """Main entry point for downloading data to the database.

    Args:
        args: Indexable collection of string arguments provided by the CLI
            specific to this command.
    """
    if len(args) != USAGE_DOWNLOAD_NUM_ARGS:
        print(USAGE_BASE_STR + USAGE_DOWNLOAD_STR)
        return

    year_range_maybe = try_parse_range(args[0])
    if year_range_maybe is None or len(year_range_maybe) != 2:
        print(YEAR_RANGE_STR)
        return

    start_year = year_range_maybe[0]
    end_year = year_range_maybe[1]

    filepath = args[1]

    try:
        geohash_size = int(args[2])
        assert geohash_size >= 1
        assert geohash_size <= 12
    except (ValueError, AssertionError):
        print(INVALID_GEOHASH_STR)
        return

    years = range(start_year, end_year + 1)

    # Thanks https://stackoverflow.com/questions/19522505
    with contextlib.closing(sqlite3.connect(filepath)) as con:
        for year in years:
            for survey in SURVEYS:

                with con as cur:
                    download_and_persist_year(survey, year, cur, geohash_size)

                print('Completed %d for %s.' % (year, survey))
                time.sleep(SLEEP_TIME)


def main():
    """Main overall entry point for this command line utility."""
    if len(sys.argv) < USAGE_BASE_NUM_ARGS + 1:
        print(USAGE_BASE_STR + USAGE_COMMANDS_STR)
        return

    command = sys.argv[1]

    commands = {
        USAGE_CREATE_DB_COMMAND: create_db_main,
        USAGE_DOWNLOAD_COMMAND: download_main
    }

    if command not in commands:
        print(USAGE_BASE_STR + USAGE_COMMANDS_STR)
        return

    commands[command](sys.argv[2:])


if __name__ == '__main__':
    main()
