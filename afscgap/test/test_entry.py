"""
Tests for library entry point vai the query function.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import csv
import unittest
import unittest.mock

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
        query = afscgap.Query(requestor=self._mock_requestor)
        query.filter_year(eq=2021)
        query.filter_srvy(eq='BSS')
        results = list(query.execute())
        self.assertEquals(len(results), 20)

    def test_query_dict(self):
        query = afscgap.Query(requestor=self._mock_requestor)
        query.filter_year(eq=2021)
        query.filter_latitude_dd(eq={'$gte': 56.99, '$lte': 57.04})
        query.filter_longitude_dd(eq={'$gte': -143.96, '$lte': -144.01})
        results = list(query.execute())
        self.assertEquals(len(results), 20)

    def test_query_keywords(self):
        query = afscgap.Query(requestor=self._mock_requestor)
        query.filter_year(eq=2021)
        query.filter_latitude_dd(min_val=56.99, max_val=57.04)
        query.filter_longitude_dd(min_val=-143.96, max_val=-144.01)
        results = list(query.execute())
        self.assertEquals(len(results), 20)

    def test_query_dict_filter_incomplete(self):
        query = afscgap.Query(requestor=self._mock_requestor)
        query.filter_year(eq=2021)
        query.filter_latitude_dd(eq={'$gte': 56.99, '$lte': 57.04})
        query.filter_longitude_dd(eq={'$gte': -143.96, '$lte': -144.01})
        query.set_filter_incomplete(True)
        results = list(query.execute())
        self.assertEquals(len(results), 19)

    def test_query_dict_invalid_filter_incomplete(self):
        query = afscgap.Query(requestor=self._mock_requestor)
        query.filter_year(eq=2021)
        query.filter_latitude_dd(eq={'$gte': 56.99, '$lte': 57.04})
        query.filter_longitude_dd(eq={'$gte': -143.96, '$lte': -144.01})
        query.set_filter_incomplete(True)
        result = query.execute()
        list(result)
        self.assertEquals(result.get_invalid().qsize(), 2)

    def test_query_dict_invalid_keep_incomplete(self):
        query = afscgap.Query(requestor=self._mock_requestor)
        query.filter_year(eq=2021)
        query.filter_latitude_dd(eq={'$gte': 56.99, '$lte': 57.04})
        query.filter_longitude_dd(eq={'$gte': -143.96, '$lte': -144.01})
        query.set_filter_incomplete(False)
        result = query.execute()
        list(result)
        self.assertEquals(result.get_invalid().qsize(), 1)

    def test_create_param_eq(self):
        query = afscgap.Query(requestor=self._mock_requestor)
        self.assertEqual(query._create_param(2021), 2021)

    def test_create_param_lt(self):
        query = afscgap.Query(requestor=self._mock_requestor)
        self.assertEqual(query._create_param(min_val=2021), [2021, None])

    def test_create_param_gt(self):
        query = afscgap.Query(requestor=self._mock_requestor)
        self.assertEqual(query._create_param(max_val=2021), [None, 2021])

    def test_create_param_between(self):
        query = afscgap.Query(requestor=self._mock_requestor)
        self.assertEqual(
            query._create_param(min_val=2020, max_val=2021),
            [2020, 2021]
        )


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

        query = afscgap.Query(requestor=mock_requestor)
        query.filter_year(eq=2021)
        query.set_presence_only(True)
        result = query.execute()

        results = list(result)
        self.assertEquals(len(results), 2)

    def test_query_primitive(self):
        warn_function = unittest.mock.MagicMock()

        query = afscgap.Query(requestor=self._mock_requestor)
        query.filter_year(eq=2021)
        query.set_presence_only(False)
        query.set_warn_function(warn_function)
        result = query.execute()

        results = list(result)
        self.assertEquals(len(results), 4)

    def test_query_primitive_warning(self):
        warn_function = unittest.mock.MagicMock()

        query = afscgap.Query(requestor=self._mock_requestor)
        query.filter_year(eq=2021)
        query.set_presence_only(False)
        query.set_warn_function(warn_function)
        result = query.execute()

        warn_function.assert_called()

    def test_query_primitive_suppress(self):
        warn_function = unittest.mock.MagicMock()
        
        query = afscgap.Query(requestor=self._mock_requestor)
        query.filter_year(eq=2021)
        query.set_presence_only(False)
        query.set_warn_function(warn_function)
        query.set_suppress_large_warning(True)
        result = query.execute()

        warn_function.assert_not_called()

    def test_prefetch(self):
        hauls_path = afscgap.test.test_tools.get_test_file_path('hauls.csv')
        with open(hauls_path) as f:
            rows = csv.DictReader(f)
            hauls = [afscgap.inference.parse_haul(row) for row in rows]

        warn_function = unittest.mock.MagicMock()

        query = afscgap.Query(requestor=self._mock_requestor)
        query.filter_year(eq=2021)
        query.set_presence_only(False)
        query.set_warn_function(warn_function)
        query.set_suppress_large_warning(True)
        query.set_hauls_prefetch(hauls)
        result = query.execute()

        self._mock_requestor.assert_not_called()
