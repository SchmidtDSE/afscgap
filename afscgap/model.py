"""
Definition of common library data with its structures and interfaces.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
from afscgap.typesdef import OPT_FLOAT
from afscgap.typesdef import OPT_INT

OPT_RECORD = 'typing.Optional[Record]'


class HaulKeyable:
    """Interface for objects which can be associated to a specific haul.

    Interface for objects which have enough information to be associated to a
    specific haul but may not be the only data associated with that haul.
    """

    def get_srvy(self) -> str:
        """Get the field labeled as srvy in the API.

        Returns:
            The name of the survey with which this data point is associated.
            Examples: NBS (N Bearing Sea), EBS (SE Bearing Sea), BSS (Bearing
            Sea Slope), or GOA (Gulf of Alaska)
        """
        raise NotImplementedError('Use implementor.')

    def get_year(self) -> float:
        """Get the year in which or for which this data point was made.

        Returns:
            The four digit year like 2023 with which this data point is
            associated.
        """
        raise NotImplementedError('Use implementor.')

    def get_vessel_id(self) -> float:
        """Get the ID of the vessel with which this data point is associated.

        Returns:
            Name of the vessel at the time the observation or inference was made
            with multiple names potentially associated with a vessel ID.
        """
        raise NotImplementedError('Use implementor.')

    def get_cruise(self) -> float:
        """Get the ID of the cruise with which this data point is associated.

        Returns:
            An ID uniquely identifying the cruise in which or for which this
            data point was made. Multiple cruises in a survey.
        """
        raise NotImplementedError('Use implementor.')

    def get_haul(self) -> float:
        """Get the ID of the haul with which this data point is associated.

        Returns:
            Unique ID for the haul with which this data point is associated.
        """
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
            Year for the survey in which this observation was made or for which
            an inferred zero catch record was generated.
        """
        raise NotImplementedError('Use implementor.')

    def get_srvy(self) -> str:
        """Get the field labeled as srvy in the API.

        Returns:
            The name of the survey in which this observation or inference was
            made. NBS (N Bearing Sea), EBS (SE Bearing Sea), BSS (Bearing Sea
            Slope), or GOA (Gulf of Alaska)
        """
        raise NotImplementedError('Use implementor.')

    def get_survey(self) -> str:
        """Get the field labeled as survey in the API.

        Returns:
            Long form description of the survey in which the observation was
            made or for which an inferred zero catch record was made.
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
            An ID uniquely identifying the cruise in which the observation or
            inferrence was made. Multiple cruises in a survey.
        """
        raise NotImplementedError('Use implementor.')

    def get_haul(self) -> float:
        """Get the field labeled as haul in the API.

        Returns:
            An ID uniquely identifying the haul in which this observation or
            inference was made. Multiple hauls per cruises.
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
            Unique ID describing the vessel that made this observation or
            inference.
        """
        raise NotImplementedError('Use implementor.')

    def get_vessel_id(self) -> float:
        """Get the field labeled as vessel_id in the API.

        Returns:
            Name of the vessel at the time the observation was made with
            multiple names potentially associated with a vessel ID. May be
            emulated in the case of inferred records
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

    def get_latitude(self, units: str = 'dd') -> float:
        """Get the field labeled as latitude_dd in the API.

        Args:
            units: The units to return this value in. Only supported is dd for
                degrees. Deafults to dd.

        Returns:
            Latitude in decimal degrees associated with the haul.
        """
        raise NotImplementedError('Use implementor.')

    def get_longitude(self, units: str = 'dd') -> float:
        """Get the field labeled as longitude_dd in the API.

        Args:
            units: The units to return this value in. Only supported is dd for
                degrees. Deafults to dd.

        Returns:
            Longitude in decimal degrees associated with the haul.
        """
        raise NotImplementedError('Use implementor.')

    def get_species_code(self) -> float:
        """Get the field labeled as species_code in the API.

        Returns:
            Unique ID associated with the species observed or for which a zero
            catch record was inferred.
        """
        raise NotImplementedError('Use implementor.')

    def get_common_name(self) -> str:
        """Get the field labeled as common_name in the API.

        Returns:
            The “common name” associated with the species observed or for which
            a zero catch record was inferred. Example: Pacific glass shrimp.
        """
        raise NotImplementedError('Use implementor.')

    def get_scientific_name(self) -> str:
        """Get the field labeled as scientific_name in the API.

        Returns:
            The “scientific name” associated with the species observed or for
            which a zero catch record was inferred. Example: Pasiphaea pacifica.
        """
        raise NotImplementedError('Use implementor.')

    def get_taxon_confidence(self) -> str:
        """Get the field labeled as taxon_confidence in the API.

        Returns:
            Confidence flag regarding ability to identify species (High,
            Moderate, Low). In practice, this can also be Unassessed.
        """
        raise NotImplementedError('Use implementor.')

    def get_cpue_weight_maybe(self, units: str = 'kg/ha') -> OPT_FLOAT:
        """Get a field labeled as cpue_* in the API.

        Args:
            units: The desired units for the catch per unit effort. Options:
                kg/ha, kg/km2, kg1000/km2. Defaults to kg/ha.

        Returns:
            Catch weight divided by net area (in given units) if available. See
            metadata. None if could not interpret as a float. If an inferred
            zero catch record, will be zero.
        """
        raise NotImplementedError('Use implementor.')

    def get_cpue_count_maybe(self, units: str = 'count/ha') -> OPT_FLOAT:
        """Get the field labeled as cpue_* in the API.

        Get the catch per unit effort from the record with one of the following
        units: kg/ha, kg/km2, kg1000/km2.

        Args:
            units: The desired units for the catch per unit effort. Options:
                count/ha, count/km2, and count1000/km2. Defaults to count/ha.

        Returns:
            Catch weight divided by net area (in given units) if available. See
            metadata. None if could not interpret as a float. If an inferred
            zero catch record, will be zero.
        """
        raise NotImplementedError('Use implementor.')

    def get_weight_maybe(self, units: str = 'kg') -> OPT_FLOAT:
        """Get the field labeled as weight_kg in the API.

        Args:
            units: The units in which the weight should be returned. Options are
                g, kg for grams and kilograms respectively. Deafults to kg.

        Returns:
            Taxon weight if available. See metadata. None if could not
            interpret as a float. If an inferred zero catch record, will be
            zero.
        """
        raise NotImplementedError('Use implementor.')

    def get_count_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as count in the API.

        Returns:
            Total number of organism individuals in haul. None if could not
            interpret as a float. If an inferred zero catch record, will be
            zero.
        """
        raise NotImplementedError('Use implementor.')

    def get_bottom_temperature_maybe(self, units: str = 'c') -> OPT_FLOAT:
        """Get the field labeled as bottom_temperature_c in the API.

        Args:
            units: The units in which the temperature should be returned.
                Options: c or f for Celcius and Fahrenheit respectively.
                Defaults to c.

        Returns:
            Bottom temperature associated with observation / inferrence if
            available in desired units. None if not given or could not interpret
            as a float.
        """
        raise NotImplementedError('Use implementor.')

    def get_surface_temperature_maybe(self, units: str = 'c') -> OPT_FLOAT:
        """Get the field labeled as surface_temperature_c in the API.

        Args:
            units: The units in which the temperature should be returned.
                Options: c or f for Celcius and Fahrenheit respectively.
                Defaults to c.

        Returns:
            Surface temperature associated with observation / inferrence if
            available. None if not given or could not interpret as a float.
        """
        raise NotImplementedError('Use implementor.')

    def get_depth(self, units: str = 'm') -> float:
        """Get the field labeled as depth_m in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            Depth of the bottom.
        """
        raise NotImplementedError('Use implementor.')

    def get_distance_fished(self, units: str = 'm') -> float:
        """Get the field labeled as distance_fished_km in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            Distance of the net fished.
        """
        raise NotImplementedError('Use implementor.')

    def get_net_width(self, units: str = 'm') -> float:
        """Get the field labeled as net_width_m in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            Distance of the net fished after asserting it is given.
        """
        raise NotImplementedError('Use implementor.')

    def get_net_height(self, units: str = 'm') -> float:
        """Get the field labeled as net_height_m in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            Height of the net fished after asserting it is given.
        """
        raise NotImplementedError('Use implementor.')

    def get_net_width_maybe(self, units: str = 'm') -> OPT_FLOAT:
        """Get the field labeled as net_width_m in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            Distance of the net fished or None if not given.
        """
        raise NotImplementedError('Use implementor.')

    def get_net_height_maybe(self, units: str = 'm') -> OPT_FLOAT:
        """Get the field labeled as net_height_m in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            Height of the net fished or None if not given.
        """
        raise NotImplementedError('Use implementor.')

    def get_area_swept(self, units: str = 'ha') -> float:
        """Get the field labeled as area_swept_ha in the API.

        Args:
            units: The units in which the area should be returned. Options:
                ha, m2, km2. Defaults to ha.

        Returns:
            Area covered by the net while fishing in desired units.
        """
        raise NotImplementedError('Use implementor.')

    def get_duration(self, units: str = 'hr') -> float:
        """Get the field labeled as duration_hr in the API.

        Args:
            units: The units in which the duration should be returned. Options:
                day, hr, min. Defaults to hr.

        Returns:
            Duration of the haul.
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

    def get_cpue_weight(self, units: str = 'kg/ha') -> float:
        """Get the value of field cpue_kgha with validity assert.

        Args:
            units: The desired units for the catch per unit effort. Options:
                kg/ha, kg/km2, kg1000/km2. Defaults to kg/ha.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Catch weight divided by net area (kg / hectares) if available. See
            metadata. Will be zero if a zero catch record.
        """
        raise NotImplementedError('Use implementor.')

    def get_cpue_count(self, units: str = 'count/ha') -> float:
        """Get the value of field cpue_noha with validity assert.

        Args:
            units: The desired units for the catch per unit effort. Options:
                count/ha, count/km2, and count1000/km2. Defaults to count/ha.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Catch number divided by net sweep area if available (count /
            hectares). See metadata. Will be zero if a zero catch record.
        """
        raise NotImplementedError('Use implementor.')

    def get_weight(self, units: str = 'kg') -> float:
        """Get the value of field weight_kg with validity assert.

        Args:
            units: The units in which the weight should be returned. Options are
                g, kg for grams and kilograms respectively. Deafults to kg.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Taxon weight (kg) if available. See metadata. Will be zero if a zero
            catch record.
        """
        raise NotImplementedError('Use implementor.')

    def get_count(self) -> float:
        """Get the value of field count with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Total number of organism individuals in haul. Will be zero if a zero
            catch record.
        """
        raise NotImplementedError('Use implementor.')

    def get_bottom_temperature(self, units='c') -> float:
        """Get the value of field bottom_temperature_c with validity assert.

        Args:
            units: The units in which the temperature should be returned.
                Options: c or f for Celcius and Fahrenheit respectively.
                Defaults to c.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Bottom temperature associated with observation / inferrence if
            available.
        """
        raise NotImplementedError('Use implementor.')

    def get_surface_temperature(self, units='c') -> float:
        """Get the value of field surface_temperature_c with validity assert.

        Args:
            units: The units in which the temperature should be returned.
                Options: c or f for Celcius and Fahrenheit respectively.
                Defaults to c.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Surface temperature associated with observation / inferrence if
            available.
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

        Serialize this Record to a dictionary form, including only field names
        that would be found on records returned from the API service.

        Returns:
            Dictionary with field names matching those found in the API results
            with incomplete records having some values as None.
        """
        return {
            'year': self.get_year(),
            'srvy': self.get_srvy(),
            'survey': self.get_survey(),
            'survey_id': self.get_survey_id(),
            'cruise': self.get_cruise(),
            'haul': self.get_haul(),
            'stratum': self.get_stratum(),
            'station': self.get_station(),
            'vessel_name': self.get_vessel_name(),
            'vessel_id': self.get_vessel_id(),
            'date_time': self.get_date_time(),
            'latitude_dd': self.get_latitude(),
            'longitude_dd': self.get_longitude(),
            'species_code': self.get_species_code(),
            'common_name': self.get_common_name(),
            'scientific_name': self.get_scientific_name(),
            'taxon_confidence': self.get_taxon_confidence(),
            'cpue_kgha': self.get_cpue_weight_maybe(units='kg/ha'),
            'cpue_kgkm2': self.get_cpue_weight_maybe(units='kg/km2'),
            'cpue_kg1000km2': self.get_cpue_weight_maybe(units='kg1000/km2'),
            'cpue_noha': self.get_cpue_count_maybe(units='count/ha'),
            'cpue_nokm2': self.get_cpue_count_maybe(units='count/km2'),
            'cpue_no1000km2': self.get_cpue_count_maybe(units='count1000/km2'),
            'weight_kg': self.get_weight(units='kg'),
            'count': self.get_count(),
            'bottom_temperature_c': self.get_bottom_temperature_maybe(
                units='c'
            ),
            'surface_temperature_c': self.get_surface_temperature_maybe(
                units='c'
            ),
            'depth_m': self.get_depth(units='m'),
            'distance_fished_km': self.get_distance_fished(units='km'),
            'net_width_m': self.get_net_width(units='m'),
            'net_height_m': self.get_net_height(units='m'),
            'area_swept_ha': self.get_area_swept(units='ha'),
            'duration_hr': self.get_duration(units='hr'),
            'tsn': self.get_tsn_maybe(),
            'ak_survey_id': self.get_ak_survey_id()
        }


class Haul(HaulKeyable):
    """Metadata about a haul performed in a survey.

    Metadata about a haul performed in a survey which is typically maintained
    for record inferrence and which does not typically leave the internals of
    the afscgap library.
    """

    def __init__(self, srvy: str, survey: str, survey_id: float, cruise: float,
        haul: float, stratum: float, station: str, vessel_name: str,
        vessel_id: float, date_time: str, latitude_dd: float,
        longitude_dd: float, bottom_temperature_c: OPT_FLOAT,
        surface_temperature_c: OPT_FLOAT, depth_m: float,
        distance_fished_km: float, net_width_m: OPT_FLOAT,
        net_height_m: OPT_FLOAT, area_swept_ha: float, duration_hr: float):
        """Create a new Haul record.

        Args:
            srvy: The name of the survey in which this observation was made
                like NBS.
            survey: Long form description of the survey in which the haul was
                made like Gulf of Alaska.
            survey_id: Unique numeric ID for the survey.
            cruise: An ID uniquely identifying the cruise in which the haul was
                made.
            haul: An ID uniquely identifying the haul.
            stratum: Unique ID for statistical area / survey combination as
                described in the metadata or 0 if an experimental tow.
            station: Station associated with the survey.
            vessel_name: Unique ID describing the vessel that made this haul.
                Note this is left as a string but, in practice, is likely
                numeric.
            vessel_id: ID of the vessel at the time the haul was made.
            date_time: The date and time of the haul which has been attempted to
                be transformed to an ISO 8601 string without timezone info.
            latitude_dd: Latitude in decimal degrees associated with the haul.
            longitude_dd: Longitude in decimal degrees associated with the haul.
            bottom_temperature_c: Bottom temperature associated with haul if
                available in Celsius.
            surface_temperature_c: Surface temperature associated with haul if
                available in Celsius.
            depth_m: Depth of the bottom in meters.
            distance_fished_km: Distance of the net fished as km.
            net_width_m: Distance of the net fished as m or None if not given.
            net_height_m: Height of the net fished as m or None if not given.
            area_swept_ha: Area covered by the net while fishing in hectares.
            duration_hr: Duration of the haul as number of hours.
        """
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
        """Get the field labeled as Srvy in the dataset.

        Returns:
            The name of the survey in which this observation was made. NBS (N
            Bearing Sea), EBS (SE Bearing Sea), BSS (Bearing Sea Slope), or GOA
            (Gulf of Alaska)
        """
        return self._srvy

    def get_survey(self) -> str:
        """Get the field labeled as Survey in the dataset.

        Returns:
            Long form description of the survey in which the haul was made.
        """
        return self._survey

    def get_survey_id(self) -> float:
        """Get the field labeled as Survey Id in the dataset.

        Returns:
            Unique numeric ID for the survey.
        """
        return self._survey_id

    def get_cruise(self) -> float:
        """Get the field labeled as Cruise in the dataset.

        Returns:
            An ID uniquely identifying the cruise in which the haul was made.
            Multiple cruises in a survey.
        """
        return self._cruise

    def get_haul(self) -> float:
        """Get the field labeled as Haul in the dataset.

        Returns:
            An ID uniquely identifying the haul. Multiple hauls per cruises.
        """
        return self._haul

    def get_stratum(self) -> float:
        """Get the field labeled as Stratum in the dataset.

        Returns:
            Unique ID for statistical area / survey combination as described in
            the metadata or 0 if an experimental tow.
        """
        return self._stratum

    def get_station(self) -> str:
        """Get the field labeled as Station in the dataset.

        Returns:
            Station associated with the survey.
        """
        return self._station

    def get_vessel_name(self) -> str:
        """Get the field labeled as Vessel Name in the dataset.

        Returns:
            Unique ID describing the vessel that made this haul. Note this is
            left as a string but, in practice, is likely numeric.
        """
        return self._vessel_name

    def get_vessel_id(self) -> float:
        """Get the field labeled as Vessel ID in the dataset.

        Returns:
            ID of the vessel at the time the haul was made.
        """
        return self._vessel_id

    def get_date_time(self) -> str:
        """Get the field labeled as Date Time in the dataset.

        Returns:
            The date and time of the haul which has been attempted to be
            transformed to an ISO 8601 string without timezone info. If it
            couldn’t be transformed, the original string is reported.
        """
        return self._date_time

    def get_latitude_dd(self) -> float:
        """Get the field labeled as Latitude Dd in the dataset.

        Returns:
            Latitude in decimal degrees associated with the haul.
        """
        return self._latitude_dd

    def get_longitude_dd(self) -> float:
        """Get the field labeled as Longitude Dd in the dataset.

        Returns:
            Longitude in decimal degrees associated with the haul.
        """
        return self._longitude_dd

    def get_bottom_temperature_c_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as Bottom Temperature C in the dataset.

        Returns:
            Bottom temperature associated with haul if available in
            Celsius. None if not given or could not interpret as a float.
        """
        return self._bottom_temperature_c

    def get_surface_temperature_c_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as Surface Temperature C in the dataset.

        Returns:

            Surface temperature associated with haul if available in
            Celsius. None if not given or could not interpret as a float.
        """
        return self._surface_temperature_c

    def get_depth_m(self) -> float:
        """Get the field labeled as Depth N in the dataset.

        Returns:
            Depth of the bottom in meters.
        """
        return self._depth_m

    def get_distance_fished_km(self) -> float:
        """Get the field labeled as Distance Fished Km in the dataset.

        Returns:
            Distance of the net fished as km.
        """
        return self._distance_fished_km

    def get_net_width_m_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as Net Width M in the dataset.

        Returns:
            Distance of the net fished as m if given or None.
        """
        return self._net_width_m

    def get_net_height_m_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as Net Height M in the dataset.

        Returns:
            Height of the net fished as m if given or None.
        """
        return self._net_height_m

    def get_net_width_m(self) -> float:
        """Get the field labeled as Net Width M in the dataset.

        Returns:
            Distance of the net fished as m after asserting it is given.
        """
        return assert_float_present(self._net_width_m)

    def get_net_height_m(self) -> float:
        """Get the field labeled as Net Height M in the dataset.

        Returns:
            Height of the net fished as m after asserting it is given.
        """
        return assert_float_present(self._net_height_m)

    def get_area_swept_ha(self) -> float:
        """Get the field labeled as Area Swept Ha in the dataset.

        Returns:
            Area covered by the net while fishing in hectares.
        """
        return self._area_swept_ha

    def get_duration_hr(self) -> float:
        """Get the field labeled as Duration Hr in the dataset.

        Returns:
            Duration of the haul as number of hours.
        """
        return self._duration_hr

    def get_bottom_temperature_c(self) -> float:
        """Get the value of field Bottom Temperature C with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Bottom temperature associated with haul if available in Celsius.
        """
        return assert_float_present(self._bottom_temperature_c)

    def get_surface_temperature_c(self) -> float:
        """Get the value of field Surface Temperature C with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Surface temperature associated with haul if available in Celsius.
        """
        return assert_float_present(self._surface_temperature_c)

    def is_complete(self) -> bool:
        """Determine if this Haul has all optional fields set.

        Returns:
            True if all optional fields are non-None and false otherwise.
        """
        bottom_valid = self._bottom_temperature_c is not None
        surface_valid = self._surface_temperature_c is not None
        return bottom_valid and surface_valid

    def to_dict(self) -> dict:
        """Convert this object to a primitive dictionary representation.

        Returns:
            Dictionary representation which may have Nones.
        """
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


class SpeciesRecord:
    """Record of a species found within a dataset.

    Largely used for internal record keeping inside the library, this record of
    a species found within a dataset houses basic species metadata. Note that
    this is not expected to leave the internals of the library.
    """

    def __init__(self, scientific_name: str, common_name: str,
        species_code: float, tsn: OPT_INT):
        """Create a new record of a species found in a datset.

        Args:
            scientific_name: The “scientific name” associated with the species
                observed.
            common_name: The “common name” associated with the species observed.
            species_code: Unique ID associated with the species observed.
            tsn: Taxonomic information system species code.
        """
        self._scientific_name = scientific_name
        self._common_name = common_name
        self._species_code = species_code
        self._tsn = tsn

    def get_scientific_name(self) -> str:
        """Get the “scientific name” associated with the species.

        Returns:
            The “scientific name” associated with the species.
        """
        return self._scientific_name

    def get_common_name(self) -> str:
        """Get the “common name” associated with the species observed.

        Returns:
            The “common name” associated with the species observed.
        """
        return self._common_name

    def get_species_code(self) -> float:
        """Get the unique ID associated with the species observed.

        Returns:
            Unique ID associated with the species observed.
        """
        return self._species_code

    def get_tsn(self) -> OPT_INT:
        """Get the taxonomic information system species code.

        Returns:
            Taxonomic information system species code.
        """
        return self._tsn


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
    """Assert that a value is non-None before returning that value.

    Args:
        target: The value to check if not None.

    Raises:
        AssertionError: Raised if target is None.

    Returns:
        The value of target if not None.
    """
    assert target is not None
    return target


def assert_int_present(target: OPT_INT) -> int:
    """Assert that a value is non-None before returning that value.

    Args:
        target: The value to check if not None.

    Raises:
        AssertionError: Raised if target is None.

    Returns:
        The value of target if not None.
    """
    assert target is not None
    return target
