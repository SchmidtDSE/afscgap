"""
Tests for model utilities.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import unittest
import unittest.mock

import afscgap.model_util


class ModelUtilTests(unittest.TestCase):

    def test_get_opt_float_valid(self):
        self.assertAlmostEqual(afscgap.model_util.get_opt_float('1.23'), 1.23)

    def test_get_opt_float_invalid(self):
        self.assertIsNone(afscgap.model_util.get_opt_float('1.23abc'))

    def test_get_opt_float_none(self):
        self.assertIsNone(afscgap.model_util.get_opt_float(None))

    def test_get_opt_int_valid(self):
        self.assertEqual(afscgap.model_util.get_opt_float('123'), 123)

    def test_get_opt_int_invalid(self):
        self.assertIsNone(afscgap.model_util.get_opt_float('123abc'))

    def test_get_opt_int_none(self):
        self.assertIsNone(afscgap.model_util.get_opt_float(None))

    def assert_float_present_true(self):
        self.assertAlmostEqual(afscgap.model_util.assert_float_present(1.23), 1.23)

    def assert_float_present_false(self):
        with self.assertRaises(ValueError):
            afscgap.model_util.assert_float_present(None)

    def assert_int_present_true(self):
        self.assertEqual(afscgap.model_util.assert_float_present(123), 123)

    def assert_int_present_false(self):
        with self.assertRaises(ValueError):
            afscgap.model_util.assert_int_present(None)
