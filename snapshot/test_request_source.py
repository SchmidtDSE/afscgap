"""
Tests for requesting upstream source data.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import unittest
import unittest.mock

import request_source


class ApiUrlGenerationTests(unittest.TestCase):

    def test_haul(self):
        url = request_source.get_api_request_url('haul', 2025, 12, 34)
        self.assertTrue('afsc_groundfish_survey_haul' in url)
        self.assertTrue('offset=12' in url)
        self.assertTrue('limit=34' in url)
        self.assertTrue('q={"year":2025}' in url)

    def test_catch(self):
        url = request_source.get_api_request_url('catch', None, 12, 34)
        self.assertTrue('afsc_groundfish_survey_catch' in url)
        self.assertTrue('offset=12' in url)
        self.assertTrue('limit=34' in url)

    def test_species(self):
        url = request_source.get_api_request_url('species', None, 12, 34)
        self.assertTrue('afsc_groundfish_survey_species' in url)
        self.assertTrue('offset=12' in url)
        self.assertTrue('limit=34' in url)

    def test_year_provide_not_support(self):
        with self.assertRaises(RuntimeError):
            request_source.get_api_request_url('catch', 2025, 12, 34)

        with self.assertRaises(RuntimeError):
            request_source.get_api_request_url('species', 2025, 12, 34)

    def test_year_not_provided_supported(self):
        with self.assertRaises(RuntimeError):
            request_source.get_api_request_url('haul', None, 12, 34)
