"""
Logic for representing and working with data returned by the AFSC GAP API.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.txt.
"""
from afscgap.util import OPT_FLOAT
from afscgap.util import OPT_INT

OPT_RECORD = 'typing.Optional[Record]'


class HaulKeyable:

    def get_srvy(self) -> str:
        raise NotImplementedError('Use implementor.')

    def get_year(self) -> float:
        raise NotImplementedError('Use implementor.')

    def get_vessel_id(self) -> float:
        raise NotImplementedError('Use implementor.')

    def get_cruise(self) -> float:
        raise NotImplementedError('Use implementor.')

    def get_haul(self) -> float:
        raise NotImplementedError('Use implementor.')


class Record(HaulKeyable):
    """Interface describing a single record.

    Interface describing a single record of an observtion. Note that, in
    practice, this "observation" can be a presence obervation where a species
    was found or an "absence" / "zero catch" observation where a sepcies was
    not observed in a haul.
    """

    def get_year(self) -> float:
        """Get the field labeled as year in the API.

        Returns:
            Year for the survey in which this observation was made.
        """
        raise NotImplementedError('Use implementor.')

    def get_srvy(self) -> str:
        """Get the field labeled as srvy in the API.

        Returns:
            The name of the survey in which this observation was made. NBS (N
            Bearing Sea), EBS (SE Bearing Sea), BSS (Bearing Sea Slope), or GOA
            (Gulf of Alaska)
        """
        raise NotImplementedError('Use implementor.')

    def get_survey(self) -> str:
        """Get the field labeled as survey in the API.

        Returns:
            Long form description of the survey in which the observation was
            made.
        """
        raise NotImplementedError('Use implementor.')

    def get_survey_id(self) -> float:
        """Get the field labeled as survey_id in the API.

        Returns:
            Unique numeric ID for the survey.
        """
        raise NotImplementedError('Use implementor.')

    def get_cruise(self) -> float:
        """Get the field labeled as cruise in the API.

        Returns:
            An ID uniquely identifying the cruise in which the observation was
            made. Multiple cruises in a survey.
        """
        raise NotImplementedError('Use implementor.')

    def get_haul(self) -> float:
        """Get the field labeled as haul in the API.

        Returns:
            An ID uniquely identifying the haul in which this observation was
            made. Multiple hauls per cruises.
        """
        raise NotImplementedError('Use implementor.')

    def get_stratum(self) -> float:
        """Get the field labeled as stratum in the API.

        Returns:
            Unique ID for statistical area / survey combination as described in
            the metadata or 0 if an experimental tow.
        """
        raise NotImplementedError('Use implementor.')

    def get_station(self) -> str:
        """Get the field labeled as station in the API.

        Returns:
            Station associated with the survey.
        """
        raise NotImplementedError('Use implementor.')

    def get_vessel_name(self) -> str:
        """Get the field labeled as vessel_name in the API.

        Returns:
            Unique ID describing the vessel that made this observation. This is
            left as a string but, in practice, is likely numeric.
        """
        raise NotImplementedError('Use implementor.')

    def get_vessel_id(self) -> float:
        """Get the field labeled as vessel_id in the API.

        Returns:
            Name of the vessel at the time the observation was made with
            multiple names potentially associated with a vessel ID.
        """
        raise NotImplementedError('Use implementor.')

    def get_date_time(self) -> str:
        """Get the field labeled as date_time in the API.

        Returns:
            The date and time of the haul which has been attempted to be
            transformed to an ISO 8601 string without timezone info. If it
            couldn’t be transformed, the original string is reported.
        """
        raise NotImplementedError('Use implementor.')

    def get_latitude_dd(self) -> float:
        """Get the field labeled as latitude_dd in the API.

        Returns:
            Latitude in decimal degrees associated with the haul.
        """
        raise NotImplementedError('Use implementor.')

    def get_longitude_dd(self) -> float:
        """Get the field labeled as longitude_dd in the API.

        Returns:
            Longitude in decimal degrees associated with the haul.
        """
        raise NotImplementedError('Use implementor.')

    def get_species_code(self) -> float:
        """Get the field labeled as species_code in the API.

        Returns:
            Unique ID associated with the species observed.
        """
        raise NotImplementedError('Use implementor.')

    def get_common_name(self) -> str:
        """Get the field labeled as common_name in the API.

        Returns:
            The “common name” associated with the species observed. Example:
            Pacific glass shrimp.
        """
        raise NotImplementedError('Use implementor.')

    def get_scientific_name(self) -> str:
        """Get the field labeled as scientific_name in the API.

        Returns:
            The “scientific name” associated with the species observed. Example:
            Pasiphaea pacifica.
        """
        raise NotImplementedError('Use implementor.')

    def get_taxon_confidence(self) -> str:
        """Get the field labeled as taxon_confidence in the API.

        Returns:
            Confidence flag regarding ability to identify species (High,
            Moderate, Low). In practice, this can also be Unassessed.
        """
        raise NotImplementedError('Use implementor.')

    def get_cpue_kgha_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as cpue_kgha in the API.

        Returns:
            Catch weight divided by net area (kg / hectares) if available. See
            metadata. None if could not interpret as a float.
        """
        raise NotImplementedError('Use implementor.')

    def get_cpue_kgkm2_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as cpue_kgkm2 in the API.

        Returns:
            Catch weight divided by net area (kg / km^2) if available. See
            metadata. None if could not interpret as a float.
        """
        raise NotImplementedError('Use implementor.')

    def get_cpue_kg1000km2_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as cpue_kg1000km2 in the API.

        Returns:
            Catch weight divided by net area (kg / km^2 * 1000) if available.
            See metadata. None if could not interpret as a float.
        """
        raise NotImplementedError('Use implementor.')

    def get_cpue_noha_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as cpue_noha in the API.

        Returns:
            Catch number divided by net sweep area if available (count /
            hectares). See metadata. None if could not interpret as a float.
        """
        raise NotImplementedError('Use implementor.')

    def get_cpue_nokm2_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as cpue_nokm2 in the API.

        Returns:
            Catch number divided by net sweep area if available (count / km^2).
            See metadata. None if could not interpret as a float.
        """
        raise NotImplementedError('Use implementor.')

    def get_cpue_no1000km2_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as cpue_no1000km2 in the API.

        Returns:
            Catch number divided by net sweep area if available (count / km^2 *
            1000). See metadata. None if could not interpret as a float.
        """
        raise NotImplementedError('Use implementor.')

    def get_weight_kg_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as weight_kg in the API.

        Returns:
            Taxon weight (kg) if available. See metadata. None if could not
            interpret as a float.
        """
        raise NotImplementedError('Use implementor.')

    def get_count_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as count in the API.

        Returns:
            Total number of organism individuals in haul. None if could not
            interpret as a float.
        """
        raise NotImplementedError('Use implementor.')

    def get_bottom_temperature_c_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as bottom_temperature_c in the API.

        Returns:
            Bottom temperature associated with observation if available in
            Celsius. None if not given or could not interpret as a float.
        """
        raise NotImplementedError('Use implementor.')

    def get_surface_temperature_c_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as surface_temperature_c in the API.

        Returns:
            Surface temperature associated with observation if available in
            Celsius. None if not given or could not interpret as a float.
        """
        raise NotImplementedError('Use implementor.')

    def get_depth_m(self) -> float:
        """Get the field labeled as depth_m in the API.

        Returns:
            Depth of the bottom in meters.
        """
        raise NotImplementedError('Use implementor.')

    def get_distance_fished_km(self) -> float:
        """Get the field labeled as distance_fished_km in the API.

        Returns:
            Distance of the net fished as km.
        """
        raise NotImplementedError('Use implementor.')

    def get_net_width_m(self) -> float:
        """Get the field labeled as net_width_m in the API.

        Returns:
            Distance of the net fished as m.
        """
        raise NotImplementedError('Use implementor.')

    def get_net_height_m(self) -> float:
        """Get the field labeled as net_height_m in the API.

        Returns:
            Height of the net fished as m.
        """
        raise NotImplementedError('Use implementor.')

    def get_area_swept_ha(self) -> float:
        """Get the field labeled as area_swept_ha in the API.

        Returns:
            Area covered by the net while fishing in hectares.
        """
        raise NotImplementedError('Use implementor.')

    def get_duration_hr(self) -> float:
        """Get the field labeled as duration_hr in the API.

        Returns:
            Duration of the haul as number of hours.
        """
        raise NotImplementedError('Use implementor.')

    def get_tsn(self) -> int:
        """Get the field labeled as tsn in the API.

        Returns:
            Taxonomic information system species code.
        """
        raise NotImplementedError('Use implementor.')

    def get_tsn_maybe(self) -> OPT_INT:
        """Get the field labeled as tsn in the API or None.

        Returns:
            Taxonomic information system species code if it could be parsed as
            an int and None otherwise.
        """
        raise NotImplementedError('Use implementor.')

    def get_ak_survey_id(self) -> int:
        """Get the field labeled as ak_survey_id in the API.

        Returns:
            AK identifier for the survey.
        """
        raise NotImplementedError('Use implementor.')

    def get_ak_survey_id_maybe(self) -> OPT_INT:
        """Get the field labeled as ak_survey_id in the API.

        Returns:
            AK identifier for the survey or None if not given.
        """
        raise NotImplementedError('Use implementor.')

    def get_cpue_kgha(self) -> float:
        """Get the value of field cpue_kgha with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Catch weight divided by net area (kg / hectares) if available. See
            metadata.
        """
        raise NotImplementedError('Use implementor.')

    def get_cpue_kgkm2(self) -> float:
        """Get the value of field cpue_kgkm2 with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Catch weight divided by net area (kg / km^2) if available. See
            metadata.
        """
        raise NotImplementedError('Use implementor.')

    def get_cpue_kg1000km2(self) -> float:
        """Get the value of field cpue_kg1000km2 with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Catch weight divided by net area (kg / km^2 * 1000) if available.
            See metadata.
        """
        raise NotImplementedError('Use implementor.')

    def get_cpue_noha(self) -> float:
        """Get the value of field cpue_noha with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Catch number divided by net sweep area if available (count /
            hectares). See metadata.
        """
        raise NotImplementedError('Use implementor.')

    def get_cpue_nokm2(self) -> float:
        """Get the value of field cpue_nokm2 with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Catch number divided by net sweep area if available (count / km^2).
            See metadata.
        """
        raise NotImplementedError('Use implementor.')

    def get_cpue_no1000km2(self) -> float:
        """Get the value of field cpue_no1000km2 with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Catch number divided by net sweep area if available (count / km^2 *
            1000). See metadata.
        """
        raise NotImplementedError('Use implementor.')

    def get_weight_kg(self) -> float:
        """Get the value of field weight_kg with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Taxon weight (kg) if available. See metadata.
        """
        raise NotImplementedError('Use implementor.')

    def get_count(self) -> float:
        """Get the value of field count with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Total number of organism individuals in haul.
        """
        raise NotImplementedError('Use implementor.')

    def get_bottom_temperature_c(self) -> float:
        """Get the value of field bottom_temperature_c with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Bottom temperature associated with observation if available in
            Celsius.
        """
        raise NotImplementedError('Use implementor.')

    def get_surface_temperature_c(self) -> float:
        """Get the value of field surface_temperature_c with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Surface temperature associated with observation if available in
            Celsius. None if not
        """
        raise NotImplementedError('Use implementor.')

    def is_complete(self) -> bool:
        """Determine if this record has all of its values filled in.

        Returns:
            True if all optional fields have a parsed value with the expected
            type and false otherwise.
        """
        raise NotImplementedError('Use implementor.')

    def to_dict(self) -> dict:
        """Serialize this Record to a dictionary form.

        Returns:
            Dictionary with field names matching those found in the API results
            with incomplete records having some values as None.
        """
        raise NotImplementedError('Use implementor.')


class Haul(HaulKeyable):

    def __init__(self, srvy: str, survey: str, survey_id: float, cruise: float,
        haul: float, stratum: float, station: str, vessel_name: str,
        vessel_id: float, date_time: str, latitude_dd: float,
        longitude_dd: float, bottom_temperature_c: OPT_FLOAT,
        surface_temperature_c: OPT_FLOAT, depth_m: float,
        distance_fished_km: float, net_width_m: float, net_height_m: float,
        area_swept_ha: float, duration_hr: float):
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
        self._bottom_temperature_c = bottom_temperature_c
        self._surface_temperature_c = surface_temperature_c
        self._depth_m = depth_m
        self._distance_fished_km = distance_fished_km
        self._net_width_m = net_width_m
        self._net_height_m = net_height_m
        self._area_swept_ha = area_swept_ha
        self._duration_hr = duration_hr

    def get_year(self) -> float:
        """Get year inferred from get_date_time().

        Returns:
            Year for the survey in which this observation was made.
        """
        return int(self.get_date_time().split('-')[0])

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
            Long form description of the survey in which the haul was made.
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
            An ID uniquely identifying the cruise in which the haul was made.
            Multiple cruises in a survey.
        """
        return self._cruise

    def get_haul(self) -> float:
        """Get the field labeled as haul in the API.

        Returns:
            An ID uniquely identifying the haul. Multiple hauls per cruises.
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
            Unique ID describing the vessel that made this haul. Note this is
            left as a string but, in practice, is likely numeric.
        """
        return self._vessel_name

    def get_vessel_id(self) -> float:
        """Get the field labeled as vessel_id in the API.

        Returns:
            Name of the vessel at the time the haul was made. Note that
            multiple names are potentially associated with a vessel ID.
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

    def get_bottom_temperature_c_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as bottom_temperature_c in the API.

        Returns:
            Bottom temperature associated with haul if available in
            Celsius. None if not given or could not interpret as a float.
        """
        return self._bottom_temperature_c

    def get_surface_temperature_c_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as surface_temperature_c in the API.

        Returns:
            Surface temperature associated with haul if available in
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

    def get_bottom_temperature_c(self) -> float:
        """Get the value of field bottom_temperature_c with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Bottom temperature associated with haul if available in Celsius.
        """
        return assert_float_present(self._bottom_temperature_c)

    def get_surface_temperature_c(self) -> float:
        """Get the value of field surface_temperature_c with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Surface temperature associated with haul if available in Celsius.
        """
        return assert_float_present(self._surface_temperature_c)

    def is_complete(self) -> bool:
        bottom_valid = self._bottom_temperature_c is not None
        surface_valid = self._surface_temperature_c is not None
        return bottom_valid and surface_valid

    def to_dict(self) -> dict:
        return {
            'year': self.get_year(),
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
            'bottom_temperature_c': self._bottom_temperature_c,
            'surface_temperature_c': self._surface_temperature_c,
            'depth_m': self._depth_m,
            'distance_fished_km': self._distance_fished_km,
            'net_width_m': self._net_width_m,
            'net_height_m': self._net_height_m,
            'area_swept_ha': self._area_swept_ha,
            'duration_hr': self._duration_hr
        }


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


def assert_float_present(target: OPT_FLOAT) -> float:
    assert target is not None
    return target


def assert_int_present(target: OPT_INT) -> int:
    assert target is not None
    return target
