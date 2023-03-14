import sqlite3
import typing

import model
import sql_util


def get_list(survey: str, filename: str,
    connection: sqlite3.Connection) -> typing.List[str]:
    sql = sql_util.get_sql(filename)

    cursor = connection.cursor()
    cursor.execute(sql, (survey,))
    results_iter = cursor.fetchall()
    results = [str(x[0]) for x in results_iter]
    cursor.close()

    return results


def get_survey_availability(survey: str,
    connection: sqlite3.Connection) -> model.SurveyAvailability:
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
