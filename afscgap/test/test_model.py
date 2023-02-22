"""
Unit tests for data structures as part of afscgap.

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

import afscgap.model
import afscgap.test.test_util

# pylint: disable=C0115, C0116


class ModelTests(unittest.TestCase):

    def test_get_opt_float_valid(self):
        self.assertAlmostEquals(afscgap.model.get_opt_float('1.48E+002'), 148)

    def test_get_opt_float_not_given(self):
        self.assertIsNone(afscgap.model.get_opt_float(None))

    def test_get_opt_float_na(self):
        self.assertIsNone(afscgap.model.get_opt_float('NA'))

    def test_get_opt_int_valid(self):
        self.assertEquals(afscgap.model.get_opt_int('148'), 148)

    def test_get_opt_int_not_given(self):
        self.assertIsNone(afscgap.model.get_opt_int(None))

    def test_get_opt_int_na(self):
        self.assertIsNone(afscgap.model.get_opt_int('NA'))

    def test_parse_record(self):
        result = afscgap.test.test_util.load_test_data('result_1.json')
        parsed = afscgap.model.parse_record(result['items'][0])
        self.assertEqual(parsed.get_srvy(), 'GOA')
        self.assertAlmostEquals(parsed.get_vessel_id(), 148)
        self.assertAlmostEquals(
            parsed.get_cpue_kg1000km2(),
            40.132273,
            places=5
        )

    def test_try_parse_success(self):
        result = afscgap.test.test_util.load_test_data('result_1.json')
        parsed = afscgap.model.try_parse(result['items'][0])
        self.assertTrue(parsed.meets_requirements(True))
        self.assertTrue(parsed.meets_requirements(False))
        self.assertIsNotNone(parsed.get_parsed())

    def test_try_parse_invalid(self):
        result = afscgap.test.test_util.load_test_data('result_1.json')
        parsed = afscgap.model.try_parse(result['items'][9])
        self.assertTrue(parsed.meets_requirements(True))
        self.assertFalse(parsed.meets_requirements(False))
        self.assertIsNotNone(parsed.get_parsed())

    def test_try_parse_incomplete(self):
        parsed = afscgap.model.try_parse({})
        self.assertFalse(parsed.meets_requirements(True))
        self.assertFalse(parsed.meets_requirements(False))
        self.assertIsNone(parsed.get_parsed())

    def test_to_dict(self):
        result = afscgap.test.test_util.load_test_data('result_1.json')
        parsed = afscgap.model.parse_record(result['items'][0])
        parsed_dict = parsed.to_dict()
        self.assertEqual(parsed_dict['srvy'], 'GOA')

    def test_convert_to_iso8601_success(self):
        result = afscgap.model.convert_to_iso8601('07/16/2021 11:30:22')
        self.assertEqual(result, '2021-07-16T11:30:22')

    def test_convert_to_iso8601_fail(self):
        result = afscgap.model.convert_to_iso8601('test')
        self.assertEqual(result, 'test')

    def test_iso8601_regex(self):
        self.assertIsNone(
            afscgap.model.ISO_8601_REGEX.match('07/16/2021 11:30:22')
        )
        self.assertIsNotNone(
            afscgap.model.ISO_8601_REGEX.match('2021-07-16T11:30:22')
        )
