"""Small web service providing geohash level data for the afscgap visualization.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
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


def sort_names_by_lower(target: typing.List[str]) -> typing.List[str]:
    """Sort a set of strings ignoring case in ascending order.

    Args:
        target: The collection of strings to sort.

    Returns:
        A copy of target sorted.
    """
    return sorted(target, key=lambda x: x.lower())


def get_display_info(connection: sqlite3.Connection,
    state: typing.Optional[typing.Dict] = None) -> dict:
    """Get information required to render species selection controls.

    Args:
        connection: A DB API 2.0 compliant connection.
        state: The state (initial selection of dataset filter vaules) provided
            by the client for which supplemental information is required or None
            if the client did not provide an initial selection in which case
            a default will be provided.

    Returns:
        A state dictionary with supplemental information required for the UI.
    """
    if state is None:
        state = {'state': [
            {
                'selections': [
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
                'temperature': 'disabled'
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
                'temperature': 'disabled'
            }
        ]}

    cached_results: typing.Dict[str, model.SurveyAvailability] = {}

    def get_cached(survey: str) -> model.SurveyAvailability:
        """Get availability information for a survey.

        Get a survey value if it has already been requested or request it if it
        is not yet cached.

        Args:
            survey: The name of the survey for which availability information
                is required. Example is GOA.

        Returns:
            Information on data availability within a survey.
        """
        if survey not in cached_results:
            cached_results[survey] = survey_util.get_survey_availability(
                survey,
                connection
            )

        return cached_results[survey]

    for record in state['state']:
        availability = get_cached(record['area'])
        species = sort_names_by_lower(availability.get_species())
        common_names = sort_names_by_lower(availability.get_common_names())
        years = availability.get_years()

        record['species'] = species
        record['commonNames'] = common_names
        record['years'] = years

    return state


def get_species_select_content(display: typing.Dict, index: int) -> str:
    """Utility function to server-side render the UI for species selection.

    Utility function to server-side render the UI for species selection which
    is useful due to the number of database calls required to produce it.

    Args:
        display: Information about the display state for which the selection
            component is being rendered. See get_display_info.
        index: The index of the selection UI within the page for pre-populating
            the elements IDs.

    Returns:
        Rendered template as a string.
    """
    return flask.render_template(
        'species.html',
        display=display,
        display_index=index
    )


def build_app(app: flask.Flask, db_str: typing.Optional[str] = None,
    db_uri: typing.Optional[bool] = None,
    conn_generator_builder=None) -> flask.Flask:
    """Register endpoints for the visualization application.

    Args:
        app: The application in which to register the endpoints.
        sqlite_str: Path to the sqlite database on which to make queries.
        sqlite_uri: Flag indicating if sqlite_str should be read as a URI.
        conn_generator_builder: Function which builds a function that takes
            no arguments. It must yield a DB API 2.0 compliant connection
            into a context that is "released" when the context ends. See
            make_sqlite_connection for an example. Some clients may choose
            to close connection on "release" while others may choose to use
            a connection pool depending on the underlying data store. If not
            provided or None, defaults to make_sqlite_connection.

    Returns:
        The same app after endpoint registration.
    """
    if not db_str:
        db_str = 'geohashes.db'

    if not db_uri:
        db_uri = False

    @contextlib.contextmanager
    def make_sqlite_connection():
        """Wrap a sqlite connection with close on leaving context.

        If client code did not provide a conn_generator_builder, this default
        opens a sqlite connection that is closed on context end.

        Yeilds:
            Connection which is closed on context end.
        """
        connection = sqlite3.connect(db_str, uri=db_uri)
        try:
            yield connection
        finally:
            connection.close()

    if conn_generator_builder:
        conn_generator = conn_generator_builder()
    else:
        conn_generator = make_sqlite_connection

    @app.route('/')
    def render_page():
        """Render the visualization tool.

        Returns:
            Rendered HTML template.
        """
        state = flask.request.args.get('state', None)
        if state:
            state = json.loads(state)

        with conn_generator() as con:
            return flask.render_template(
                'viz.html',
                displays=get_display_info(con, state)['state'],
                get_species_select_content=get_species_select_content
            )

    @app.route('/speciesSelector/<area>.html')
    def render_species_selector(area: str):
        """Server-side render the speices selector UI.

        Due to the large number of database calls involved, server-side render
        the species selection component for a display.

        Args:
            area: The name of the area (like GOA for Gulf of Alaska).

        Returns:
            Pre-rendered species selection selector UI.
        """
        with conn_generator() as con:
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

        display_index = int(flask.request.args.get('index', 0))

        return get_species_select_content(display, display_index)

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
                geohash_size + 1,
                species_filter[0],
                geohash_size + 1,
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
            query_sql = base_sql % (geohash_size + 1, species_filter[0])
            query_args = (year, survey, species_filter[1])

        output_io = io.StringIO()
        writer = csv.DictWriter(output_io, fieldnames=OUTPUT_COLS)
        writer.writeheader()

        with conn_generator() as connection:
            cursor = connection.cursor()
            cursor.execute(
                query_sql,
                query_args
            )
            results = cursor.fetchall()
            cursor.close()

        results_obj = map(data_util.parse_record, results)
        results_dict = map(data_util.record_to_dict, results_obj)
        writer.writerows(results_dict)

        output = flask.make_response(output_io.getvalue())
        output.headers['Content-Disposition'] = 'attachment; filename=geo.csv'
        output.headers['Content-type'] = 'text/csv'

        return output

    @app.route('/example.py')
    def download_python_example():
        """Generate a Python example.

        Geneate a Python example for requesting data currently displayed in the
        visualization.

        Returns:
            Python code file with 1 - 2 example queries against NOAA AFSC GAP.
        """
        is_comparison = flask.request.args.get('comparison', 'n') == 'y'

        survey = flask.request.args['survey']
        year = flask.request.args['year']

        species = flask.request.args.get('species', None)
        common_name = flask.request.args.get('commonName', None)

        if is_comparison:
            other_year = flask.request.args['otherYear']
            other_species = flask.request.args.get('otherSpecies', None)
            other_common_name = flask.request.args.get('otherCommonName', None)
        else:
            other_year = None
            other_species = None
            other_common_name = None

        output = flask.make_response(flask.render_template(
            'example.py_html',
            survey=survey,
            year=year,
            species=species,
            common_name=common_name,
            is_comparison=is_comparison,
            other_year=other_year,
            other_species=other_species,
            other_common_name=other_common_name
        ))
        output.headers['Content-Disposition'] = 'attachment; filename=query.py'
        output.headers['Content-type'] = 'text/python'

        return output

    @app.route('/summarize.json')
    def summarize():
        """Provide summary statistics for a dataset.

        Summarize the minimum and maximum values in a data subset which is
        required to properly generate scales for the visualization. This is
        done server side in order to offload some computation to the database
        engine.

        Returns:
            JSON encoded document with min and max temperatures and catch per
            unit area.
        """
        def try_int(target: str) -> int:
            try:
                return int(target)
            except ValueError:
                return 0

        def try_float(target: str) -> float:
            try:
                return float(target)
            except ValueError:
                return 0

        survey = flask.request.args['survey']
        year = try_int(flask.request.args['year'])
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
            other_year = try_int(flask.request.args['otherYear'])
            other_species = flask.request.args.get('otherSpecies', None)
            other_common_name = flask.request.args.get('otherCommonName', None)

            if other_species is not None:
                other_species_filter = ('species', other_species)
            elif other_common_name is not None:
                other_species_filter = ('common_name', other_common_name)
            else:
                return 'Whoops! Please specify commonName or species.', 400

            base_sql = sql_util.get_sql('summarize_compare')
            query_sql = base_sql % (
                temperature_field,
                geohash_size + 1,
                species_filter[0],
                temperature_field,
                geohash_size + 1,
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
                geohash_size + 1
            )
            query_args = (year, survey, species_filter[1])

        with conn_generator() as connection:
            cursor = connection.cursor()
            cursor.execute(
                query_sql,
                query_args
            )
            results = cursor.fetchall()
            cursor.close()

        result = results[0]

        if result[0] is None:
            min_cpue = 0
            max_cpue = 0
            min_temp = 0
            max_temp = 0
            first_cpue = 0
            second_cpue = 0
        else:
            result_float = [try_float(x) for x in result]

            (
                min_cpue,
                max_cpue,
                min_temp,
                max_temp,
                first_cpue,
                second_cpue
            ) = result_float

        ret_object = {
            'cpue': {
                'min': min_cpue,
                'max': max_cpue,
                'first': {
                    'name': species_filter[1],
                    'year': year,
                    'value': first_cpue
                }
            },
            'temperature': {'min': min_temp, 'max': max_temp}
        }

        if is_comparison:
            ret_object['cpue']['second'] = {
                'name': other_species_filter[1],
                'year': other_year,
                'value': second_cpue
            }

        return json.dumps(ret_object)

    return app


if __name__ == '__main__':
    app = flask.Flask(__name__)
    build_app(app, 'geohashes.db', True)
    app.run(debug=True)
