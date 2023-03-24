"""
Tests for library entry point vai the query function.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import csv
import unittest

import afscgap.test.test_tools

# pylint: disable=C0115, C0116


class EntryPointNoInferenceTests(unittest.TestCase):

    def setUp(self):
        self._result_1 = afscgap.test.test_tools.make_result_json(
            'result_1.json'
        )
        self._result_2 = afscgap.test.test_tools.make_result_json(
            'result_2.json'
        )
        self._mock_requestor = unittest.mock.MagicMock(
            side_effect=[self._result_1, self._result_2]
        )

    def test_query_primitive(self):
        result = afscgap.query(
            year=2021,
            srvy='BSS',
            requestor=self._mock_requestor
        )
        results = list(result)
        self.assertEquals(len(results), 20)

    def test_query_dict(self):
        result = afscgap.query(
            year=2021,
            latitude_dd={'$gte': 56.99, '$lte': 57.04},
            longitude_dd={'$gte': -143.96, '$lte': -144.01},
            requestor=self._mock_requestor
        )
        results = list(result)
        self.assertEquals(len(results), 20)

    def test_query_dict_filter_incomplete(self):
        result = afscgap.query(
            year=2021,
            latitude_dd={'$gte': 56.99, '$lte': 57.04},
            longitude_dd={'$gte': -143.96, '$lte': -144.01},
            requestor=self._mock_requestor,
            filter_incomplete=True
        )
        results = list(result)
        self.assertEquals(len(results), 19)

    def test_query_dict_invalid_filter_incomplete(self):
        result = afscgap.query(
            year=2021,
            latitude_dd={'$gte': 56.99, '$lte': 57.04},
            longitude_dd={'$gte': -143.96, '$lte': -144.01},
            requestor=self._mock_requestor,
            filter_incomplete=True
        )
        list(result)
        self.assertEquals(result.get_invalid().qsize(), 2)

    def test_query_dict_invalid_keep_incomplete(self):
        result = afscgap.query(
            year=2021,
            latitude_dd={'$gte': 56.99, '$lte': 57.04},
            longitude_dd={'$gte': -143.96, '$lte': -144.01},
            requestor=self._mock_requestor,
            filter_incomplete=False
        )
        list(result)
        self.assertEquals(result.get_invalid().qsize(), 1)


class EntryPointInferenceTests(unittest.TestCase):

    def setUp(self):
        self._api_result = afscgap.test.test_tools.make_result_json(
            'limited.json'
        )
        self._hauls_result = afscgap.test.test_tools.make_result_text(
            'hauls.csv'
        )
        self._mock_requestor = unittest.mock.MagicMock(
            side_effect=[self._hauls_result, self._api_result]
        )

    def test_query_keep_presence_only(self):
        mock_requestor = unittest.mock.MagicMock(
            side_effect=[self._api_result]
        )

        result = afscgap.query(
            year=2021,
            requestor=mock_requestor,
            presence_only=True
        )
        results = list(result)
        self.assertEquals(len(results), 2)

    def test_query_primitive(self):
        warn_function = unittest.mock.MagicMock()

        result = afscgap.query(
            year=2021,
            requestor=self._mock_requestor,
            presence_only=False,
            warn_function=warn_function
        )
        results = list(result)
        self.assertEquals(len(results), 4)

    def test_query_primitive_warning(self):
        warn_function = unittest.mock.MagicMock()
        result = afscgap.query(
            year=2021,
            requestor=self._mock_requestor,
            presence_only=False,
            warn_function=warn_function
        )
        warn_function.assert_called()

    def test_query_primitive_suppress(self):
        warn_function = unittest.mock.MagicMock()
        result = afscgap.query(
            year=2021,
            requestor=self._mock_requestor,
            presence_only=False,
            suppress_large_warning=True,
            warn_function=warn_function
        )
        warn_function.assert_not_called()

    def test_prefetch(self):
        hauls_path = afscgap.test.test_tools.get_test_file_path('hauls.csv')
        with open(hauls_path) as f:
            rows = csv.DictReader(f)
            hauls = [afscgap.inference.parse_haul(row) for row in rows]

        warn_function = unittest.mock.MagicMock()
        result = afscgap.query(
            year=2021,
            requestor=self._mock_requestor,
            presence_only=False,
            suppress_large_warning=True,
            warn_function=warn_function,
            hauls_prefetch=hauls
        )
        self._mock_requestor.assert_not_called()
