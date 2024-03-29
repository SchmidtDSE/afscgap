"""
Unit tests for data structures as part of afscgap.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import unittest

import afscgap.model
import afscgap.test.test_tools

# pylint: disable=C0115, C0116


class ModelTests(unittest.TestCase):

    def test_get_opt_float_valid(self):
        self.assertAlmostEquals(afscgap.model.get_opt_float('1.48E+002'), 148)

    def test_get_opt_float_not_given(self):
        self.assertIsNone(afscgap.model.get_opt_float(None))

    def test_get_opt_float_na(self):
        self.assertIsNone(afscgap.model.get_opt_float('NA'))

    def test_get_opt_int_valid(self):
        self.assertEquals(afscgap.model.get_opt_int('148'), 148)

    def test_get_opt_int_not_given(self):
        self.assertIsNone(afscgap.model.get_opt_int(None))

    def test_get_opt_int_na(self):
        self.assertIsNone(afscgap.model.get_opt_int('NA'))

    def test_assert_float_present_true(self):
        self.assertAlmostEquals(
            afscgap.model.assert_float_present(1.23),
            1.23
        )

    def test_assert_float_present_false(self):
        with self.assertRaises(AssertionError):
            afscgap.model.assert_float_present(None)

    def test_assert_int_present_true(self):
        self.assertEquals(
            afscgap.model.assert_int_present(123),
            123
        )

    def test_assert_int_present_false(self):
        with self.assertRaises(AssertionError):
            afscgap.model.assert_int_present(None)
