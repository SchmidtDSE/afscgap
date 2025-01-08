"""
Tests for generating sharded indicies.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import unittest
import unittest.mock

import const
import generate_indicies


class BuildIndexRecordTests(unittest.TestCase):

    def setUp(self):
        self._record = {'testkey': 'testvalue'}

    def test_build_index_record_value(self):
        record = generate_indicies.build_index_record(self._record, 'testkey', 2025, 'GOA', 123)
        self.assertEqual(record['value'], 'testvalue')

    def test_build_index_record_same(self):
        record_1 = generate_indicies.build_index_record(self._record, 'testkey', 2025, 'GOA', 123)
        record_2 = generate_indicies.build_index_record(self._record, 'testkey', 2025, 'GOA', 123)
        key_1 = list(record_1['keys'])[0]
        key_2 = list(record_2['keys'])[0]
        self.assertEqual(key_1, key_2)

    def test_build_index_record_different_year(self):
        record_1 = generate_indicies.build_index_record(self._record, 'testkey', 2025, 'GOA', 123)
        record_2 = generate_indicies.build_index_record(self._record, 'testkey', 2026, 'GOA', 123)
        key_1 = list(record_1['keys'])[0]
        key_2 = list(record_2['keys'])[0]
        self.assertNotEqual(key_1, key_2)

    def test_build_index_record_different_survey(self):
        record_1 = generate_indicies.build_index_record(self._record, 'testkey', 2025, 'GOA', 123)
        record_2 = generate_indicies.build_index_record(self._record, 'testkey', 2025, 'Other', 123)
        key_1 = list(record_1['keys'])[0]
        key_2 = list(record_2['keys'])[0]
        self.assertNotEqual(key_1, key_2)

    def test_build_index_record_different_haul(self):
        record_1 = generate_indicies.build_index_record(self._record, 'testkey', 2025, 'GOA', 123)
        record_2 = generate_indicies.build_index_record(self._record, 'testkey', 2025, 'GOA', 124)
        key_1 = list(record_1['keys'])[0]
        key_2 = list(record_2['keys'])[0]
        self.assertNotEqual(key_1, key_2)


class NormTests(unittest.TestCase):

    def test_unchanged(self):
        normalized = generate_indicies.normalize_value(
            {'value': 'test val'},
            'test attr'
        )
        self.assertEqual(normalized, 'test val')

    def test_none(self):
        normalized = generate_indicies.normalize_value(
            {'value': None},
            'depth_m'
        )
        self.assertEqual(normalized, None)

    def test_changed(self):
        normalized = generate_indicies.normalize_value(
            {'value': 1.236},
            'depth_m'
        )
        self.assertEqual(normalized, '1.24')

    def test_rounded_float_same(self):
        normalized_1 = generate_indicies.normalize_value(
            {'value': 1.236},
            'depth_m'
        )
        normalized_2 = generate_indicies.normalize_value(
            {'value': 1.237},
            'depth_m'
        )
        self.assertEqual(normalized_1, normalized_2)

    def test_rounded_float_different(self):
        normalized_1 = generate_indicies.normalize_value(
            {'value': 1.234},
            'depth_m'
        )
        normalized_2 = generate_indicies.normalize_value(
            {'value': 1.236},
            'depth_m'
        )
        self.assertNotEqual(normalized_1, normalized_2)

    def test_rounded_datetime_same(self):
        normalized_1 = generate_indicies.normalize_value(
            {'value': '2025-12-31T13:25:50Z'},
            'date_time'
        )
        normalized_2 = generate_indicies.normalize_value(
            {'value': '2025-12-31T14:25:50Z'},
            'date_time'
        )
        self.assertEqual(normalized_1, normalized_2)

    def test_rounded_datetime_different(self):
        normalized_1 = generate_indicies.normalize_value(
            {'value': '2025-12-31T13:25:50Z'},
            'date_time'
        )
        normalized_2 = generate_indicies.normalize_value(
            {'value': '2025-12-30T14:25:50Z'},
            'date_time'
        )
        self.assertNotEqual(normalized_1, normalized_2)


class IsNonZeroTests(unittest.TestCase):

    def setUp(self):
        self._target = {}
        for field in const.ZEROABLE_FIELDS:
            self._target[field] = 123

    def test_is_non_zero_not_zeroable_zero(self):
        self._target['other'] = 0
        self.assertTrue(generate_indicies.is_non_zero(self._target))

    def test_is_non_zero_not_zeroable_none(self):
        self._target['other'] = None  # type: ignore
        self.assertTrue(generate_indicies.is_non_zero(self._target))

    def test_is_non_zero_zeroable_zero_partial(self):
        self._target['count'] = 0
        self.assertTrue(generate_indicies.is_non_zero(self._target))

    def test_is_non_zero_zeroable_none_partial(self):
        self._target['count'] = None  # type: ignore
        self.assertTrue(generate_indicies.is_non_zero(self._target))

    def test_is_non_zero_zeroable_zero_all(self):
        for field in const.ZEROABLE_FIELDS:
            self._target[field] = 0

        self.assertFalse(generate_indicies.is_non_zero(self._target))

    def test_is_non_zero_zeroable_none_all(self):
        for field in const.ZEROABLE_FIELDS:
            self._target[field] = None  # type: ignore

        self.assertFalse(generate_indicies.is_non_zero(self._target))


class BuildOutputRecordTests(unittest.TestCase):

    def setUp(self):
        target = {'value': 'test value', 'keys': ['2025\tGOA\t123', '2025\tGOA\t124']}
        self._output_record = generate_indicies.build_output_record(target)

    def test_build_output_record(self):
        self.assertEqual(self._output_record['value'], 'test value')

    def test_build_key_meta_check_first(self):
        key = self._output_record['keys'][0]
        self.assertEqual(key['year'], 2025)
        self.assertEqual(key['survey'], 'GOA')
        self.assertEqual(key['haul'], 123)

    def test_build_key_meta_check_hauls(self):
        key_1 = self._output_record['keys'][0]
        self.assertEqual(key_1['haul'], 123)

        key_2 = self._output_record['keys'][1]
        self.assertEqual(key_2['haul'], 124)


class CombineTests(unittest.TestCase):

    def setUp(self):
        self._base = {'value': 1, 'keys': {'a'}}
        self._compatible = {'value': 1, 'keys': {'b'}}
        self._incompatible = {'value': 2, 'keys': {'c'}}

    def test_combine_compatible(self):
        combined = generate_indicies.combine_records(self._base, self._compatible)
        self.assertEqual(combined['value'], 1)

        keys = combined['keys']
        self.assertEqual(len(keys), 2)
        self.assertTrue('a' in keys)
        self.assertTrue('b' in keys)
