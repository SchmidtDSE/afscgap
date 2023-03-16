"""
Tests for the afscgap web based visualization.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.txt.
"""
import unittest

import afscgapviz


class AfscgapvizTests(unittest.TestCase):

    def test_sort_names_by_lower(self):
        result = afscgapviz.sort_names_by_lower(['ABC', 'cDE', 'aAbc'])
        self.assertEquals(len(result), 3)
        self.assertEquals(result[0], 'aAbc')
        self.assertEquals(result[1], 'ABC')
        self.assertEquals(result[2], 'cDE')
