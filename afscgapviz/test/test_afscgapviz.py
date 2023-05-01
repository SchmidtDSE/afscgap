"""
Tests for the afscgap web based visualization.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
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
    
    def test_transform_keys_for_delta(self):
        target = {
            'year': 1,
            'survey': 2,
            'species': 3,
            'commonName': 4,
            'geohash': 5,
            'surfaceTemperatureC': 6,
            'bottomTemperatureC': 7,
            'weightKg': 8,
            'count': 9,
            'areaSweptHectares': 10,
            'numRecordsAggregated': 11,
            'latLowDegrees': 12,
            'lngLowDegrees': 13,
            'latHighDegrees': 14,
            'lngHighDegrees': 15
        }

        result = afscgapviz.transform_keys_for_delta(target)
        self.assertEqual(result['year'], 1)
        self.assertEqual(result['weightKgDelta'], 8)
        self.assertFalse('weightKg' in result)
