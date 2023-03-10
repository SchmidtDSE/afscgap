"""Small web service providing geohash level data for the afscgap visualization.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
"""
import contextlib
import csv
import io
import sqlite3
import typing

import flask

import data_util
import model
import sql_util
import survey_util


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


def get_default_displays(connection: sqlite3.Connection) -> typing.List[dict]:
    availability = survey_util.get_survey_availability('GOA', connection)
    species = availability.get_species()
    common_names = availability.get_common_names()
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
                    'year': flask.request.args.get("year1", "None")
                },
                {
                    'speciesType': 'common',
                    'scientificName': flask.request.args.get("name2", "None"),
                    'commonName': flask.request.args.get("name2", "None"),
                    'year': flask.request.args.get("year2", "None")
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
        survey = flask.request.args['survey']
        year = flask.request.args['year']

        species = flask.request.args.get('species', None)
        common_name = flask.request.args.get('commonName', None)

        if species is not None:
            species_filter = ('species', species)
        elif common_name is not None:
            species_filter = ('common_name', common_name)
        else:
            return 'Whoops! Please specify commonName or species.', 400

        base_sql = sql_util.get_sql('query')
        query_sql = base_sql % (species_filter[0])

        output_io = io.StringIO()
        writer = csv.DictWriter(output_io, fieldnames=OUTPUT_COLS)
        writer.writeheader()

        # Thanks https://stackoverflow.com/questions/19522505
        with contextlib.closing(sqlite3.connect(db_str, uri=db_uri)) as con:
            with con as cur:
                results = cur.execute(
                    query_sql,
                    (year, survey, species_filter[1])
                )

                results_obj = map(data_util.parse_record, results)
                results_dict = map(data_util.record_to_dict, results_obj)
                writer.writerows(results_dict)

        output = flask.make_response(output_io.getvalue())
        output.headers['Content-Disposition'] = 'attachment; filename=geo.csv'
        output.headers['Content-type'] = 'text/csv'

        return output

    return app


if __name__ == '__main__':
    app = flask.Flask(__name__)
    build_app(app, 'geohashes.db', True)
    app.run(debug=True)
