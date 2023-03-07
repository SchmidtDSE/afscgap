"""
Tests for afscgap backend utility functions.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.txt.
"""
import unittest

import util


class UtilTests(unittest.TestCase):

    def test_get_sql(self):
        sql = util.get_sql('insert_record')
        self.assertTrue('INSERT' in sql)
