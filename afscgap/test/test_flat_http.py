"""
Tests for HTTP utility functions for interacting with Avro flat files.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import unittest
import unittest.mock

import afscgap.flat_http
import afscgap.flat_model


class FlatHttpTests(unittest.TestCase):

    def setUp(self):
        self._meta_params = afscgap.flat_model.ExecuteMetaParams(
            'base_url:',
            None,
            None,
            False,
            False,
            False,
            lambda x: print(x)
        )

        self._index_filter = unittest.mock.MagicMock()
        self._index_filter.get_index_names = unittest.mock.MagicMock(return_value=['test_index'])
        self._index_filter.get_matches = lambda x: x % 2 == 1

    def test_build_haul_from_avro(self):
        input_dict = {'year': 2024, 'survey': 'Gulf of Alaska', 'haul': 123}
        haul_key = afscgap.flat_http.build_haul_from_avro(input_dict)
        self.assertEqual(haul_key.get_year(), 2024)
        self.assertEqual(haul_key.get_survey(), 'Gulf of Alaska')
        self.assertEqual(haul_key.get_haul(), 123)

    def test_build_requestor(self):
        requestor = afscgap.flat_http.build_requestor()
        self.assertIsNotNone(requestor)

    def test_get_index_url_all(self):
        urls = list(afscgap.flat_http.get_index_urls(self._meta_params))
        self.assertEqual(len(urls), 1)
        url = urls[0]
        self.assertTrue('base_url:' in url)
        self.assertTrue('.avro' in url)

    def test_get_index_url_subset(self):
        urls = list(afscgap.flat_http.get_index_urls(self._meta_params, self._index_filter))
        self.assertEqual(len(urls), 1)
        url = urls[0]
        self.assertTrue('base_url:' in url)
        self.assertTrue('test_index' in url)
        self.assertTrue('.avro' in url)

    def test_determine_matching_hauls_from_index(self):
        options = [
            {'value': 1, 'keys': ['a', 'b']},
            {'value': 2, 'keys': ['c', 'd']},
            {'value': 3, 'keys': ['e', 'f']}
        ]
        keys = afscgap.flat_http.determine_matching_hauls_from_index(options, self._index_filter)
        keys_realized = list(keys)
        self.assertEqual(len(keys_realized), 4)
        self.assertEqual(keys_realized[0], 'a')
        self.assertEqual(keys_realized[1], 'b')
        self.assertEqual(keys_realized[2], 'e')
        self.assertEqual(keys_realized[3], 'f')
        
