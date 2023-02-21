"""
Logic for representing and working with data returned by the AFSC GAP API.

(c) 2023 The Eric and Wendy Schmidt Center for Data Science and the Environment
at UC Berkeley.

This file is part of afscgap.

Afscgap is free software: you can redistribute it and/or modify it under the
terms of the GNU Lesser General Public License as published by the Free Software 
Foundation, either version 3 of the License, or (at your option) any later
version.

Afscgap is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along 
with Afscgap. If not, see <https://www.gnu.org/licenses/>. 
"""
import re

from afscgap.util import OPT_FLOAT

# pylint: disable=C0301
DATE_REGEX = re.compile('(?P<month>\\d{2})\\/(?P<day>\\d{2})\\/(?P<year>\\d{4}) (?P<hours>\\d{2})\\:(?P<minutes>\\d{2})\\:(?P<seconds>\\d{2})')
ISO_8601_REGEX = re.compile('^\\d{4}\\-\\d{2}\\-\\d{2}T\\d{2}\\:\\d{2}\\:\\d{2}$')
ISO_8601_TEMPLATE = '%s-%s-%sT%s:%s:%s'


class Record:

    def __init__(self, year: float, srvy: str, survey: str, survey_id: float,
        cruise: float, haul: float, stratum: float, station: str,
        vessel_name: str, vessel_id: float, date_time: str, latitude_dd: float,
        longitude_dd: float, species_code: float, common_name: str,
        scientific_name: str, taxon_confidence: str, cpue_kgha: OPT_FLOAT,
        cpue_kgkm2: OPT_FLOAT, cpue_kg1000km2: OPT_FLOAT, cpue_noha: OPT_FLOAT,
        cpue_nokm2: OPT_FLOAT, cpue_no1000km2: OPT_FLOAT, weight_kg: OPT_FLOAT,
        count: OPT_FLOAT, bottom_temperature_c: OPT_FLOAT,
        surface_temperature_c: OPT_FLOAT, depth_m: float,
        distance_fished_km: float, net_width_m: float, net_height_m: float,
        area_swept_ha: float, duration_hr: float, tsn: int,
        ak_survey_id: int):
        self._year = year
        self._srvy = srvy
        self._survey = survey
        self._survey_id = survey_id
        self._cruise = cruise
        self._haul = haul
        self._stratum = stratum
        self._station = station
        self._vessel_name = vessel_name
        self._vessel_id = vessel_id
        self._date_time = date_time
        self._latitude_dd = latitude_dd
        self._longitude_dd = longitude_dd
        self._species_code = species_code
        self._common_name = common_name
        self._scientific_name = scientific_name
        self._taxon_confidence = taxon_confidence
        self._cpue_kgha = cpue_kgha
        self._cpue_kgkm2 = cpue_kgkm2
        self._cpue_kg1000km2 = cpue_kg1000km2
        self._cpue_noha = cpue_noha
        self._cpue_nokm2 = cpue_nokm2
        self._cpue_no1000km2 = cpue_no1000km2
        self._weight_kg = weight_kg
        self._count = count
        self._bottom_temperature_c = bottom_temperature_c
        self._surface_temperature_c = surface_temperature_c
        self._depth_m = depth_m
        self._distance_fished_km = distance_fished_km
        self._net_width_m = net_width_m
        self._net_height_m = net_height_m
        self._area_swept_ha = area_swept_ha
        self._duration_hr = duration_hr
        self._tsn = tsn
        self._ak_survey_id = ak_survey_id

    def get_year(self) -> float:
        return self._year

    def get_srvy(self) -> str:
        return self._srvy

    def get_survey(self) -> str:
        return self._survey

    def get_survey_id(self) -> float:
        return self._survey_id

    def get_cruise(self) -> float:
        return self._cruise

    def get_haul(self) -> float:
        return self._haul

    def get_stratum(self) -> float:
        return self._stratum

    def get_station(self) -> str:
        return self._station

    def get_vessel_name(self) -> str:
        return self._vessel_name

    def get_vessel_id(self) -> float:
        return self._vessel_id

    def get_date_time(self) -> str:
        return self._date_time

    def get_latitude_dd(self) -> float:
        return self._latitude_dd

    def get_longitude_dd(self) -> float:
        return self._longitude_dd

    def get_species_code(self) -> float:
        return self._species_code

    def get_common_name(self) -> str:
        return self._common_name

    def get_scientific_name(self) -> str:
        return self._scientific_name

    def get_taxon_confidence(self) -> str:
        return self._taxon_confidence

    def get_cpue_kgha_maybe(self) -> OPT_FLOAT:
        return self._cpue_kgha

    def get_cpue_kgkm2_maybe(self) -> OPT_FLOAT:
        return self._cpue_kgkm2

    def get_cpue_kg1000km2_maybe(self) -> OPT_FLOAT:
        return self._cpue_kg1000km2

    def get_cpue_noha_maybe(self) -> OPT_FLOAT:
        return self._cpue_noha

    def get_cpue_nokm2_maybe(self) -> OPT_FLOAT:
        return self._cpue_nokm2

    def get_cpue_no1000km2_maybe(self) -> OPT_FLOAT:
        return self._cpue_no1000km2

    def get_weight_kg_maybe(self) -> OPT_FLOAT:
        return self._weight_kg

    def get_count_maybe(self) -> OPT_FLOAT:
        return self._count

    def get_bottom_temperature_c_maybe(self) -> OPT_FLOAT:
        return self._bottom_temperature_c

    def get_surface_temperature_c_maybe(self) -> OPT_FLOAT:
        return self._surface_temperature_c

    def get_cpue_kgha(self) -> float:
        return self._assert_present(self._cpue_kgha)

    def get_cpue_kgkm2(self) -> float:
        return self._assert_present(self._cpue_kgkm2)

    def get_cpue_kg1000km2(self) -> float:
        return self._assert_present(self._cpue_kg1000km2)

    def get_cpue_noha(self) -> float:
        return self._assert_present(self._cpue_noha)

    def get_cpue_nokm2(self) -> float:
        return self._assert_present(self._cpue_nokm2)

    def get_cpue_no1000km2(self) -> float:
        return self._assert_present(self._cpue_no1000km2)

    def get_weight_kg(self) -> float:
        return self._assert_present(self._weight_kg)

    def get_count(self) -> float:
        return self._assert_present(self._count)

    def get_bottom_temperature_c(self) -> float:
        return self._assert_present(self._bottom_temperature_c)

    def get_surface_temperature_c(self) -> float:
        return self._assert_present(self._surface_temperature_c)

    def get_depth_m(self) -> float:
        return self._depth_m

    def get_distance_fished_km(self) -> float:
        return self._distance_fished_km

    def get_net_width_m(self) -> float:
        return self._net_width_m

    def get_net_height_m(self) -> float:
        return self._net_height_m

    def get_area_swept_ha(self) -> float:
        return self._area_swept_ha

    def get_duration_hr(self) -> float:
        return self._duration_hr

    def get_tsn(self) -> int:
        return self._tsn

    def get_ak_survey_id(self) -> int:
        return self._ak_survey_id

    def is_complete(self) -> bool:
        optional_fields = [
            self._cpue_kgha,
            self._cpue_kgkm2,
            self._cpue_kg1000km2,
            self._cpue_noha,
            self._cpue_nokm2,
            self._cpue_no1000km2,
            self._weight_kg,
            self._count,
            self._bottom_temperature_c,
            self._surface_temperature_c
        ]
        
        has_none = None in optional_fields
        all_fields_present = not has_none
        has_valid_date_time = ISO_8601_REGEX.match(self._date_time) is not None

        return all_fields_present and has_valid_date_time

    def to_dict(self) -> dict:
        return {
            'year': self._year,
            'srvy': self._srvy,
            'survey': self._survey,
            'survey_id': self._survey_id,
            'cruise': self._cruise,
            'haul': self._haul,
            'stratum': self._stratum,
            'station': self._station,
            'vessel_name': self._vessel_name,
            'vessel_id': self._vessel_id,
            'date_time': self._date_time,
            'latitude_dd': self._latitude_dd,
            'longitude_dd': self._longitude_dd,
            'species_code': self._species_code,
            'common_name': self._common_name,
            'scientific_name': self._scientific_name,
            'taxon_confidence': self._taxon_confidence,
            'cpue_kgha': self._cpue_kgha,
            'cpue_kgkm2': self._cpue_kgkm2,
            'cpue_kg1000km2': self._cpue_kg1000km2,
            'cpue_noha': self._cpue_noha,
            'cpue_nokm2': self._cpue_nokm2,
            'cpue_no1000km2': self._cpue_no1000km2,
            'weight_kg': self._weight_kg,
            'count': self._count,
            'bottom_temperature_c': self._bottom_temperature_c,
            'surface_temperature_c': self._surface_temperature_c,
            'depth_m': self._depth_m,
            'distance_fished_km': self._distance_fished_km,
            'net_width_m': self._net_width_m,
            'net_height_m': self._net_height_m,
            'area_swept_ha': self._area_swept_ha,
            'duration_hr': self._duration_hr,
            'tsn': self._tsn,
            'ak_survey_id': self._ak_survey_id,
        }

    def _assert_present(self, target: OPT_FLOAT) -> float:
        assert target is not None
        return target


def get_opt_float(t_maybearget) -> OPT_FLOAT:
    if target:
        try:
            return float(target)
        except ValueError:
            return None
    else:
        return None


def parse_datetime(target: str) -> str:
    match = DATE_REGEX.match(target)

    if not match:
        return target

    year = match.group('year')
    month = match.group('month')
    day = match.group('day')
    hours = match.group('hours')
    minutes = match.group('minutes')
    seconds = match.group('seconds')

    return ISO_8601_TEMPLATE % (year, month, day, hours, minutes, seconds)


def parse_record(target: dict) -> Record:
    year = float(target['year'])
    srvy = str(target['srvy'])
    survey = str(target['survey'])
    survey_id = float(target['survey_id'])
    cruise = float(target['cruise'])
    haul = float(target['haul'])
    stratum = float(target['stratum'])
    station = str(target['station'])
    vessel_name = str(target['vessel_name'])
    vessel_id = float(target['vessel_id'])
    date_time = parse_datetime(str(target['date_time']))
    latitude_dd = float(target['latitude_dd'])
    longitude_dd = float(target['longitude_dd'])
    species_code = float(target['species_code'])
    common_name = str(target['common_name'])
    scientific_name = str(target['scientific_name'])
    taxon_confidence = str(target['taxon_confidence'])
    cpue_kgha = get_opt_float(target['cpue_kgha'])
    cpue_kgkm2 = get_opt_float(target['cpue_kgkm2'])
    cpue_kg1000km2 = get_opt_float(target['cpue_kg1000km2'])
    cpue_noha = get_opt_float(target['cpue_noha'])
    cpue_nokm2 = get_opt_float(target['cpue_nokm2'])
    cpue_no1000km2 = get_opt_float(target['cpue_no1000km2'])
    weight_kg = get_opt_float(target['weight_kg'])
    count = float(target['count'])
    bottom_temperature_c = float(target['bottom_temperature_c'])
    surface_temperature_c = float(target['surface_temperature_c'])
    depth_m = float(target['depth_m'])
    distance_fished_km = float(target['distance_fished_km'])
    net_width_m = float(target['net_width_m'])
    net_height_m = float(target['net_height_m'])
    area_swept_ha = float(target['area_swept_ha'])
    duration_hr = float(target['duration_hr'])
    tsn = int(target['tsn'])
    ak_survey_id = int(target['ak_survey_id'])

    return Record(
        year,
        srvy,
        survey,
        survey_id,
        cruise,
        haul,
        stratum,
        station,
        vessel_name,
        vessel_id,
        date_time,
        latitude_dd,
        longitude_dd,
        species_code,
        common_name,
        scientific_name,
        taxon_confidence,
        cpue_kgha,
        cpue_kgkm2,
        cpue_kg1000km2,
        cpue_noha,
        cpue_nokm2,
        cpue_no1000km2,
        weight_kg,
        count,
        bottom_temperature_c,
        surface_temperature_c,
        depth_m,
        distance_fished_km,
        net_width_m,
        net_height_m,
        area_swept_ha,
        duration_hr,
        tsn,
        ak_survey_id
    )


class ParseResult:

    def __init__(self, raw_record: dict, parsed: typing.Optional[Record]):
        self._raw_record = raw_record
        self._parsed = parsed

    def get_raw_record(self) -> dict:
        return self._raw_record

    def get_parsed(self) -> typing.Optional[Record]:
        return self._parsed_record

    def meets_requirements(self, allow_incomplete: bool) -> bool:
        if self._parsed_record is None:
            return False

        return record.is_complete() or allow_incomplete


def try_parse(target: dict) -> ParseResult:
    try:
        return ParseResult(target, parse_record(target))
    except ValueError, KeyError:
        return ParseResult(target, None)
