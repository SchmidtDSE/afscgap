"""
Convienence functions for testing afscgap.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.txt.
"""
import json
import os
import pathlib
import unittest

# pylint: disable=C0115, C0116


def get_test_file_path(filename: str) -> str:
    parent_dir = pathlib.Path(__file__).parent.absolute()
    data_dir = os.path.join(parent_dir, 'data')
    full_path = os.path.join(data_dir, filename)
    return full_path


def load_test_data_json(filename: str) -> dict:
    full_path = get_test_file_path(filename)

    with open(full_path) as f:
        loaded_data = json.load(f)

    return loaded_data


def load_test_data_text(filename: str) -> str:
    full_path = get_test_file_path(filename)

    with open(full_path) as f:
        loaded_data = f.read()

    return loaded_data


def make_result_json(filename: str):
    new_mock = unittest.mock.MagicMock()
    new_mock.status_code = 200

    loaded_data = load_test_data_json(filename)

    new_mock.json = unittest.mock.MagicMock(
        return_value=loaded_data
    )

    return new_mock


def make_result_text(filename: str):
    new_mock = unittest.mock.MagicMock()
    new_mock.status_code = 200

    loaded_data = load_test_data_text(filename)
    new_mock.text = loaded_data

    return new_mock
