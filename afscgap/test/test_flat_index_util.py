"""
Tests for precomputed index filters.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import unittest
import unittest.mock

import afscgap.flat_index_util
import afscgap.param


class StringEqIndexFilterTests(unittest.TestCase):

    def setUp(self):
        param = unittest.mock.MagicMock()
        param.get_value = unittest.mock.MagicMock(return_value='test')
        self._index_filter = afscgap.flat_index_util.StringEqIndexFilter('index', param)

    def test_matches(self):
        self.assertTrue(self._index_filter.get_matches('test'))

    def test_not_matches(self):
        self.assertFalse(self._index_filter.get_matches('other'))

    def test_not_matches_case(self):
        self.assertFalse(self._index_filter.get_matches('Test'))

    def test_none(self):
        self.assertFalse(self._index_filter.get_matches(None))


class StringRangeIndexFilterTests(unittest.TestCase):

    def setUp(self):
        param = unittest.mock.MagicMock()
        param.get_low = unittest.mock.MagicMock(return_value='b')
        param.get_high = unittest.mock.MagicMock(return_value='d')
        self._index_filter = afscgap.flat_index_util.StringRangeIndexFilter('index', param)

    def test_out_low(self):
        self.assertFalse(self._index_filter.get_matches('a'))

    def test_low(self):
        self.assertTrue(self._index_filter.get_matches('b'))

    def test_mid(self):
        self.assertTrue(self._index_filter.get_matches('c'))

    def test_high(self):
        self.assertTrue(self._index_filter.get_matches('d'))

    def test_out_high(self):
        self.assertFalse(self._index_filter.get_matches('e'))

    def test_none(self):
        self.assertFalse(self._index_filter.get_matches(None))


class IntEqIndexFilterTests(unittest.TestCase):

    def setUp(self):
        param = unittest.mock.MagicMock()
        param.get_value = unittest.mock.MagicMock(return_value=123)
        self._index_filter = afscgap.flat_index_util.IntEqIndexFilter('index', param)

    def test_matches(self):
        self.assertTrue(self._index_filter.get_matches(123))

    def test_not_matches(self):
        self.assertFalse(self._index_filter.get_matches(12))
    
    def test_none(self):
        self.assertFalse(self._index_filter.get_matches(None))


class IntRangeIndexFilterTests(unittest.TestCase):

    def setUp(self):
        param = unittest.mock.MagicMock()
        param.get_low = unittest.mock.MagicMock(return_value=2)
        param.get_high = unittest.mock.MagicMock(return_value=4)
        self._index_filter = afscgap.flat_index_util.IntRangeIndexFilter('index', param)

    def test_out_low(self):
        self.assertFalse(self._index_filter.get_matches(1))

    def test_low(self):
        self.assertTrue(self._index_filter.get_matches(2))

    def test_mid(self):
        self.assertTrue(self._index_filter.get_matches(3))

    def test_high(self):
        self.assertTrue(self._index_filter.get_matches(4))

    def test_out_high(self):
        self.assertFalse(self._index_filter.get_matches(5))

    def test_none(self):
        self.assertFalse(self._index_filter.get_matches(None))


class FloatEqIndexFilterTests(unittest.TestCase):

    def setUp(self):
        param = unittest.mock.MagicMock()
        param.get_value = unittest.mock.MagicMock(return_value=123.45)
        self._index_filter = afscgap.flat_index_util.FloatEqIndexFilter('index', param)

    def test_matches(self):
        self.assertTrue(self._index_filter.get_matches(123.45))

    def test_not_matches(self):
        self.assertFalse(self._index_filter.get_matches(12))

    def test_approx_not_matches(self):
        self.assertFalse(self._index_filter.get_matches(123.4555))

    def test_approx_matches(self):
        self.assertTrue(self._index_filter.get_matches(123.454))

    def test_none(self):
        self.assertFalse(self._index_filter.get_matches(None))


class FloatRangeIndexFilterTests(unittest.TestCase):

    def setUp(self):
        param = unittest.mock.MagicMock()
        param.get_low = unittest.mock.MagicMock(return_value=2.34)
        param.get_high = unittest.mock.MagicMock(return_value=4.56)
        self._index_filter = afscgap.flat_index_util.FloatRangeIndexFilter('index', param)

    def test_out_low(self):
        self.assertFalse(self._index_filter.get_matches(1))

    def test_low(self):
        self.assertTrue(self._index_filter.get_matches(2.34))
    
    def test_low_approx_match(self):
        self.assertTrue(self._index_filter.get_matches(2.3355))
    
    def test_low_approx_not_match(self):
        self.assertFalse(self._index_filter.get_matches(2.3344))

    def test_mid(self):
        self.assertTrue(self._index_filter.get_matches(3))

    def test_high(self):
        self.assertTrue(self._index_filter.get_matches(4.56))
    
    def test_high_approx_match(self):
        self.assertTrue(self._index_filter.get_matches(4.561))
    
    def test_high_approx_not_match(self):
        self.assertFalse(self._index_filter.get_matches(4.5655))

    def test_out_high(self):
        self.assertFalse(self._index_filter.get_matches(5))

    def test_none(self):
        self.assertFalse(self._index_filter.get_matches(None))


class DatetimeEqIndexFilterTests(unittest.TestCase):

    def setUp(self):
        param = unittest.mock.MagicMock()
        param.get_value = unittest.mock.MagicMock(return_value='2025-01-13T13:50:50Z')
        self._index_filter = afscgap.flat_index_util.DatetimeEqIndexFilter('index', param)

    def test_matches(self):
        self.assertTrue(self._index_filter.get_matches('2025-01-13T13:50:50Z'))

    def test_not_matches(self):
        self.assertFalse(self._index_filter.get_matches('2025-02-13T13:50:50Z'))

    def test_approx_not_matches(self):
        self.assertFalse(self._index_filter.get_matches('2025-01-14T13:50:50Z'))

    def test_approx_matches(self):
        self.assertTrue(self._index_filter.get_matches('2025-01-13T14:50:50Z'))

    def test_none(self):
        self.assertFalse(self._index_filter.get_matches(None))


class DatetimeRangeIndexFilterTests(unittest.TestCase):

    def setUp(self):
        param = unittest.mock.MagicMock()
        param.get_low = unittest.mock.MagicMock(return_value='2025-01-13T13:50:50Z')
        param.get_high = unittest.mock.MagicMock(return_value='2025-03-13T13:50:50Z')
        self._index_filter = afscgap.flat_index_util.DatetimeRangeIndexFilter('index', param)

    def test_out_low(self):
        self.assertFalse(self._index_filter.get_matches('2024-06-07T13:50:50Z'))

    def test_low(self):
        self.assertTrue(self._index_filter.get_matches('2025-01-13T13:50:50Z'))
    
    def test_low_approx_match(self):
        self.assertTrue(self._index_filter.get_matches('2025-01-13T14:50:50Z'))
    
    def test_low_approx_not_match(self):
        self.assertFalse(self._index_filter.get_matches('2025-01-12T13:50:50Z'))

    def test_mid(self):
        self.assertTrue(self._index_filter.get_matches('2025-02-13T14:50:50Z'))

    def test_high(self):
        self.assertTrue(self._index_filter.get_matches('2025-03-13T14:50:50Z'))
    
    def test_high_approx_match(self):
        self.assertTrue(self._index_filter.get_matches('2025-03-13T15:50:50Z'))
    
    def test_high_approx_not_match(self):
        self.assertFalse(self._index_filter.get_matches('2025-03-14T14:50:50Z'))

    def test_out_high(self):
        self.assertFalse(self._index_filter.get_matches('2025-04-13T14:50:50Z'))

    def test_none(self):
        self.assertFalse(self._index_filter.get_matches(None))


class UnitConversionIndexFilterTests(unittest.TestCase):

    def setUp(self):
        self._inner = unittest.mock.MagicMock()
        self._inner.get_matches = lambda x: x is not None and abs(x - 10000) < 0.001

    def test_noop_true(self):
        index_filter = afscgap.flat_index_util.UnitConversionIndexFilter(self._inner, 'ha', 'ha')
        self.assertTrue(index_filter.get_matches(10000))
    
    def test_noop_false(self):
        index_filter = afscgap.flat_index_util.UnitConversionIndexFilter(self._inner, 'ha', 'ha')
        self.assertFalse(index_filter.get_matches(20000))
    
    def test_noop_none(self):
        index_filter = afscgap.flat_index_util.UnitConversionIndexFilter(self._inner, 'ha', 'ha')
        self.assertFalse(index_filter.get_matches(None))
    
    def test_convert_true(self):
        index_filter = afscgap.flat_index_util.UnitConversionIndexFilter(self._inner, 'm2', 'ha')
        self.assertTrue(index_filter.get_matches(1))
    
    def test_convert_false(self):
        index_filter = afscgap.flat_index_util.UnitConversionIndexFilter(self._inner, 'm2', 'ha')
        self.assertFalse(index_filter.get_matches(2))
    
    def test_convert_none(self):
        index_filter = afscgap.flat_index_util.UnitConversionIndexFilter(self._inner, 'm2', 'ha')
        self.assertFalse(index_filter.get_matches(None))


class LogicalOrIndexFilterTests(unittest.TestCase):

    def test_true_single(self):
        index_filter = afscgap.flat_index_util.LogicalOrIndexFilter([
            self._make_inner_filter(1, 'test')
        ])
        self.assertTrue(index_filter.get_matches(1))

    def test_true_multiple(self):
        index_filter = afscgap.flat_index_util.LogicalOrIndexFilter([
            self._make_inner_filter(1, 'test'),
            self._make_inner_filter(1, 'test')
        ])
        self.assertTrue(index_filter.get_matches(1))

    def test_true_multiple_different(self):
        index_filter = afscgap.flat_index_util.LogicalOrIndexFilter([
            self._make_inner_filter(1, 'test'),
            self._make_inner_filter(2, 'test')
        ])
        self.assertTrue(index_filter.get_matches(1))

    def test_false_single(self):
        index_filter = afscgap.flat_index_util.LogicalOrIndexFilter([
            self._make_inner_filter(1, 'test')
        ])
        self.assertFalse(index_filter.get_matches(2))

    def test_false_multiple(self):
        index_filter = afscgap.flat_index_util.LogicalOrIndexFilter([
            self._make_inner_filter(1, 'test'),
            self._make_inner_filter(1, 'test')
        ])
        self.assertFalse(index_filter.get_matches(2))

    def test_empty(self):
        with self.assertRaises(RuntimeError):
            afscgap.flat_index_util.LogicalOrIndexFilter([])
    
    def test_unmatched(self):
        index_filter = afscgap.flat_index_util.LogicalOrIndexFilter([
            self._make_inner_filter(1, 'test1'),
            self._make_inner_filter(2, 'test2')
        ])
        index_names = list(index_filter.get_index_names())
        self.assertEqual(len(index_names), 2)
        self.assertTrue('test1' in index_names)
        self.assertTrue('test2' in index_names)

    def _make_inner_filter(self, value, index):
        mock = unittest.mock.MagicMock()
        mock.get_matches = lambda x: x == value
        mock.get_index_names = unittest.mock.MagicMock(return_value=[index])
        return mock


class DecorateFilterTests(unittest.TestCase):

    def setUp(self):
        self._inner = unittest.mock.MagicMock()
        self._inner.get_matches = lambda x: x is not None and abs(x - 123) < 0.001

    def test_decorate_filter_active_true(self):
        decorated = afscgap.flat_index_util.decorate_filter('area_swept_ha', self._inner)
        self.assertTrue(decorated.get_matches(12300))
    
    def test_decorate_filter_active_false(self):
        decorated = afscgap.flat_index_util.decorate_filter('area_swept_ha', self._inner)
        self.assertFalse(decorated.get_matches(12400))
    
    def test_decorate_filter_active_none(self):
        decorated = afscgap.flat_index_util.decorate_filter('area_swept_ha', self._inner)
        self.assertFalse(decorated.get_matches(None))

    def test_decorate_filter_active_true(self):
        decorated = afscgap.flat_index_util.decorate_filter('other', self._inner)
        self.assertTrue(decorated.get_matches(123))

    def test_decorate_filter_active_true(self):
        decorated = afscgap.flat_index_util.decorate_filter('other', self._inner)
        self.assertFalse(decorated.get_matches(124))
    
    def test_decorate_filter_active_none(self):
        decorated = afscgap.flat_index_util.decorate_filter('other', self._inner)
        self.assertFalse(decorated.get_matches(None))


class MakeFilterTests(unittest.TestCase):

    def test_empty(self):
        param = afscgap.param.EmptyParam()
        filters = afscgap.flat_index_util.make_filters('test', param, True)
        self.assertEqual(len(filters), 0)

    def test_string_true(self):
        param = afscgap.param.StrEqualsParam('test')
        filters = afscgap.flat_index_util.make_filters('common_name', param, True)
        self.assertEqual(len(filters), 1)
        self.assertTrue(filters[0].get_matches('test'))

    def test_string_false(self):
        param = afscgap.param.StrEqualsParam('test')
        filters = afscgap.flat_index_util.make_filters('common_name', param, True)
        self.assertEqual(len(filters), 1)
        self.assertFalse(filters[0].get_matches('other'))

    def test_int_true(self):
        param = afscgap.param.IntEqualsParam(1)
        filters = afscgap.flat_index_util.make_filters('vessel_id', param, True)
        self.assertEqual(len(filters), 1)
        self.assertTrue(filters[0].get_matches(1))

    def test_int_false(self):
        param = afscgap.param.IntEqualsParam(1)
        filters = afscgap.flat_index_util.make_filters('vessel_id', param, True)
        self.assertEqual(len(filters), 1)
        self.assertFalse(filters[0].get_matches(2))

    def test_float_true(self):
        param = afscgap.param.FloatEqualsParam(1.234)
        filters = afscgap.flat_index_util.make_filters('latitude_dd', param, True)
        self.assertEqual(len(filters), 1)
        self.assertTrue(filters[0].get_matches(1.233))

    def test_float_false(self):
        param = afscgap.param.FloatEqualsParam(1.234)
        filters = afscgap.flat_index_util.make_filters('latitude_dd', param, True)
        self.assertEqual(len(filters), 1)
        self.assertFalse(filters[0].get_matches(1.2355))

    def test_unit_conversion_true(self):
        param = afscgap.param.FloatEqualsParam(1)
        filters = afscgap.flat_index_util.make_filters('area_swept_ha', param, True)
        self.assertEqual(len(filters), 1)
        self.assertTrue(filters[0].get_matches(0.01))

    def test_unit_conversion_false(self):
        param = afscgap.param.FloatEqualsParam(1)
        filters = afscgap.flat_index_util.make_filters('area_swept_ha', param, True)
        self.assertEqual(len(filters), 1)
        self.assertFalse(filters[0].get_matches(0.02))

    def test_unknown_field(self):
        param = afscgap.param.FloatEqualsParam(1)
        filters = afscgap.flat_index_util.make_filters('other', param, True)
        self.assertEqual(len(filters), 0)
