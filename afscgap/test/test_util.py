"""
Convienence functions for testing afscgap.

(c) 2023 The Eric and Wendy Schmidt Center for Data Science and the Environment
at UC Berkeley.

This file is part of afscgap.

Afscgap is free software: you can redistribute it and/or modify it under the
terms of the GNU Lesser General Public License as published by the Free Software 
Foundation, either version 3 of the License, or (at your option) any later
version.

Afscgap is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along 
with Afscgap. If not, see <https://www.gnu.org/licenses/>. 
"""
import json
import os
import pathlib
import unittest

# pylint: disable=C0115, C0116


def load_test_data(filename: str) -> dict:
    parent_dir = pathlib.Path(__file__).parent.absolute()
    data_dir = os.path.join(parent_dir, 'data')
    full_path = os.path.join(data_dir, filename)

    with open(full_path) as f:
        loaded_data = json.load(f)

    return loaded_data


def make_result(filename: str):
    new_mock = unittest.mock.MagicMock()
    new_mock.status_code = 200

    loaded_data = load_test_data(filename)

    new_mock.json = unittest.mock.MagicMock(
        return_value=loaded_data
    )

    return new_mock
