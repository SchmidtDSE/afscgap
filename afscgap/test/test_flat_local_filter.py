"""
Tests for local filtering on returned flat results.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import unittest
import unittest.mock

import afscgap.flat_local_filter
import afscgap.param


class EqualsLocalFilterTests(unittest.TestCase):

    def setUp(self):
        self._filter = afscgap.flat_local_filter.EqualsLocalFilter(
            lambda x: x.get_value(),
            1
        )

    def test_matches_true(self):
        self.assertTrue(self._filter.matches(self._make_target(1)))
    
    def test_matches_false(self):
        self.assertFalse(self._filter.matches(self._make_target(1.001)))
    
    def test_matches_none(self):
        self.assertFalse(self._filter.matches(self._make_target(None)))

    def _make_target(self, value):
        mock = unittest.mock.MagicMock()
        mock.get_value = unittest.mock.MagicMock(return_value=value)
        return mock


class RangeLocalFilterTests(unittest.TestCase):

    def setUp(self):
        self._filter = afscgap.flat_local_filter.RangeLocalFilter(
            lambda x: x.get_value(),
            2,
            4
        )

    def test_out_lower(self):
        self.assertFalse(self._filter.matches(self._make_target(1)))

    def test_at_lower(self):
        self.assertTrue(self._filter.matches(self._make_target(2)))

    def test_mid(self):
        self.assertTrue(self._filter.matches(self._make_target(3)))

    def test_at_high(self):
        self.assertTrue(self._filter.matches(self._make_target(4)))

    def test_above_high(self):
        self.assertFalse(self._filter.matches(self._make_target(5)))

    def test_none(self):
        self.assertFalse(self._filter.matches(self._make_target(None)))

    def _make_target(self, value):
        mock = unittest.mock.MagicMock()
        mock.get_value = unittest.mock.MagicMock(return_value=value)
        return mock


class LogcalAndLocalFilterTests(unittest.TestCase):

    def test_empty(self):
        target = self._make_filter([])
        self.assertTrue(target.matches(1))
    
    def test_single_true(self):
        target = self._make_filter([True])
        self.assertTrue(target.matches(1))
    
    def test_single_false(self):
        target = self._make_filter([False])
        self.assertFalse(target.matches(1))
    
    def test_multiple_true(self):
        target = self._make_filter([True, True])
        self.assertTrue(target.matches(1))
    
    def test_multiple_false(self):
        target = self._make_filter([True, False])
        self.assertFalse(target.matches(1))
    
    def test_none(self):
        target = self._make_filter([True, True])
        self.assertTrue(target.matches(None))

    def _make_filter(self, values):
        inner_filters = map(lambda x: self._make_inner_filter(x), values)
        return afscgap.flat_local_filter.LogicalAndLocalFilter(inner_filters)
    
    def _make_inner_filter(self, value):
        mock = unittest.mock.MagicMock()
        mock.matches = unittest.mock.MagicMock(return_value=value)
        return mock


class BuildIndividualFilterTests(unittest.TestCase):

    def test_empty(self):
        param = afscgap.param.EmptyParam()
        local_filter = afscgap.flat_local_filter.build_individual_filter('year', param)
        self.assertIsNone(local_filter)

    def test_equals_true(self):
        param = afscgap.param.IntEqualsParam(2025)
        local_filter = afscgap.flat_local_filter.build_individual_filter('year', param)
        self.assertTrue(local_filter.matches(self._make_target(2025)))
    
    def test_equals_false(self):
        param = afscgap.param.IntEqualsParam(2025)
        local_filter = afscgap.flat_local_filter.build_individual_filter('year', param)
        self.assertFalse(local_filter.matches(self._make_target(2024)))

    def test_range_true(self):
        param = afscgap.param.IntRangeParam(2024, 2026)
        local_filter = afscgap.flat_local_filter.build_individual_filter('year', param)
        self.assertTrue(local_filter.matches(self._make_target(2025)))

    def test_range_false(self):
        param = afscgap.param.IntRangeParam(2024, 2026)
        local_filter = afscgap.flat_local_filter.build_individual_filter('year', param)
        self.assertFalse(local_filter.matches(self._make_target(2023)))

    def test_unsupported_accessor(self):
        with self.assertRaises(RuntimeError):
            param = afscgap.param.EmptyParam()
            afscgap.flat_local_filter.build_individual_filter('unknown', param)

    def test_unsupported_filter(self):
        with self.assertRaises(RuntimeError):
            param = unittest.mock.MagicMock()
            param.get_filter_type = unittest.mock.MagicMock(return_value='unknown')
            afscgap.flat_local_filter.build_individual_filter('year', param)
    
    def _make_target(self, target_value):
        mock_target = unittest.mock.MagicMock()
        mock_target.get_year = unittest.mock.MagicMock(return_value=target_value)
        return mock_target


class BuildFilterTests(unittest.TestCase):

    def setUp(self):
        params = {
            'year': afscgap.param.IntRangeParam(2024, 2026),
            'srvy': afscgap.param.StrEqualsParam('GOA'),
            'count': afscgap.param.EmptyParam()
        }
        self._local_filter = afscgap.flat_local_filter.build_filter(params)

    def test_true(self):
        example = self._build_example(2025, 'GOA', 123)
        self.assertTrue(self._local_filter.matches(example))

    def test_false_int(self):
        example = self._build_example(2023, 'GOA', 123)
        self.assertFalse(self._local_filter.matches(example))
    
    def test_false_str(self):
        example = self._build_example(2025, 'Other', 123)
        self.assertFalse(self._local_filter.matches(example))
    
    def test_ignorable(self):
        example = self._build_example(2025, 'GOA', None)
        self.assertTrue(self._local_filter.matches(example))

    def _build_example(self, year, survey, count):
        mock = unittest.mock.MagicMock()
        mock.get_year = unittest.mock.MagicMock(return_value=year)
        mock.get_srvy = unittest.mock.MagicMock(return_value=survey)
        mock.get_count = unittest.mock.MagicMock(return_value=count)
        return mock
