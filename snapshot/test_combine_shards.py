"""
Tests for scripts to combine index shards.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import unittest
import unittest.mock

import combine_shards


class NormTests(unittest.TestCase):

    def test_unchanged(self):
        normalized = combine_shards.normalize_record('test attr', {'value': 'test val'})
        self.assertEqual(normalized['value'], 'test val')

    def test_none(self):
        normalized = combine_shards.normalize_record('depth_m', {'value': None})
        self.assertEqual(normalized['value'], None)

    def test_changed(self):
        normalized = combine_shards.normalize_record('depth_m', {'value': 1.236})
        self.assertAlmostEqual(float(normalized['value']), 1.24)

    def test_rounded_float_same(self):
        normalized_1 = combine_shards.normalize_record('depth_m', {'value': 1.236})
        normalized_2 = combine_shards.normalize_record('depth_m', {'value': 1.237})
        self.assertAlmostEqual(float(normalized_1['value']), float(normalized_2['value']))

    def test_rounded_float_different(self):
        normalized_1 = combine_shards.normalize_record('depth_m', {'value': 1.234})
        normalized_2 = combine_shards.normalize_record('depth_m', {'value': 1.236})
        self.assertNotAlmostEqual(float(normalized_1['value']), float(normalized_2['value']))

    def test_rounded_datetime_same(self):
        normalized_1 = combine_shards.normalize_record(
            'date_time',
            {'value': '2025-12-31T13:25:50Z'}
        )
        normalized_2 = combine_shards.normalize_record(
            'date_time',
            {'value': '2025-12-31T14:25:50Z'}
        )
        self.assertEqual(normalized_1['value'], normalized_2['value'])

    def test_rounded_datetime_different(self):
        normalized_1 = combine_shards.normalize_record(
            'date_time',
            {'value': '2025-12-31T13:25:50Z'}
        )
        normalized_2 = combine_shards.normalize_record(
            'date_time',
            {'value': '2025-12-30T14:25:50Z'}
        )
        self.assertNotEqual(normalized_1['value'], normalized_2['value'])
