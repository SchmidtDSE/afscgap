"""
Tests for library entry point vai the query function.

(c) 2023 The Eric and Wendy Schmidt Center for Data Science and the Environment
at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.txt.
"""
import unittest

import afscgap.test.test_util

# pylint: disable=C0115, C0116


class QueryTests(unittest.TestCase):

    def setUp(self):
        self._result_1 = afscgap.test.test_util.make_result('result_1.json')
        self._result_2 = afscgap.test.test_util.make_result('result_2.json')
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

    def test_convert_from_iso8601_match_string(self):
        result = afscgap.convert_from_iso8601('2021-07-16T11:30:22')
        self.assertEquals(result, '07/16/2021 11:30:22')

    def test_convert_from_iso8601_match_string_with_tz(self):
        result = afscgap.convert_from_iso8601('2021-07-16T11:30:22Z')
        self.assertEquals(result, '07/16/2021 11:30:22')

    def test_convert_from_iso8601_match_dict(self):
        test_dict = {
            'a': '2021-07-16T11:30:22',
            'b': 'test2',
            'c': 3
        }
        result = afscgap.convert_from_iso8601(test_dict)
        self.assertEquals(result['a'], '07/16/2021 11:30:22')
        self.assertEquals(result['b'], 'test2')
        self.assertEquals(result['c'], 3)

    def test_convert_from_iso8601_match_none(self):
        result = afscgap.convert_from_iso8601(3)
        self.assertEquals(result, 3)
