"""Convienence functions for finding availability of data within a survey.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import sqlite3
import typing

import model
import sql_util


def get_list(survey: str, filename: str,
    connection: sqlite3.Connection) -> typing.List[str]:
    """Get a list of values available within a survey.

    Args:
        survey: The survey for which available values should be queried.
        filename: The SQL file corresponding to the type of list desired like
            get_years for all years available in a survey.
        connection: The DB API 2.0 connection to use to execute the query.

    Returns:
        List of values found as strings.
    """
    sql = sql_util.get_sql(filename)

    cursor = connection.cursor()
    cursor.execute(sql, (survey,))
    results_iter = cursor.fetchall()
    results = [str(x[0]) for x in results_iter]
    cursor.close()

    return results


def get_survey_availability(survey: str,
    connection: sqlite3.Connection) -> model.SurveyAvailability:
    """Get a summary of data available for a survey within AFSC GAP.

    Args:
        survey: The name of the survey for which a summary should be generated
            like GOA for Gulf of Alaska.
        connection: The DB API 2.0 connection to use to execute the query.

    Returns:
        Summary of data available in survey.
    """
    years_str = get_list(survey, 'get_years', connection)
    species = get_list(survey, 'get_species', connection)
    common_names = get_list(survey, 'get_common_names', connection)

    years = [int(x) for x in years_str]

    return model.SurveyAvailability(
        survey,
        years,
        species,
        common_names
    )
