"""
Tests for data support functions.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import unittest

import data_util
import model


class DataUtilTests(unittest.TestCase):

    def test_parse_record(self):
        result = data_util.parse_record((
            2023,
            'GOA',
            'scientific',
            'common',
            'abc',
            1.2,
            3.4,
            5,
            6,
            7,
            8
        ))
        self.assertEquals(result.get_year(), 2023)

    def test_record_to_dict(self):
        record = model.SimplifiedRecord(
            2023,
            'GOA',
            'scientific',
            'common',
            '9q9p3',
            1.2,
            3.4,
            5,
            6,
            7,
            8
        )
        record_dict = data_util.record_to_dict(record)
        self.assertEquals(record_dict['year'], 2023)
