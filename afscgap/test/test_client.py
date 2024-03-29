"""
Unit tests for the logic that interacts with the API and makes HTTP requests.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import json
import unittest
import unittest.mock

import afscgap.client
import afscgap.test.test_tools

# pylint: disable=C0115, C0116


class ClientTests(unittest.TestCase):

    def setUp(self):
        self._result_1 = afscgap.test.test_tools.make_result_json(
            'result_1.json'
        )
        self._result_2 = afscgap.test.test_tools.make_result_json(
            'result_2.json'
        )
        self._mock_requsetor = unittest.mock.MagicMock(
            side_effect=[self._result_1, self._result_2]
        )
        self._cursor = afscgap.client.ApiServiceCursor(
            'BASE_URL',
            requestor=self._mock_requsetor
        )
        self._cursor_filter_incomplete = afscgap.client.ApiServiceCursor(
            'BASE_URL',
            requestor=self._mock_requsetor,
            filter_incomplete=True
        )
        self._cursor_override = afscgap.client.ApiServiceCursor(
            'BASE_URL',
            limit=12,
            start_offset=34,
            requestor=self._mock_requsetor
        )

    def test_get_query_url(self):
        result = afscgap.client.get_query_url({
            'param1': None,
            'param2': 2,
            'param3': 'three'
        })
        self.assertTrue('noaa.gov' in result)

        components = result.split('?q=')
        self.assertEqual(len(components), 2)

        query = json.loads(components[1])
        self.assertFalse('param1' in query)
        self.assertEqual(query['param2'], 2)
        self.assertEqual(query['param3'], 'three')

    def test_meta(self):
        self.assertEqual(self._cursor.get_base_url(), 'BASE_URL')
        self.assertIsNone(self._cursor.get_limit())
        self.assertIsNone(self._cursor.get_start_offset())
        self.assertEqual(self._cursor_override.get_limit(), 12)
        self.assertEqual(self._cursor_override.get_start_offset(), 34)

    def test_get_page_url_default(self):
        self.assertEqual(self._cursor.get_page_url(), 'BASE_URL')
        self.assertEqual(
            self._cursor_override.get_page_url(),
            'BASE_URL&offset=34&limit=12'
        )

    def test_get_page_url_override(self):
        self.assertEqual(
            self._cursor.get_page_url(limit=56, offset=78),
            'BASE_URL&offset=78&limit=56'
        )

    def test_get_page(self):
        result = self._cursor.get_page()
        self.assertEqual(len(result), 10)
        self.assertEqual(result[0].get_srvy(), 'GOA')

    def test_get_page_invalid(self):
        self._cursor.get_page()
        
        with self.assertRaises(RuntimeError):
            self._cursor.get_page()

    def test_get_page_invalid_ignore(self):
        self._cursor.get_page(ignore_invalid=True)
        result = self._cursor.get_page(ignore_invalid=True)
        self.assertEqual(len(result), 10)

    def test_find_next_url_present(self):
        loaded_data = afscgap.test.test_tools.load_test_data_json(
            'result_1.json'
        )
        next_url = self._cursor._find_next_url(loaded_data)
        self.assertEqual(
            next_url,
            'https://apps-st.fisheries.noaa.gov/ods/foss/afsc_groundfish_survey/?q=%7B%22year%22:2021%2C%22latitude_dd%22:%7B%22%24gt%22:56.99%2C%22%24lt%22:+57.04%7D%2C%22longitude_dd%22:%7B%22%24gt%22:-143.96%2C%22%24lt%22:-144.01%7D%7D&offset=10&limit=10'
        )

    def test_find_next_url_not_present(self):
        loaded_data = afscgap.test.test_tools.load_test_data_json(
            'result_2.json'
        )
        next_url = self._cursor._find_next_url(loaded_data)
        self.assertIsNone(next_url)

    def test_iterate(self):
        result = list(self._cursor)
        self.assertEqual(len(result), 20)
        self.assertEqual(result[0].get_srvy(), 'GOA')

    def test_iterate_incomplete(self):
        result = list(self._cursor_filter_incomplete)
        self.assertEqual(len(result), 19)
        self.assertEqual(result[0].get_srvy(), 'GOA')

    def test_to_dicts(self):
        result = list(self._cursor.to_dicts())
        self.assertEqual(len(result), 20)
        self.assertEqual(result[0]['srvy'], 'GOA')

    def test_to_dicts_incomplete(self):
        result = list(self._cursor_filter_incomplete.to_dicts())
        self.assertEqual(len(result), 19)
        self.assertEqual(result[0]['srvy'], 'GOA')

    def test_parse_record(self):
        result = afscgap.test.test_tools.load_test_data_json('result_1.json')
        parsed = afscgap.client.parse_record(result['items'][0])
        self.assertEqual(parsed.get_srvy(), 'GOA')
        self.assertAlmostEquals(parsed.get_vessel_id(), 148)
        self.assertAlmostEquals(
            parsed.get_cpue_weight(units='kg1000/km2'),
            40.132273,
            places=5
        )

    def test_to_dict(self):
        result = afscgap.test.test_tools.load_test_data_json('result_1.json')
        parsed = afscgap.client.parse_record(result['items'][0])
        parsed_dict = parsed.to_dict()
        self.assertEqual(parsed_dict['srvy'], 'GOA')

    def test_try_parse_incomplete(self):
        parsed = afscgap.client.try_parse({})
        self.assertFalse(parsed.meets_requirements(True))
        self.assertFalse(parsed.meets_requirements(False))
        self.assertIsNone(parsed.get_parsed())

    def test_try_parse_success(self):
        result = afscgap.test.test_tools.load_test_data_json('result_1.json')
        parsed = afscgap.client.try_parse(result['items'][0])
        self.assertTrue(parsed.meets_requirements(True))
        self.assertTrue(parsed.meets_requirements(False))
        self.assertIsNotNone(parsed.get_parsed())

    def test_try_parse_invalid(self):
        result = afscgap.test.test_tools.load_test_data_json('result_1.json')
        parsed = afscgap.client.try_parse(result['items'][9])
        self.assertTrue(parsed.meets_requirements(True))
        self.assertFalse(parsed.meets_requirements(False))
        self.assertIsNotNone(parsed.get_parsed())
