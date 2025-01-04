"""
Tests for the main index generation script.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import unittest
import unittest.mock

import write_main_index

EXAMPLE_URL = 'joined/2025_Gulf of Alaska_123.avro'


class HaulMetadataRecordTests(unittest.TestCase):

    def setUp(self):
        self._record = write_main_index.make_haul_metadata_record(EXAMPLE_URL)

    def test_year(self):
        self.assertEqual(self._record['year'], 2025)

    def test_survey(self):
        self.assertEqual(self._record['survey'], 'Gulf of Alaska')

    def test_haul(self):
        self.assertEqual(self._record['haul'], 123)
