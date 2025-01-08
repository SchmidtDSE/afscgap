"""
Tests for script to join data to build flat files.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import unittest
import unittest.mock

import render_flat


class ZeroRecordTests(unittest.TestCase):

    def setUp(self):
        self._species = {
            'species_code': 1,
            'scientific_name': 'test_science',
            'common_name': 'test_common',
            'id_rank': 2,
            'worms': False,
            'itis': 3
        }
        self._species_by_code = {
            1: self._species
        }
        self._haul_record = {'haul_field': 123}
        self._zero_record_sample = render_flat.make_zero_record(
            self._species,
            self._haul_record
        )

    def test_make_zero_record_haul(self):
        self.assertEqual(self._zero_record_sample['haul_field'], 123)

    def test_make_zero_record_zero(self):
        self.assertEqual(self._zero_record_sample['count'], 0)

    def test_make_zero_record_species(self):
        self.assertEqual(self._zero_record_sample['scientific_name'], 'test_science')

    def test_make_zero_catch_records_no_infer(self):
        output_records_iter = render_flat.make_zero_catch_records(
            [{'species_code': 1, 'haul_field': 456}],
            self._species_by_code,  # type: ignore
            self._haul_record
        )
        output_records = list(output_records_iter)
        self.assertEqual(len(output_records), 0)

    def test_make_zero_catch_records_infer(self):
        output_records_iter = render_flat.make_zero_catch_records(
            [{'species_code': 2, 'haul_field': 456}],
            self._species_by_code,  # type: ignore
            self._haul_record
        )
        output_records = list(output_records_iter)
        self.assertEqual(len(output_records), 1)
        self.assertEqual(output_records[0]['haul_field'], 123)


class JoinTests(unittest.TestCase):

    def setUp(self):
        self._known = {'species_code': 1, 'catch_field': 12}
        self._unknown = {'species_code': 2, 'catch_field': 23}
        self._catch_records = [self._known, self._unknown]
        self._species_by_code = {
            1: {'species_field': 34}
        }
        self._haul_record = {'haul_field': 45}

    def test_append_complete_catch_field(self):
        result = render_flat.append_species_from_species_list(
            self._known,
            self._species_by_code  # type: ignore
        )
        self.assertEqual(result['catch_field'], 12)

    def test_append_complete_species_field(self):
        result = render_flat.append_species_from_species_list(
            self._known,
            self._species_by_code  # type: ignore
        )
        self.assertEqual(result['species_field'], 34)

    def test_append_complete_flag(self):
        result = render_flat.append_species_from_species_list(
            self._known,
            self._species_by_code  # type: ignore
        )
        self.assertTrue(result['complete'])

    def test_append_incomplete_catch_field(self):
        result = render_flat.append_species_from_species_list(
            self._unknown,
            self._species_by_code  # type: ignore
        )
        self.assertEqual(result['catch_field'], 23)

    def test_append_incomplete_species_field(self):
        result = render_flat.append_species_from_species_list(
            self._unknown,
            self._species_by_code  # type: ignore
        )
        self.assertFalse('species_field' in result)

    def test_append_incomplete_flag(self):
        result = render_flat.append_species_from_species_list(
            self._unknown,
            self._species_by_code  # type: ignore
        )
        self.assertFalse(result['complete'])

    def test_full_join_execution(self):
        full_join = self._execute_full_join()
        count = sum(map(lambda x: 1, full_join))
        self.assertEqual(count, 2)

    def test_full_join_no_catch(self):
        result = render_flat.execute_full_join(
            self._haul_record,
            None,
            self._species_by_code  # type: ignore
        )

        result_realized = list(result)
        self.assertEqual(len(result_realized), 1)

        result_individual = result_realized[0]
        self.assertFalse(result_individual['complete'])

    def test_full_join_no_species(self):
        target = self._get_species_code_from_join(2)
        self.assertFalse(target['complete'])
        self.assertEqual(target['catch_field'], 23)
        self.assertEqual(target['haul_field'], 45)

    def test_full_join_success(self):
        target = self._get_species_code_from_join(1)
        self.assertTrue(target['complete'])
        self.assertEqual(target['catch_field'], 12)
        self.assertEqual(target['species_code'], 1)
        self.assertEqual(target['haul_field'], 45)

    def _execute_full_join(self):
        return render_flat.execute_full_join(
            self._haul_record,
            self._catch_records,
            self._species_by_code  # type: ignore
        )

    def _get_species_code_from_join(self, species_code):
        full_join = self._execute_full_join()
        full_join_tuple = map(lambda x: (x['species_code'], x), full_join)
        full_join_dict = dict(full_join_tuple)
        return full_join_dict[species_code]


class MakeAvroTests(unittest.TestCase):

    def test_make_get_avro(self):
        client = unittest.mock.MagicMock()
        result = render_flat.make_get_avro('bucket', client)
        self.assertIsNotNone(result)


class CombineCatchHaulTests(unittest.TestCase):

    def test_append_catch_haul(self):
        catch = {'catch_field': 12}
        haul = {'haul_field': 34}
        combined = render_flat.append_catch_haul(catch, haul)
        self.assertEqual(combined['catch_field'], 12)
        self.assertEqual(combined['haul_field'], 34)


class CompleteRecordTests(unittest.TestCase):

    def setUp(self):
        self._start_record = {'unknown': 12, 'count': 34}
        self._completed = render_flat.complete_record(self._start_record)

    def test_complete_record_pass_through(self):
        self.assertEqual(self._completed['count'], 34)

    def test_complete_record_unknown_field(self):
        self.assertFalse('unknown' in self._completed)

    def test_complete_record_missing_field(self):
        self.assertIsNone(self._completed['species_code'])

    def test_mark_complete(self):
        result = render_flat.mark_complete(self._start_record)
        self.assertTrue(result['complete'])

    def test_mark_incomplete(self):
        result = render_flat.mark_incomplete(self._start_record)
        self.assertFalse(result['complete'])


class PathTests(unittest.TestCase):

    def test_get_path_for_catches_in_haul(self):
        path = render_flat.get_path_for_catches_in_haul(123)
        self.assertEqual(path, 'catch/123.avro')

    def test_get_meta_path_for_haul(self):
        path = render_flat.get_meta_path_for_haul(2025, 'Gulf of Alaska', 123)
        self.assertEqual(path, 'haul/2025_Gulf of Alaska_123.avro')

    def test_get_joined_path(self):
        path = render_flat.get_joined_path(2025, 'Gulf of Alaska', 123)
        self.assertEqual(path, 'joined/2025_Gulf of Alaska_123.avro')

    def test_make_haul_metadata_record(self):
        path = render_flat.get_joined_path(2025, 'Gulf of Alaska', 123)
        metadata = render_flat.make_haul_metadata_record(path)
        self.assertEqual(metadata['loc'], path)
        self.assertEqual(metadata['year'], 2025)
        self.assertEqual(metadata['survey'], 'Gulf of Alaska')
        self.assertEqual(metadata['haul'], 123)
