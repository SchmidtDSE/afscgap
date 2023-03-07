"""
Tests for data structures used inside the visualizations for py afscgap.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.txt.
"""
import unittest

import model


class ModelTests(unittest.TestCase):

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

        self._test_record_3 = model.SimplifiedRecord(
            2022,
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

        self._combine_result = self._test_record_1.combine(self._test_record_2)

    def test_get_key(self):
        self.assertEquals(
            self._test_record_1.get_key(),
            self._test_record_2.get_key()
        )

        self.assertNotEquals(
            self._test_record_1.get_key(),
            self._test_record_3.get_key()
        )

    def test_combine_record_meta(self):
        self.assertEqual(
            self._combine_result.get_key(),
            self._test_record_1.get_key()
        )

        self.assertEquals(self._combine_result.get_year(), 2023)
        self.assertEquals(self._combine_result.get_survey(), 'GOA')
        self.assertEquals(self._combine_result.get_species(), 'scientific')
        self.assertEquals(self._combine_result.get_common_name(), 'common')
        self.assertEquals(self._combine_result.get_geohash(), 'abc')
        
    def test_combine_record_calculations(self):
        self.assertAlmostEquals(
            self._combine_result.get_surface_temperature(),
            (1.2 * 8 + 1.3 * 9) / (8 + 9)
        )
        self.assertAlmostEquals(
            self._combine_result.get_bottom_temperature(),
            (3.4 * 8 + 3.5 * 9) / (8 + 9)
        )
        self.assertAlmostEquals(
            self._combine_result.get_weight(),
            5 + 6
        )
        self.assertAlmostEquals(
            self._combine_result.get_count(),
            6 + 7
        )
        self.assertAlmostEquals(
            self._combine_result.get_area_swept(),
            7 + 8
        )
        self.assertAlmostEquals(
            self._combine_result.get_num_records_aggregated(),
            8 + 9
        )
