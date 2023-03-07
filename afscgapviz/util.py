"""Utility functions for the afscgap web based visualization.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.txt.
"""
import os
import pathlib


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