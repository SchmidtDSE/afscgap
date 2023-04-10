import unittest
import unittest.mock

import afscgap.http


class UtilTests(unittest.TestCase):

    def test_check_result_ok(self):
        response = unittest.mock.MagicMock()
        response.status_code = 200
        afscgap.http.check_result(response)
        self.assertTrue(True)

    def test_check_result_not_ok(self):
        with self.assertRaises(RuntimeError):
            response = unittest.mock.MagicMock()
            response.status_code = 400
            afscgap.http.check_result(response)

    def test_build_requestor(self):
        self.assertIsNotNone(afscgap.http.build_requestor())
