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
