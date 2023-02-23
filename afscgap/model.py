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
import typing

from afscgap.util import OPT_FLOAT
from afscgap.util import OPT_INT

DATE_REGEX = re.compile('(?P<month>\\d{2})\\/(?P<day>\\d{2})\\/' + \
    '(?P<year>\\d{4}) (?P<hours>\\d{2})\\:(?P<minutes>\\d{2})\\:' + \
    '(?P<seconds>\\d{2})')
DATE_TEMPLATE = '%s/%s/%s %s:%s:%s'
ISO_8601_REGEX = re.compile('(?P<year>\\d{4})\\-(?P<month>\\d{2})\\-' + \
    '(?P<day>\\d{2})T(?P<hours>\\d{2})\\:(?P<minutes>\\d{2})\\:' + \
    '(?P<seconds>\\d{2})')
ISO_8601_TEMPLATE = '%s-%s-%sT%s:%s:%s'


class Record:
    """Data structure describing a single record returned by the API."""

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
        area_swept_ha: float, duration_hr: float, tsn: OPT_INT,
        ak_survey_id: int):
        """Create a new record.

        Args:
            year: Year for the survey in which this observation was made.
            srvy: The name of the survey in which this observation was made.
                NBS (N Bearing Sea), EBS (SE Bearing Sea), BSS (Bearing Sea
                Slope), or GOA (Gulf of Alaska)
            survey: Long form description of the survey in which the observation
                was made.
            survey_id: Unique numeric ID for the survey.
            cruise: An ID uniquely identifying the cruise in which the
                observation was made. Multiple cruises in a survey.
            haul: An ID uniquely identifying the haul in which this observation
                was made. Multiple hauls per cruises.
            stratum: Unique ID for statistical area / survey combination as
                described in the metadata or 0 if an experimental tow.
            station: Station associated with the survey.
            vessel_name: Unique ID describing the vessel that made this
                observation. This is left as a string but, in practice, is
                likely numeric.
            vessel_id: Name of the vessel at the time the observation was made
                with multiple names potentially associated with a vessel ID.
            date_time: The date and time of the haul which has been attempted to
                be transformed to an ISO 8601 string without timezone info.
                If it couldn’t be transformed, the original string.
            latitude_dd: Latitude in decimal degrees associated with the haul.
            longitude_dd: Longitude in decimal degrees associated with the haul.
            species_code: Unique ID associated with the species observed.
            common_name: The “common name” associated with the species observed.
            scientific_name: The “scientific name” associated with the species
                observed.
            taxon_confidence: Confidence flag regarding ability to identify
                species (High, Moderate, Low). In practice, this can also be
                Unassessed.
            cpue_kgha: Catch weight divided by net area (kg / hectares) if
                available. None if could not interpret as a float.
            cpue_kgkm2: Catch weight divided by net area (kg / km^2) if
                available. None if could not interpret as a float.
            cpue_kg1000km2: Catch weight divided by net area (kg / km^2 * 1000)
                if available. See metadata. None if could not interpret as a
                float.
            cpue_noha: Catch number divided by net sweep area if available
                (count / hectares). None if could not interpret as a float.
            cpue_nokm2: Catch number divided by net sweep area if available
                (count / km^2). See metadata. None if could not interpret as a
                float.
            cpue_no1000km2: Catch number divided by net sweep area if available
                (count / km^2 * 1000). See metadata. None if could not interpret
                as a float.
            weight_kg: Taxon weight (kg) if available. See metadata. None if
                could not interpret as a float.
            count: Total number of organism individuals in haul. None if could
                not interpret as a float.
            bottom_temperature_c: Bottom temperature associated with observation
                if available in Celsius. None if not given or could not
                interpret as a float.
            surface_temperature_c: Surface temperature associated with
                observation if available in Celsius. None if not given or could
                not interpret as a float.
            depth_m: Depth of the bottom in meters.
            distance_fished_km: Distance of the net fished as km.
            net_width_m: Distance of the net fished as m.
            net_height_m: Height of the net fished as m.
            area_swept_ha: Area covered by the net while fishing in hectares.
            duration_hr: Duration of the haul as number of hours.
            tsn: Taxonomic information system species code.
            ak_survey_id: AK identifier for the survey.
        """
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
        """Get the field labeled as year in the API.

        Returns:
            Year for the survey in which this observation was made.
        """
        return self._year

    def get_srvy(self) -> str:
        """Get the field labeled as srvy in the API.

        Returns:
            The name of the survey in which this observation was made. NBS (N
            Bearing Sea), EBS (SE Bearing Sea), BSS (Bearing Sea Slope), or GOA
            (Gulf of Alaska)
        """
        return self._srvy

    def get_survey(self) -> str:
        """Get the field labeled as survey in the API.

        Returns:
            Long form description of the survey in which the observation was
            made.
        """
        return self._survey

    def get_survey_id(self) -> float:
        """Get the field labeled as survey_id in the API.

        Returns:
            Unique numeric ID for the survey.
        """
        return self._survey_id

    def get_cruise(self) -> float:
        """Get the field labeled as cruise in the API.

        Returns:
            An ID uniquely identifying the cruise in which the observation was
            made. Multiple cruises in a survey.
        """
        return self._cruise

    def get_haul(self) -> float:
        """Get the field labeled as haul in the API.

        Returns:
            An ID uniquely identifying the haul in which this observation was
            made. Multiple hauls per cruises.
        """
        return self._haul

    def get_stratum(self) -> float:
        """Get the field labeled as stratum in the API.

        Returns:
            Unique ID for statistical area / survey combination as described in
            the metadata or 0 if an experimental tow.
        """
        return self._stratum

    def get_station(self) -> str:
        """Get the field labeled as station in the API.

        Returns:
            Station associated with the survey.
        """
        return self._station

    def get_vessel_name(self) -> str:
        """Get the field labeled as vessel_name in the API.

        Returns:
            Unique ID describing the vessel that made this observation. This is
            left as a string but, in practice, is likely numeric.
        """
        return self._vessel_name

    def get_vessel_id(self) -> float:
        """Get the field labeled as vessel_id in the API.

        Returns:
            Name of the vessel at the time the observation was made with
            multiple names potentially associated with a vessel ID.
        """
        return self._vessel_id

    def get_date_time(self) -> str:
        """Get the field labeled as date_time in the API.

        Returns:
            The date and time of the haul which has been attempted to be
            transformed to an ISO 8601 string without timezone info. If it
            couldn’t be transformed, the original string is reported.
        """
        return self._date_time

    def get_latitude_dd(self) -> float:
        """Get the field labeled as latitude_dd in the API.

        Returns:
            Latitude in decimal degrees associated with the haul.
        """
        return self._latitude_dd

    def get_longitude_dd(self) -> float:
        """Get the field labeled as longitude_dd in the API.

        Returns:
            Longitude in decimal degrees associated with the haul.
        """
        return self._longitude_dd

    def get_species_code(self) -> float:
        """Get the field labeled as species_code in the API.

        Returns:
            Unique ID associated with the species observed.
        """
        return self._species_code

    def get_common_name(self) -> str:
        """Get the field labeled as common_name in the API.

        Returns:
            The “common name” associated with the species observed. Example:
            Pacific glass shrimp.
        """
        return self._common_name

    def get_scientific_name(self) -> str:
        """Get the field labeled as scientific_name in the API.

        Returns:
            The “scientific name” associated with the species observed. Example:
            Pasiphaea pacifica.
        """
        return self._scientific_name

    def get_taxon_confidence(self) -> str:
        """Get the field labeled as taxon_confidence in the API.

        Returns:
            Confidence flag regarding ability to identify species (High,
            Moderate, Low). In practice, this can also be Unassessed.
        """
        return self._taxon_confidence

    def get_cpue_kgha_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as cpue_kgha in the API.

        Returns:
            Catch weight divided by net area (kg / hectares) if available. See
            metadata. None if could not interpret as a float.
        """
        return self._cpue_kgha

    def get_cpue_kgkm2_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as cpue_kgkm2 in the API.

        Returns:
            Catch weight divided by net area (kg / km^2) if available. See
            metadata. None if could not interpret as a float.
        """
        return self._cpue_kgkm2

    def get_cpue_kg1000km2_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as cpue_kg1000km2 in the API.

        Returns:
            Catch weight divided by net area (kg / km^2 * 1000) if available.
            See metadata. None if could not interpret as a float.
        """
        return self._cpue_kg1000km2

    def get_cpue_noha_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as cpue_noha in the API.

        Returns:
            Catch number divided by net sweep area if available (count /
            hectares). See metadata. None if could not interpret as a float.
        """
        return self._cpue_noha

    def get_cpue_nokm2_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as cpue_nokm2 in the API.

        Returns:
            Catch number divided by net sweep area if available (count / km^2).
            See metadata. None if could not interpret as a float.
        """
        return self._cpue_nokm2

    def get_cpue_no1000km2_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as cpue_no1000km2 in the API.

        Returns:
            Catch number divided by net sweep area if available (count / km^2 *
            1000). See metadata. None if could not interpret as a float.
        """
        return self._cpue_no1000km2

    def get_weight_kg_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as weight_kg in the API.

        Returns:
            Taxon weight (kg) if available. See metadata. None if could not
            interpret as a float.
        """
        return self._weight_kg

    def get_count_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as count in the API.

        Returns:
            Total number of organism individuals in haul. None if could not
            interpret as a float.
        """
        return self._count

    def get_bottom_temperature_c_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as bottom_temperature_c in the API.

        Returns:
            Bottom temperature associated with observation if available in
            Celsius. None if not given or could not interpret as a float.
        """
        return self._bottom_temperature_c

    def get_surface_temperature_c_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as surface_temperature_c in the API.

        Returns:
            Surface temperature associated with observation if available in
            Celsius. None if not given or could not interpret as a float.
        """
        return self._surface_temperature_c

    def get_depth_m(self) -> float:
        """Get the field labeled as depth_m in the API.

        Returns:
            Depth of the bottom in meters.
        """
        return self._depth_m

    def get_distance_fished_km(self) -> float:
        """Get the field labeled as distance_fished_km in the API.

        Returns:
            Distance of the net fished as km.
        """
        return self._distance_fished_km

    def get_net_width_m(self) -> float:
        """Get the field labeled as net_width_m in the API.

        Returns:
            Distance of the net fished as m.
        """
        return self._net_width_m

    def get_net_height_m(self) -> float:
        """Get the field labeled as net_height_m in the API.

        Returns:
            Height of the net fished as m.
        """
        return self._net_height_m

    def get_area_swept_ha(self) -> float:
        """Get the field labeled as area_swept_ha in the API.

        Returns:
            Area covered by the net while fishing in hectares.
        """
        return self._area_swept_ha

    def get_duration_hr(self) -> float:
        """Get the field labeled as duration_hr in the API.

        Returns:
            Duration of the haul as number of hours.
        """
        return self._duration_hr

    def get_tsn(self) -> int:
        """Get the field labeled as tsn in the API.

        Returns:
            Taxonomic information system species code.
        """
        return self._assert_int_present(self._tsn)

    def get_tsn_maybe(self) -> OPT_INT:
        """Get the field labeled as tsn in the API or None.

        Returns:
            Taxonomic information system species code if it could be parsed as
            an int and None otherwise.
        """
        return self._tsn

    def get_ak_survey_id(self) -> int:
        """Get the field labeled as ak_survey_id in the API.

        Returns:
            AK identifier for the survey.
        """
        return self._ak_survey_id

    def get_cpue_kgha(self) -> float:
        """Get the value of field cpue_kgha with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Catch weight divided by net area (kg / hectares) if available. See
            metadata.
        """
        return self._assert_float_present(self._cpue_kgha)

    def get_cpue_kgkm2(self) -> float:
        """Get the value of field cpue_kgkm2 with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Catch weight divided by net area (kg / km^2) if available. See
            metadata.
        """
        return self._assert_float_present(self._cpue_kgkm2)

    def get_cpue_kg1000km2(self) -> float:
        """Get the value of field cpue_kg1000km2 with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Catch weight divided by net area (kg / km^2 * 1000) if available.
            See metadata.
        """
        return self._assert_float_present(self._cpue_kg1000km2)

    def get_cpue_noha(self) -> float:
        """Get the value of field cpue_noha with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Catch number divided by net sweep area if available (count /
            hectares). See metadata.
        """
        return self._assert_float_present(self._cpue_noha)

    def get_cpue_nokm2(self) -> float:
        """Get the value of field cpue_nokm2 with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Catch number divided by net sweep area if available (count / km^2).
            See metadata.
        """
        return self._assert_float_present(self._cpue_nokm2)

    def get_cpue_no1000km2(self) -> float:
        """Get the value of field cpue_no1000km2 with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Catch number divided by net sweep area if available (count / km^2 *
            1000). See metadata.
        """
        return self._assert_float_present(self._cpue_no1000km2)

    def get_weight_kg(self) -> float:
        """Get the value of field weight_kg with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Taxon weight (kg) if available. See metadata.
        """
        return self._assert_float_present(self._weight_kg)

    def get_count(self) -> float:
        """Get the value of field count with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Total number of organism individuals in haul.
        """
        return self._assert_float_present(self._count)

    def get_bottom_temperature_c(self) -> float:
        """Get the value of field bottom_temperature_c with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Bottom temperature associated with observation if available in
            Celsius.
        """
        return self._assert_float_present(self._bottom_temperature_c)

    def get_surface_temperature_c(self) -> float:
        """Get the value of field surface_temperature_c with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Surface temperature associated with observation if available in
            Celsius. None if not
        """
        return self._assert_float_present(self._surface_temperature_c)

    def is_complete(self) -> bool:
        """Determine if this record has all of its values filled in.

        Returns:
            True if all optional fields have a parsed value with the expected
            type and false otherwise.
        """
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
            self._surface_temperature_c,
            self._tsn
        ]

        has_none = None in optional_fields
        all_fields_present = not has_none
        has_valid_date_time = ISO_8601_REGEX.match(self._date_time) is not None

        return all_fields_present and has_valid_date_time

    def to_dict(self) -> dict:
        """Serialize this Record to a dictionary form.

        Returns:
            Dictionary with field names matching those found in the API results
            with incomplete records having some values as None.
        """
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

    def _assert_float_present(self, target: OPT_FLOAT) -> float:
        assert target is not None
        return target

    def _assert_int_present(self, target: OPT_INT) -> int:
        assert target is not None
        return target


def get_opt_float(target) -> OPT_FLOAT:
    """Attempt to parse a value as a float, returning None if there is an error.

    Args:
        target: The value to try to interpret as a float.

    Returns:
        The value of target as a float or None if there was an issue in parsing
        like that target is None.
    """
    if target:
        try:
            return float(target)
        except ValueError:
            return None
    else:
        return None


def get_opt_int(target) -> OPT_INT:
    """Attempt to parse a value as an int, returning None if there is an error.

    Args:
        target: The value to try to interpret as an int.

    Returns:
        The value of target as an int or None if there was an issue in parsing
        like that target is None.
    """
    if target:
        try:
            return int(target)
        except ValueError:
            return None
    else:
        return None


def convert_from_iso8601(target: str) -> str:
    """Attempt converting an ISO 8601 string to an API-provided datetime.

    Args:
        target: The datetime string to try to interpret.
    Returns:
        The datetime input string as a ISO 8601 string or the original value of
        target if it could not be parsed.
    """
    match = ISO_8601_REGEX.match(target)

    if not match:
        return target

    year = match.group('year')
    month = match.group('month')
    day = match.group('day')
    hours = match.group('hours')
    minutes = match.group('minutes')
    seconds = match.group('seconds')

    return DATE_TEMPLATE % (month, day, year, hours, minutes, seconds)


def convert_to_iso8601(target: str) -> str:
    """Attempt converting an API-provided datetime to ISO 8601.

    Args:
        target: The datetime string to try to interpret.
    Returns:
        The datetime input string as a ISO 8601 string or the original value of
        target if it could not be parsed.
    """
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
    """Parse a record from a returned item dictionary.

    Args:
        target: The dictionary from which values should be read.

    Raises:
        ValueError: Exception raised if a field has an unexpected type or cannot
            be parsed to an expected type.
        KeyError: Exception raised if an expected field is not found.

    Returns:
        Newly parsed record.
    """
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
    date_time = convert_to_iso8601(str(target['date_time']))
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
    count = get_opt_float(target['count'])
    bottom_temperature_c = get_opt_float(target['bottom_temperature_c'])
    surface_temperature_c = get_opt_float(target['surface_temperature_c'])
    depth_m = float(target['depth_m'])
    distance_fished_km = float(target['distance_fished_km'])
    net_width_m = float(target['net_width_m'])
    net_height_m = float(target['net_height_m'])
    area_swept_ha = float(target['area_swept_ha'])
    duration_hr = float(target['duration_hr'])
    tsn = get_opt_int(target['tsn'])
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
    """Object with the results of trying to parse a record from the API.

    Object with the results of trying to parse a record from the API, allowing
    for internal record keeping within the afscgap library. Note that this is
    an internal data structure and not expected to reach client code.
    """

    def __init__(self, raw_record: dict, parsed: typing.Optional[Record]):
        """Create a new record of a parse attempt.

        Args:
            raw_record: Item from the API's JSON response payload that the
                library attempted to parse.
            parsed: The Record read if successful or None if it could not be
                parsed.
        """
        self._raw_record = raw_record
        self._parsed = parsed

    def get_raw_record(self) -> dict:
        """Get the input raw JSON record.

        Returns:
            Item from the API's JSON response payload that the library attempted
            to parse.
        """
        return self._raw_record

    def get_parsed(self) -> typing.Optional[Record]:
        """Get the record that was parsed if successful.

        Returns:
            The Record read if successful or None if it could not be parsed.
        """
        return self._parsed

    def meets_requirements(self, allow_incomplete: bool) -> bool:
        """Determine if this record is "valid" according to the client code.

        Args:
            allow_incomplete: Flag indicating if incomplete records are
                considered valid. If true, incomplete records will be considered
                valid. If false, incomplete records will be considered invalid.
                Incomplete means missing any optional fields or failing to
                achieve an ISO 8601 date_time value.

        Returns:
            True if this record was parsed successfully and meets the
            requirements specified for being considered "valid" per the
            allow_incomplete flag. False otherwise.
        """
        if self._parsed is None:
            return False

        return allow_incomplete or self._parsed.is_complete()


def try_parse(target: dict) -> ParseResult:
    """Attempt parsing a Record from an input item dictionary from the API.

    Params:
        target: The dictionary from which to parse. This should be an item
            from the items array in the returned JSON payload from the API.

    Returns:
        Parse result describing if the dictionary was parsed successfully.
    """
    try:
        return ParseResult(target, parse_record(target))
    except (ValueError, KeyError):
        return ParseResult(target, None)
