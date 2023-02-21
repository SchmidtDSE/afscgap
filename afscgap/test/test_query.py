"""
Tests for library entry point vai the query function.

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
import unittest

import afscgap.test.test_util


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
