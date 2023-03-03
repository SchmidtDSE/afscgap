import unittest
import unittest.mock

import afscgap.util


class UtilTests(unittest.TestCase):

    def test_check_result_ok(self):
        response = unittest.mock.MagicMock()
        response.status_code = 200
        afscgap.util.check_result(response)
        self.assertTrue(True)

    def test_check_result_not_ok(self):
        with self.assertRaises(RuntimeError):
            response = unittest.mock.MagicMock()
            response.status_code = 400
            afscgap.util.check_result(response)

    def test_convert_to_iso8601_success(self):
        result = afscgap.util.convert_to_iso8601('07/16/2021 11:30:22')
        self.assertEqual(result, '2021-07-16T11:30:22')

    def test_convert_to_iso8601_fail(self):
        result = afscgap.util.convert_to_iso8601('test')
        self.assertEqual(result, 'test')

    def test_iso8601_regex_not_found(self):
        self.assertIsNone(
            afscgap.util.ISO_8601_REGEX.match('07/16/2021 11:30:22')
        )

    def test_iso8601_regex_found(self):
        self.assertIsNotNone(
            afscgap.util.ISO_8601_REGEX.match('2021-07-16T11:30:22')
        )

    def test_convert_from_iso8601_match_string(self):
        result = afscgap.util.convert_from_iso8601_str('2021-07-16T11:30:22')
        self.assertEquals(result, '07/16/2021 11:30:22')

    def test_convert_from_iso8601_match_string_with_tz(self):
        result = afscgap.util.convert_from_iso8601_str('2021-07-16T11:30:22Z')
        self.assertEquals(result, '07/16/2021 11:30:22')

    def test_convert_from_iso8601_match_dict(self):
        test_dict = {
            'a': '2021-07-16T11:30:22',
            'b': 'test2',
            'c': 3
        }
        result = afscgap.util.convert_from_iso8601(test_dict)
        self.assertEquals(result['a'], '07/16/2021 11:30:22')
        self.assertEquals(result['b'], 'test2')
        self.assertEquals(result['c'], 3)

    def test_convert_from_iso8601_match_none(self):
        result = afscgap.util.convert_from_iso8601(3)
        self.assertEquals(result, 3)

    def test_is_iso8601_success(self):
        self.assertTrue(afscgap.util.is_iso8601('2021-07-16T11:30:22'))

    def test_is_iso8601_fail(self):
        self.assertFalse(afscgap.util.is_iso8601('07/16/2021 11:30:22'))

    def test_build_requestor(self):
        self.assertIsNotNone(afscgap.util.build_requestor())
