"""
Tests for objects reprensenting flat files.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import unittest
import unittest.mock

import afscgap.flat_model

EXPECTED_FIELDS = {
    'year',
    'srvy',
    'survey',
    'survey_name',
    'survey_definition_id',
    'cruise',
    'cruisejoin',
    'hauljoin',
    'haul',
    'stratum',
    'station',
    'vessel_id',
    'vessel_name',
    'date_time',
    'latitude_dd_start',
    'longitude_dd_start',
    'latitude_dd_end',
    'longitude_dd_end',
    'bottom_temperature_c',
    'surface_temperature_c',
    'depth_m',
    'distance_fished_km',
    'duration_hr',
    'net_width_m',
    'net_height_m',
    'area_swept_km2',
    'performance',
    'species_code',
    'cpue_kgkm2',
    'cpue_nokm2',
    'count',
    'weight_kg',
    'taxon_confidence',
    'scientific_name',
    'common_name',
    'id_rank',
    'worms',
    'itis',
    'complete'
}


class ExecuteMetaParamsTests(unittest.TestCase):

    def setUp(self):
        self._params = afscgap.flat_model.ExecuteMetaParams(
            'test_base_url',
            'requestor',
            123,
            True,
            False,
            True,
            'warn_func'
        )

    def test_get_base_url(self):
        self.assertEqual(self._params.get_base_url(), 'test_base_url')

    def test_get_requestor(self):
        self.assertEqual(self._params.get_requestor(), 'requestor')

    def test_get_limit(self):
        self.assertEqual(self._params.get_limit(), 123)

    def test_get_filter_incomplete(self):
        self.assertEqual(self._params.get_filter_incomplete(), True)

    def test_get_presence_only(self):
        self.assertEqual(self._params.get_presence_only(), False)

    def test_get_suppress_large_warning(self):
        self.assertEqual(self._params.get_suppress_large_warning(), True)

    def test_get_warn_func(self):
        self.assertEqual(self._params.get_warn_func(), 'warn_func')


class HaulKeyTests(unittest.TestCase):

    def setUp(self):
        self._key = afscgap.flat_model.HaulKey(2025, 'Gulf of Alaska', 123)
        self._key_same = afscgap.flat_model.HaulKey(2025, 'Gulf of Alaska', 123)
        self._key_other_year = afscgap.flat_model.HaulKey(2026, 'Gulf of Alaska', 123)
        self._key_other_survey = afscgap.flat_model.HaulKey(2025, 'Other', 123)
        self._key_other_haul = afscgap.flat_model.HaulKey(2025, 'Gulf of Alaska', 124)

    def test_get_year(self):
        self.assertEqual(self._key.get_year(), 2025)

    def test_get_survey(self):
        self.assertEqual(self._key.get_survey(), 'Gulf of Alaska')

    def test_get_haul(self):
        self.assertEqual(self._key.get_haul(), 123)

    def test_get_key_same(self):
        self.assertEqual(self._key.get_key(), self._key_same.get_key())
    
    def test_get_key_different(self):
        self.assertNotEqual(self._key.get_key(), self._key_other_year.get_key())
        self.assertNotEqual(self._key.get_key(), self._key_other_survey.get_key())
        self.assertNotEqual(self._key.get_key(), self._key_other_haul.get_key())

    def test_get_path(self):
        self.assertEqual(self._key.get_path(), '/joined/2025_Gulf of Alaska_123.avro')

    def test_hash_eq(self):
        self.assertEqual(hash(self._key), hash(self._key_same))

    def test_hash_neq(self):
        self.assertNotEqual(hash(self._key), hash(self._key_other_year))
        self.assertNotEqual(hash(self._key), hash(self._key_other_survey))
        self.assertNotEqual(hash(self._key), hash(self._key_other_haul))

    def test_repr_eq(self):
        self.assertEqual(repr(self._key), repr(self._key_same))

    def test_repr_neq(self):
        self.assertNotEqual(repr(self._key), repr(self._key_other_year))
        self.assertNotEqual(repr(self._key), repr(self._key_other_survey))
        self.assertNotEqual(repr(self._key), repr(self._key_other_haul))

    def test_eq(self):
        self.assertEqual(self._key, self._key_same)

    def test_neq(self):
        self.assertNotEqual(self._key, self._key_other_year)
        self.assertNotEqual(self._key, self._key_other_survey)
        self.assertNotEqual(self._key, self._key_other_haul)


class FlatRecordTests(unittest.TestCase):

    def test_get_year(self):
        self._test_getter('year', 2025, lambda x: x.get_year())

    def test_get_srvy(self):
        self._test_getter('srvy', 'GOA', lambda x: x.get_srvy())

    def test_get_survey(self):
        self._test_getter('survey', 'Gulf of Alaska', lambda x: x.get_survey())

    def test_get_survey_id(self):
        self._test_getter('survey_definition_id', 123, lambda x: x.get_survey_id())

    def test_get_cruise(self):
        self._test_getter('cruise', 123, lambda x: x.get_cruise())

    def test_get_haul(self):
        self._test_getter('haul', 123, lambda x: x.get_haul())

    def test_get_stratum(self):
        self._test_getter('stratum', 123, lambda x: x.get_stratum())

    def test_get_station(self):
        self._test_getter('station', 'test station', lambda x: x.get_station())

    def test_get_vessel_name(self):
        self._test_getter('vessel_name', 'test vessel', lambda x: x.get_vessel_name())

    def test_get_vessel_id(self):
        self._test_getter('vessel_id', 123, lambda x: x.get_vessel_id())

    def test_get_date_time(self):
        self._test_getter('date_time', '2025-12-31', lambda x: x.get_date_time())

    # def test_get_latitude_start(self):
    #     pass

    # def test_get_longitude_start(self):
    #     pass

    # def test_get_latitude(self):
    #     pass

    # def test_get_longitude(self):
    #     pass

    # def test_get_latitude_end(self):
    #     pass

    # def test_get_longitude_end(self):
    #     pass

    def test_get_species_code(self):
        self._test_getter('species_code', 123, lambda x: x.get_species_code())

    def test_get_species_code_empty(self):
        self._test_getter('species_code', None, lambda x: x.get_species_code())

    def test_get_common_name(self):
        self._test_getter('common_name', 'test', lambda x: x.get_common_name())

    def test_get_common_name_empty(self):
        self._test_getter('common_name', None, lambda x: x.get_common_name())

    def test_get_scientific_name(self):
        self._test_getter('scientific_name', 'test', lambda x: x.get_scientific_name())

    def test_get_scientific_name_empty(self):
        self._test_getter('scientific_name', None, lambda x: x.get_scientific_name())

    def test_get_taxon_confidence(self):
        self._test_getter('taxon_confidence', 'test', lambda x: x.get_taxon_confidence())

    def test_get_taxon_confidence_empty(self):
        self._test_getter('taxon_confidence', None, lambda x: x.get_taxon_confidence())

    def test_get_cpue_weight_maybe_empty(self):
        self._test_getter('cpue_kgkm2', None, lambda x: x.get_cpue_weight_maybe())

    def test_get_cpue_weight_maybe_convert(self):
        self._test_getter_convert(
            'cpue_kgkm2',
            1.23,
            lambda x: x.get_cpue_weight_maybe('kg/ha'),
            'kg/km2',
            'kg/ha'
        )

    def test_get_cpue_count_maybe_empty(self):
        self._test_getter('cpue_nokm2', None, lambda x: x.get_cpue_count_maybe())

    def test_get_cpue_count_maybe_convert(self):
        self._test_getter_convert(
            'cpue_nokm2',
            1.23,
            lambda x: x.get_cpue_count_maybe('count/ha'),
            'no/km2',
            'count/ha'
        )

    def test_get_weight_maybe_empty(self):
        self._test_getter('weight_kg', None, lambda x: x.get_weight_maybe())

    def test_get_weight_maybe_convert(self):
        self._test_getter_convert(
            'weight_kg',
            1.23,
            lambda x: x.get_weight_maybe('g'),
            'kg',
            'g'
        )

    def test_get_count_maybe(self):
        self._test_getter('count', 1.23, lambda x: x.get_count_maybe())

    def test_get_count_maybe_empty(self):
        self._test_getter('count', None, lambda x: x.get_count_maybe())

    def test_get_bottom_temperature_maybe(self):
        self._test_getter(
            'bottom_temperature_c',
            1.23,
            lambda x: x.get_bottom_temperature_maybe()
        )

    def test_get_bottom_temperature_maybe_empty(self):
        self._test_getter(
            'bottom_temperature_c',
            None,
            lambda x: x.get_bottom_temperature_maybe()
        )

    def test_get_bottom_temperature_maybe_convert(self):
        self._test_getter_convert(
            'bottom_temperature_c',
            1.23,
            lambda x: x.get_bottom_temperature_maybe('f'),
            'c',
            'f'
        )

    def test_get_surface_temperature_maybe(self):
        self._test_getter(
            'surface_temperature_c',
            1.23,
            lambda x: x.get_surface_temperature_maybe()
        )

    def test_get_surface_temperature_maybe_empty(self):
        self._test_getter(
            'surface_temperature_c',
            None,
            lambda x: x.get_surface_temperature_maybe()
        )

    def test_get_surface_temperature_maybe_convert(self):
        self._test_getter_convert(
            'surface_temperature_c',
            1.23,
            lambda x: x.get_surface_temperature_maybe('f'),
            'c',
            'f'
        )

    def test_get_depth(self):
        return self._test_getter_convert(
            'depth_m',
            1.23,
            lambda x: x.get_depth('m'),
            'm',
            'm'
        )

    def test_get_depth_convert(self):
        return self._test_getter_convert(
            'depth_m',
            1.23,
            lambda x: x.get_depth('km'),
            'm',
            'km'
        )

    def test_get_distance_fished(self):
        return self._test_getter_convert(
            'distance_fished_km',
            1.23,
            lambda x: x.get_distance_fished('km'),
            'km',
            'km'
        )

    def test_get_distance_fished_convert(self):
        return self._test_getter_convert(
            'distance_fished_km',
            1.23,
            lambda x: x.get_distance_fished('m'),
            'km',
            'm'
        )

    def test_get_net_width(self):
        self._test_getter('net_width_m', 123, lambda x: x.get_net_width())

    def test_get_net_width_convert(self):
        self._test_getter_convert(
            'net_width_m',
            123,
            lambda x: x.get_net_width('km'),
            'm',
            'km'
        )

    def test_get_net_height(self):
        self._test_getter('net_height_m', 123, lambda x: x.get_net_height())

    def test_get_net_height_convert(self):
        self._test_getter_convert(
            'net_height_m',
            123,
            lambda x: x.get_net_height('km'),
            'm',
            'km'
        )

    def test_get_net_width_maybe(self):
        self._test_getter('net_width_m', 123, lambda x: x.get_net_width_maybe())

    def test_get_net_width_maybe_empty(self):
        self._test_getter('net_width_m', None, lambda x: x.get_net_width_maybe())

    def test_get_net_width_maybe_empty_convert(self):
        self._test_getter_convert(
            'net_width_m',
            123,
            lambda x: x.get_net_width_maybe('km'),
            'm',
            'km'
        )

    def test_get_net_height_maybe(self):
        self._test_getter('net_height_m', 123, lambda x: x.get_net_height_maybe())

    def test_get_net_height_maybe_empty(self):
        self._test_getter('net_height_m', None, lambda x: x.get_net_height_maybe())

    def test_get_net_height_maybe_convert(self):
        self._test_getter_convert(
            'net_height_m',
            123,
            lambda x: x.get_net_height_maybe('km'),
            'm',
            'km'
        )

    def test_get_area_swept(self):
        self._test_getter('area_swept_km2', 123, lambda x: x.get_area_swept('km2'))

    def test_get_area_swept_convert(self):
        self._test_getter_convert(
            'area_swept_km2',
            123,
            lambda x: x.get_area_swept('ha'),
            'km2',
            'ha'
        )

    def test_get_duration(self):
        self._test_getter('duration_hr', 1.23, lambda x: x.get_duration('hr'))

    def test_get_duration_convert(self):
        self._test_getter_convert(
            'duration_hr',
            1.23,
            lambda x: x.get_duration('min'),
            'hr',
            'min'
        )

    def test_get_cpue_weight(self):
        self._test_getter('cpue_kgkm2', 1.23, lambda x: x.get_cpue_weight('kg/km2'))

    def test_get_cpue_weight_convert(self):
        self._test_getter_convert(
            'cpue_kgkm2',
            1.23,
            lambda x: x.get_cpue_weight('kg/ha'),
            'kg/km2',
            'kg/ha'
        )

    def test_get_cpue_count(self):
        self._test_getter('cpue_nokm2', 1.23, lambda x: x.get_cpue_count('no/km2'))

    def test_get_cpue_count_convert(self):
        self._test_getter_convert(
            'cpue_nokm2',
            1.23,
            lambda x: x.get_cpue_count('count/ha'),
            'no/km2',
            'count/ha'
        )

    def test_get_weight(self):
        self._test_getter('weight_kg', 1.23, lambda x: x.get_weight('kg'))

    def test_get_weight_convert(self):
        self._test_getter_convert(
            'weight_kg',
            1.23,
            lambda x: x.get_weight('g'),
            'kg',
            'g'
        )

    def test_get_count(self):
        self._test_getter('count', 1123, lambda x: x.get_count())

    def test_get_bottom_temperature(self):
        self._test_getter('bottom_temperature_c', 1.23, lambda x: x.get_bottom_temperature('c'))

    def test_get_bottom_temperature_convert(self):
        self._test_getter_convert(
            'bottom_temperature_c',
            1.23,
            lambda x: x.get_bottom_temperature('f'),
            'c',
            'f'
        )

    def test_get_surface_temperature(self):
        self._test_getter('surface_temperature_c', 1.23, lambda x: x.get_surface_temperature('c'))

    def test_get_surface_temperature_convert(self):
        self._test_getter_convert(
            'surface_temperature_c',
            1.23,
            lambda x: x.get_surface_temperature('f'),
            'c',
            'f'
        )

    def test_is_complete_true(self):
        inner = {}

        for field in afscgap.flat_model.RECORD_REQUIRED_FIELDS:
            inner[field] = True

        inner['complete'] = True

        record = afscgap.flat_model.FlatRecord(inner)
        self.assertTrue(record.is_complete())

    def test_is_complete_false_computed(self):
        inner = {}

        for field in afscgap.flat_model.RECORD_REQUIRED_FIELDS:
            inner[field] = True

        inner['complete'] = True
        inner['count'] = None

        record = afscgap.flat_model.FlatRecord(inner)
        self.assertFalse(record.is_complete())

    def test_is_complete_false_explicit(self):
        inner = {}

        for field in afscgap.flat_model.RECORD_REQUIRED_FIELDS:
            inner[field] = True

        inner['complete'] = False

        record = afscgap.flat_model.FlatRecord(inner)
        self.assertFalse(record.is_complete())

    def _test_getter(self, field, value, accessor):
        self.assertTrue(field in EXPECTED_FIELDS)

        inner = {field: value}
        record = afscgap.flat_model.FlatRecord(inner)
        returned = accessor(record)

        if returned == value:
            self.assertEqual(returned, value)
        else:
            self.assertAlmostEqual(returned, value)

    def _test_getter_convert(self, field, value, accessor, source, destination):
        self.assertTrue(field in EXPECTED_FIELDS)
        inner = {field: value}
        record = afscgap.flat_model.FlatRecord(inner)
        expected = afscgap.convert.convert(value, source, destination)
        self.assertAlmostEqual(accessor(record), expected)

