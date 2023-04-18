"""
Tests for HTTP utilities.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import unittest
import unittest.mock

import afscgap.http_util


class UtilTests(unittest.TestCase):

    def test_check_result_ok(self):
        response = unittest.mock.MagicMock()
        response.status_code = 200
        afscgap.http_util.check_result(response)
        self.assertTrue(True)

    def test_check_result_not_ok(self):
        with self.assertRaises(RuntimeError):
            response = unittest.mock.MagicMock()
            response.status_code = 400
            afscgap.http_util.check_result(response)

    def test_build_requestor(self):
        self.assertIsNotNone(afscgap.http_util.build_requestor())
