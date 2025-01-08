"""
Tests for entrypoint into flat implementors.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import unittest
import unittest.mock

import afscgap.flat


class FlatTests(unittest.TestCase):

    def setUp(self):
        self._warn_function = unittest.mock.MagicMock()
        self._meta = unittest.mock.MagicMock()
        self._meta.get_warn_func = unittest.mock.MagicMock(return_value=self._warn_function)
        self._meta.get_suppress_large_warning = unittest.mock.MagicMock(return_value=False)

    def test_check_warning_warn(self):
        afscgap.flat.check_warning(range(0, 4000), self._meta)
        self._warn_function.assert_called()

    def test_check_warning_noop(self):
        afscgap.flat.check_warning(range(0, 10), self._meta)
        self._warn_function.assert_not_called()
