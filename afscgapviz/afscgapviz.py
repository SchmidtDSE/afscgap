"""Small web service providing geohash level data for the afscgap visualization.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
"""
import contextlib
import csv
import io
import json
import sqlite3
import typing

import flask

import data_util
import model
import sql_util
import survey_util


NAMES_DICT = typing.List[typing.Dict[str, str]]
OUTPUT_COLS = [
    'year',
    'survey',
    'species',
    'commonName',
    'geohash',
    'surfaceTemperatureC',
    'bottomTemperatureC',
    'weightKg',
    'count',
    'areaSweptHectares',
    'numRecordsAggregated',
    'latLowDegrees',
    'lngLowDegrees',
    'latHighDegrees',
    'lngHighDegrees'
]


def sort_names_by_lower(target: typing.List[str]) -> NAMES_DICT:
    output = [{"original": x, "lower": x.lower()} for x in target]
    output.sort(key=lambda x: x["lower"])
    return [x["original"] for x in output]


def get_default_displays(connection: sqlite3.Connection) -> typing.List[dict]:
    availability = survey_util.get_survey_availability('GOA', connection)
    species = sort_names_by_lower(availability.get_species())
    common_names = sort_names_by_lower(availability.get_common_names())
    years = availability.get_years()
    return [
        {
            "selections": [
                {
                    'speciesType': 'common',
                    'scientificName': 'Gadus macrocephalus',
                    'commonName': 'Pacific cod',
                    'year': 2013
                },
                {
                    'speciesType': 'common',
                    'scientificName': 'None',
                    'commonName': 'None',
                    'year': 2013
                }
            ],
            'area': 'GOA',
            'species': species,
            'commonNames': common_names,
            'years': years,
            "temperature": "disabled"
        },
        {
            "selections": [
                {
                    'speciesType': 'common',
                    'scientificName': 'Gadus macrocephalus',
                    'commonName': 'Pacific cod',
                    'year': 2021
                },
                {
                    'speciesType': 'common',
                    'scientificName': 'None',
                    'commonName': 'None',
                    'year': 2021
                }
            ],
            'area': 'GOA',
            'species': species,
            'commonNames': common_names,
            'years': years,
            "temperature": "disabled"
        }
    ]


def get_species_select_content(display: typing.Dict) -> str:
    return flask.render_template(
        'species.html',
        display=display
    )


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
        """Render the visualization tool.

        Returns:
            Rendered HTML template.
        """
        with contextlib.closing(sqlite3.connect(db_str, uri=db_uri)) as con:
            return flask.render_template(
                'viz.html',
                displays=get_default_displays(con),
                get_species_select_content=get_species_select_content
            )

    @app.route('/speciesSelector/<area>.html')
    def render_species_selector(area: str):
        with contextlib.closing(sqlite3.connect(db_str, uri=db_uri)) as con:
            availability = survey_util.get_survey_availability(area, con)

        species = availability.get_species()
        common_names = availability.get_common_names()
        years = availability.get_years()

        if len(species) == 0 or len(common_names) == 0 or len(years) == 0:
            return 'Not found.', 404
        
        display = {
            "selections": [
                {
                    'speciesType': 'common',
                    'scientificName': flask.request.args.get("name1", "None"),
                    'commonName': flask.request.args.get("name1", "None"),
                    'year': int(flask.request.args.get("year1", "None"))
                },
                {
                    'speciesType': 'common',
                    'scientificName': flask.request.args.get("name2", "None"),
                    'commonName': flask.request.args.get("name2", "None"),
                    'year': int(flask.request.args.get("year2", "None"))
                }
            ],
            'area': area,
            'species': species,
            'commonNames': common_names,
            'years': years
        }
        
        return get_species_select_content(display)

    @app.route('/geohashes.csv')
    def download_geohashes():
        """Download presence data for a species at the geohash level.

        Download presence data for a species at the geohash level where data are
        filtered according to get URL parameters survey and year as well as
        either species (scientific name) or common name (commonName arg).

        Returns:
            CSV file with the query results.
        """
        is_comparison = flask.request.args.get('comparison', 'n') == 'y'

        survey = flask.request.args['survey']
        year = flask.request.args['year']

        species = flask.request.args.get('species', None)
        common_name = flask.request.args.get('commonName', None)
        geohash_size = int(flask.request.args.get('geohashSize', 4))

        if species is not None:
            species_filter = ('species', species)
        elif common_name is not None:
            species_filter = ('common_name', common_name)
        else:
            return 'Whoops! Please specify commonName or species.', 400

        if is_comparison:
            other_year = flask.request.args['otherYear']
            other_species = flask.request.args.get('otherSpecies', None)
            other_common_name = flask.request.args.get('otherCommonName', None)

            if species is not None:
                other_species_filter = ('species', other_species)
            elif common_name is not None:
                other_species_filter = ('common_name', other_common_name)
            else:
                return 'Whoops! Please specify commonName or species.', 400

            base_sql = sql_util.get_sql('delta')
            query_sql = base_sql % (
                geohash_size,
                species_filter[0],
                geohash_size,
                other_species_filter[0]
            )
            query_args = (
                year,
                survey,
                species_filter[1],
                other_year,
                survey,
                other_species_filter[1]
            )
        else:
            base_sql = sql_util.get_sql('query')
            query_sql = base_sql % (geohash_size, species_filter[0])
            query_args = (year, survey, species_filter[1])

        output_io = io.StringIO()
        writer = csv.DictWriter(output_io, fieldnames=OUTPUT_COLS)
        writer.writeheader()

        # Thanks https://stackoverflow.com/questions/19522505
        with contextlib.closing(sqlite3.connect(db_str, uri=db_uri)) as con:
            with con as cur:
                results = cur.execute(
                    query_sql,
                    query_args
                )

                results_obj = map(data_util.parse_record, results)
                results_dict = map(data_util.record_to_dict, results_obj)
                writer.writerows(results_dict)

        output = flask.make_response(output_io.getvalue())
        output.headers['Content-Disposition'] = 'attachment; filename=geo.csv'
        output.headers['Content-type'] = 'text/csv'

        return output

    @app.route('/summarize.json')
    def summarize_cpue():
        survey = flask.request.args['survey']
        year = int(flask.request.args['year'])
        temperature_mode = flask.request.args['temperature']

        species = flask.request.args.get('species', None)
        common_name = flask.request.args.get('commonName', None)
        geohash_size = int(flask.request.args.get('geohashSize', 4))

        if species is not None:
            species_filter = ('species', species)
        elif common_name is not None:
            species_filter = ('common_name', common_name)
        else:
            return 'Whoops! Please specify commonName or species.', 400

        if temperature_mode == 'surface':
            temperature_field = 'surface_temperature'
        else:
            temperature_field = 'bottom_temperature'

        is_comparison = flask.request.args.get('comparison', 'n') == 'y'
        if is_comparison:
            other_year = int(flask.request.args['otherYear'])
            other_species = flask.request.args.get('otherSpecies', None)
            other_common_name = flask.request.args.get('otherCommonName', None)

            if species is not None:
                other_species_filter = ('species', other_species)
            elif common_name is not None:
                other_species_filter = ('common_name', other_common_name)
            else:
                return 'Whoops! Please specify commonName or species.', 400

            base_sql = sql_util.get_sql('summarize_compare')
            query_sql = base_sql % (
                temperature_field,
                geohash_size,
                species_filter[0],
                temperature_field,
                geohash_size,
                other_species_filter[0]
            )
            query_args = (
                year,
                survey,
                species_filter[1],
                other_year,
                survey,
                other_species_filter[1]
            )
        else:
            base_sql = sql_util.get_sql('summarize')
            query_sql = base_sql % (
                temperature_field,
                species_filter[0],
                geohash_size
            )
            query_args = (year, survey, species_filter[1])

        with contextlib.closing(sqlite3.connect(db_str, uri=db_uri)) as con:
            with con as cur:
                results = list(cur.execute(
                    query_sql,
                    query_args
                ))

                result = results[0]
                result_float = [float(x) for x in result]

                (min_cpue, max_cpue, min_temp, max_temp) = result_float

        return json.dumps({
            'cpue': {'min': min_cpue, 'max': max_cpue},
            'temperature': {'min': min_temp, 'max': max_temp}
        })

    return app


if __name__ == '__main__':
    app = flask.Flask(__name__)
    build_app(app, 'geohashes.db', True)
    app.run(debug=True)
