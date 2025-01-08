"""
Tests for flat records cursor and its decorators.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import unittest
import unittest.mock

import afscgap.flat_cursor


class FlatCursorTests(unittest.TestCase):

    def setUp(self):
        def make_record(target_id):
            mock = unittest.mock.MagicMock()
            mock.get_id = unittest.mock.MagicMock(return_value=target_id)
            mock.to_dict = unittest.mock.MagicMock(return_value={'id': target_id})
            return mock

        self._records = [make_record(1), make_record(2), make_record(3)]
        self._cursor = afscgap.flat_cursor.FlatCursor(self._records)

    def test_get_attrs(self):
        self.assertIsNone(self._cursor.get_limit())
        self.assertFalse(self._cursor.get_filtering_incomplete())

    def test_get_next(self):
        first = self._cursor.get_next()
        second = self._cursor.get_next()
        third = self._cursor.get_next()
        self.assertEqual(first.get_id(), 1)
        self.assertEqual(second.get_id(), 2)
        self.assertEqual(third.get_id(), 2)
        self.assertIsNone(self._cursor.get_next())

    def test_to_dicts(self):
        dicts = self._cursor.to_dicts()
        self.assertEqual(len(dicts), 3)
        self.assertEqual(dicts[0]['id'], 1)
        self.assertEqual(dicts[1]['id'], 2)
        self.assertEqual(dicts[2]['id'], 3)


class CompleteCursorTests(unittest.TestCase):

    def setUp(self):
        def make_record(target_id, complete):
            mock = unittest.mock.MagicMock()
            mock.get_id = unittest.mock.MagicMock(return_value=target_id)
            mock.is_complete = unittest.mock.MagicMock(return_value=complete)
            mock.to_dict = unittest.mock.MagicMock(return_value={
                'id': target_id,
                'complete': complete
            })
            return mock

        self._records = [make_record(1, True), make_record(2, False), make_record(3, True)]
        self._inner_cursor = afscgap.flat_cursor.FlatCursor(self._records)
        self._cursor = afscgap.flat_cursor.CompleteCursor(self._inner_cursor)

    def test_get_attrs(self):
        self.assertIsNone(self._cursor.get_limit())
        self.assertTrue(self._cursor.get_filtering_incomplete())

    def test_get_next(self):
        first = self._cursor.get_next()
        second = self._cursor.get_next()
        self.assertEqual(first.get_id(), 1)
        self.assertEqual(second.get_id(), 3)
        self.assertIsNone(self._cursor.get_next())

    def test_to_dicts(self):
        dicts = list(self._cursor.to_dicts())
        self.assertEqual(len(dicts), 2)
        self.assertEqual(dicts[0]['id'], 1)
        self.assertEqual(dicts[1]['id'], 3)


class FlatCursorTests(unittest.TestCase):

    def setUp(self):
        def make_record(target_id):
            mock = unittest.mock.MagicMock()
            mock.get_id = unittest.mock.MagicMock(return_value=target_id)
            mock.to_dict = unittest.mock.MagicMock(return_value={'id': target_id})
            return mock

        self._records = [make_record(1), make_record(2), make_record(3)]
        self._inner_cursor = afscgap.flat_cursor.FlatCursor(self._records)
        self._cursor = afscgap.flat_cursor.LimitCursor(self._inner_cursor, 2)

    def test_get_attrs(self):
        self.assertEqual(self._cursor.get_limit(), 2)
        self.assertFalse(self._cursor.get_filtering_incomplete())

    def test_get_next(self):
        first = self._cursor.get_next()
        second = self._cursor.get_next()
        self.assertEqual(first.get_id(), 1)
        self.assertEqual(second.get_id(), 2)
        self.assertIsNone(self._cursor.get_next())

    def test_to_dicts(self):
        dicts = list(self._cursor.to_dicts())
        self.assertEqual(len(dicts), 2)
        self.assertEqual(dicts[0]['id'], 1)
        self.assertEqual(dicts[1]['id'], 2)
