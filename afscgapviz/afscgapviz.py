"""Small web service providing geohash level data for the afscgap visualization.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
"""
import os
import pathlib
import sqlite3
import typing

import flask
import geolib.geohash  # type: ignore

import model
import util


OUTPUT_COLS = [
    'year',
    'survey',
    'species',
    'commonName',
    'geohash',
    'surfaceTemperature',
    'bottomTemperature',
    'weight',
    'count',
    'areaSwept',
    'numRecordsAggregated',
    'latLow',
    'lngLow',
    'latHigh',
    'lngHigh'
]


def parse_record(target: typing.Tuple) -> model.SimplifiedRecord:
    year = int(target[0])
    survey = str(target[1])
    species = str(target[2])
    common_name = str(target[3])
    geohash = str(target[4])
    surface_temperature = float(target[5])
    bottom_temperature = float(target[6])
    weight = float(target[7])
    count = float(target[8])
    area_swept = float(target[9])
    num_records_aggregated = int(target[10])

    return model.SimplifiedRecord(
        year,
        survey,
        species,
        common_name,
        geohash,
        surface_temperature,
        bottom_temperature,
        weight,
        count,
        area_swept,
        num_records_aggregated
    )


def record_to_dict(target: model.SimplifiedRecord) -> typing.Dict:
    bounds = geolib.geohash.bounds(target.get_geohash())
    return {
        'year': target.get_year(),
        'survey': target.get_survey(),
        'species': target.get_species(),
        'commonName': target.get_common_name(),
        'geohash': target.get_geohash(),
        'surfaceTemperature': target.get_surface_temperature(),
        'bottomTemperature': target.get_bottom_temperature(),
        'weight': target.get_weight(),
        'count': target.get_count(),
        'areaSwept': target.get_area_swept(),
        'numRecordsAggregated': target.get_num_records_aggregated(),
        'latLow': bounds[0][0],
        'lngLow': bounds[0][1],
        'latHigh': bounds[1][0],
        'lngHigh': bounds[1][1],
    }


def build_app(app: flask.Flask, db_str: str, db_uri: bool) -> flask.Flask:
    """Register endpoints for the visualization application.

    Args:
        app: The application in which to register the endpoints.
        sqlite_str: Path to the sqlite database on which to make queries.
        sqlite_uri: Flag indicating if sqlite_str should be read as a URI.

    Returns:
        The same app after endpoint registration.
    """

    @app.route('/')
    def render_page():
        return 'Under construction.'

    @app.route('/geohashes.csv')
    def download_geohashes():
        survey = flask.request.args['survey']
        year = flask.request.args['year']
        
        species = flask.request.args.get('species', '')
        common_name = flask.request.args.get('commonName', '')

        if species is not None:
            species_filter = ('species', species)
        elif common_name is not None:
            species_filter = ('common_name', common_name)
        else:
            return 'Whoops! Please specify commonName or species.', 400

        base_sql = get_sql('query')
        query_sql = base_sql % (species_filter[0])

        output_io = StringIO.StringIO()
        writer = csv.DictWriter(output_io, colnames=OUTPUT_COLS)
        writer.writeheader()

        # Thanks https://stackoverflow.com/questions/19522505
        with contextlib.closing(sqlite3.connect(db_str, uri=db_uri)) as con:
            with con as cur:
                results = cur.execute(
                    query_sql,
                    (year, survey, species_filter[1])
                )

                results_obj = map(parse_record, results)
                results_dict = map(record_to_dict, results_obj)
                writer.writerows(results_dict)
        
        output = flask.make_response(output_io.getvalue())
        output.headers['Content-Disposition'] = 'attachment; filename=geo.csv'
        output.headers['Content-type'] = 'text/csv'

        return output
