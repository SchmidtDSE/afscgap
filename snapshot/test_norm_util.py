"""
Tests for normalization utilities.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import unittest
import unittest.mock

import norm_util


class NormUtilTests(unittest.TestCase):

    def test_normalize_record_unknown_none(self):
        normalized = norm_util.normalize_value('test attr', 'test val')
        self.assertEqual(normalized, 'test val')

    def test_normalize_record_known_none(self):
        normalized = norm_util.normalize_value('depth_m', None)
        self.assertEqual(normalized, None)

    def test_normalize_record_pass_float(self):
        normalized = self._force_float(norm_util.normalize_value('depth_m', 1.23))
        self.assertAlmostEqual(normalized, 1.23)

    def test_normalize_record_pass_datetime(self):
        normalized = norm_util.normalize_value('date_time', '2025-01-13')
        self.assertEqual(normalized, '2025-01-13')

    def test_normalize_record_round_float_same_up(self):
        normalized_1 = self._force_float(norm_util.normalize_value('depth_m', 1.237))
        normalized_2 = self._force_float(norm_util.normalize_value('depth_m', 1.236))
        self.assertAlmostEqual(normalized_1, normalized_2)

    def test_normalize_record_round_float_same_down(self):
        normalized_1 = self._force_float(norm_util.normalize_value('depth_m', 1.231))
        normalized_2 = self._force_float(norm_util.normalize_value('depth_m', 1.229))
        self.assertAlmostEqual(normalized_1, normalized_2)

    def test_normalize_record_round_float_different(self):
        normalized_1 = self._force_float(norm_util.normalize_value('depth_m', 1.236))
        normalized_2 = self._force_float(norm_util.normalize_value('depth_m', 1.234))
        self.assertNotAlmostEqual(normalized_1, normalized_2)

    def test_normalize_record_round_datetime_valid_same(self):
        normalized_1 = norm_util.normalize_value('date_time', '2025-01-13T12:25:50Z')
        normalized_2 = norm_util.normalize_value('date_time', '2025-01-13T13:25:50Z')
        self.assertEqual(normalized_1, normalized_2)

    def test_normalize_record_round_datetime_valid_different(self):
        normalized_1 = norm_util.normalize_value('date_time', '2025-01-13T12:25:50Z')
        normalized_2 = norm_util.normalize_value('date_time', '2025-01-14T13:25:50Z')
        self.assertNotEqual(normalized_1, normalized_2)

    def test_normalize_record_round_datetime_invalid_same(self):
        normalized_1 = norm_util.normalize_value('date_time', 'test')
        normalized_2 = norm_util.normalize_value('date_time', 'test')
        self.assertEqual(normalized_1, normalized_2)

    def test_normalize_record_round_datetime_invalid_different(self):
        normalized_1 = norm_util.normalize_value('date_time', 'test')
        normalized_2 = norm_util.normalize_value('date_time', 'other')
        self.assertNotEqual(normalized_1, normalized_2)

    def _force_float(self, value) -> float:
        assert value is not None
        return float(value)
