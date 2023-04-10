import unittest
import unittest.mock

import afscgap.convert


class ConvertTests(unittest.TestCase):

    def test_convert_to_iso8601_success(self):
        result = afscgap.convert.convert_to_iso8601('07/16/2021 11:30:22')
        self.assertEqual(result, '2021-07-16T11:30:22')

    def test_convert_to_iso8601_fail(self):
        result = afscgap.convert.convert_to_iso8601('test')
        self.assertEqual(result, 'test')

    def test_iso8601_regex_not_found(self):
        self.assertIsNone(
            afscgap.convert.ISO_8601_REGEX.match('07/16/2021 11:30:22')
        )

    def test_iso8601_regex_found(self):
        self.assertIsNotNone(
            afscgap.convert.ISO_8601_REGEX.match('2021-07-16T11:30:22')
        )

    def test_convert_from_iso8601_match_string(self):
        result = afscgap.convert.convert_from_iso8601_str(
            '2021-07-16T11:30:22'
        )
        self.assertEquals(result, '07/16/2021 11:30:22')

    def test_convert_from_iso8601_match_string_with_tz(self):
        result = afscgap.convert.convert_from_iso8601_str(
            '2021-07-16T11:30:22Z'
        )
        self.assertEquals(result, '07/16/2021 11:30:22')

    def test_convert_from_iso8601_match_dict(self):
        test_dict = {
            'a': '2021-07-16T11:30:22',
            'b': 'test2',
            'c': 3
        }
        result = afscgap.convert.convert_from_iso8601(test_dict)
        self.assertEquals(result['a'], '07/16/2021 11:30:22')
        self.assertEquals(result['b'], 'test2')
        self.assertEquals(result['c'], 3)

    def test_convert_from_iso8601_match_none(self):
        result = afscgap.convert.convert_from_iso8601(3)
        self.assertEquals(result, 3)

    def test_is_iso8601_success(self):
        self.assertTrue(afscgap.convert.is_iso8601('2021-07-16T11:30:22'))

    def test_is_iso8601_fail(self):
        self.assertFalse(afscgap.convert.is_iso8601('07/16/2021 11:30:22'))
