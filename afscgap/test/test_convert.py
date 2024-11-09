import unittest
import unittest.mock

import afscgap.convert


class ConvertTests(unittest.TestCase):

    def test_iso8601_regex_not_found(self):
        self.assertIsNone(
            afscgap.convert.ISO_8601_REGEX.match('07/16/2021 11:30:22')
        )

    def test_iso8601_regex_found(self):
        self.assertIsNotNone(
            afscgap.convert.ISO_8601_REGEX.match('2021-07-16T11:30:22')
        )

    def test_is_iso8601_success(self):
        self.assertTrue(afscgap.convert.is_iso8601('2021-07-16T11:30:22'))

    def test_is_iso8601_fail(self):
        self.assertFalse(afscgap.convert.is_iso8601('07/16/2021 11:30:22'))

    def test_convert_area(self):
        self.assertAlmostEqual(
            afscgap.convert.convert(123, 'km2', 'm2'),
            123000000
        )

    def test_unconvert_area(self):
        self.assertAlmostEqual(
            afscgap.convert.convert(123000000, 'm2', 'km2'),
            123
        )

    def test_convert_degrees(self):
        self.assertAlmostEqual(
            afscgap.convert.convert(123, 'dd', 'dd'),
            123
        )

    def test_convert_distance(self):
        self.assertAlmostEqual(
            afscgap.convert.convert(123, 'm', 'km'),
            0.123
        )

    def test_unconvert_distance(self):
        self.assertAlmostEqual(
            afscgap.convert.convert(123, 'km', 'm'),
            123000
        )

    def test_convert_temperature(self):
        self.assertAlmostEqual(
            afscgap.convert.convert(12, 'c', 'f'),
            53.6
        )

    def test_unconvert_temperature(self):
        self.assertAlmostEqual(
            afscgap.convert.convert(12, 'f', 'c'),
            -11.111111111
        )

    def test_convert_time(self):
        self.assertAlmostEqual(
            afscgap.convert.convert(123, 'hr', 'day'),
            5.125
        )

    def test_unconvert_time(self):
        self.assertAlmostEqual(
            afscgap.convert.convert(123, 'min', 'hr'),
            2.05
        )

    def test_convert_weight(self):
        self.assertAlmostEqual(
            afscgap.convert.convert(12, 'kg', 'g'),
            12000
        )

    def test_unconvert_weight(self):
        self.assertAlmostEqual(
            afscgap.convert.convert(12, 'g', 'kg'),
            0.012
        )
