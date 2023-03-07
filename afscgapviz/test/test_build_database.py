"""
Tests for a command line utility to build a geohash summary database.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.txt.
"""
import unittest

import build_database
import model


class BuildDatabaseTests(unittest.TestCase):

    def setUp(self):
        self._test_record_1 = model.SimplifiedRecord(
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
        )

        self._test_record_2 = model.SimplifiedRecord(
            2023,
            'GOA',
            'scientific',
            'common',
            'abc',
            1.3,
            3.5,
            6,
            7,
            8,
            9
        )

        a = {
            'key': self._test_record_1.get_key(),
            'record': self._test_record_1
        }

        b = {
            'key': self._test_record_2.get_key(),
            'record': self._test_record_2
        }

        self._combine_result = build_database.combine_record(a, b)
    
    def test_try_parse_int_fail(self):
        self.assertIsNone(build_database.try_parse_int('a'))

    def test_try_parse_int_success(self):
        self.assertEqual(build_database.try_parse_int('1'), 1)
    
    def test_try_parse_range_fail(self):
        self.assertIsNone(build_database.try_parse_range('abc'))

    def test_try_parse_range_success(self):
        result = build_database.try_parse_range('2020-2023')
        self.assertEqual(result[0], 2020)
        self.assertEqual(result[1], 2023)
    
    def test_combine_record_meta(self):
        self.assertEqual(
            self._combine_result['key'],
            self._test_record_1.get_key()
        )

        result_obj = self._combine_result['record']
        self.assertEquals(result_obj.get_year(), 2023)
        self.assertEquals(result_obj.get_survey(), 'GOA')
        self.assertEquals(result_obj.get_species(), 'scientific')
        self.assertEquals(result_obj.get_common_name(), 'common')
        self.assertEquals(result_obj.get_geohash(), 'abc')
        
    def test_combine_record_calculations(self):
        result_obj = self._combine_result['record']

        self.assertAlmostEquals(
            result_obj.get_surface_temperature(),
            (1.2 * 8 + 1.3 * 9) / (8 + 9)
        )
        self.assertAlmostEquals(
            result_obj.get_bottom_temperature(),
            (3.4 * 8 + 3.5 * 9) / (8 + 9)
        )
        self.assertAlmostEquals(
            result_obj.get_weight(),
            5 + 6
        )
        self.assertAlmostEquals(
            result_obj.get_count(),
            6 + 7
        )
        self.assertAlmostEquals(
            result_obj.get_area_swept(),
            7 + 8
        )
        self.assertAlmostEquals(
            result_obj.get_num_records_aggregated(),
            8 + 9
        )
    
    def test_record_to_tuple(self):
        self.assertEquals(self._test_record_1.get_year(), 2023)
