"""
Definition of common library data with its structures and interfaces.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
from afscgap.typesdef import OPT_FLOAT
from afscgap.typesdef import OPT_STR

OPT_RECORD = 'typing.Optional[Record]'


class Record:
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

    def get_latitude_start(self, units: str = 'dd') -> float:
        """Get the field labeled as latitude_dd_start in the API.

        Args:
            units: The units to return this value in. Only supported is dd for
                degrees. Deafults to dd.

        Returns:
            Latitude in decimal degrees associated with the haul.
        """
        raise NotImplementedError('Use implementor.')

    def get_longitude_start(self, units: str = 'dd') -> float:
        """Get the field labeled as longitude_dd_start in the API.

        Args:
            units: The units to return this value in. Only supported is dd for
                degrees. Deafults to dd.

        Returns:
            Longitude in decimal degrees associated with the haul.
        """
        raise NotImplementedError('Use implementor.')

    def get_latitude(self, units: str = 'dd') -> float:
        """Get midpoint of the haul, approximating deprecated latitude_dd field in the API.

        Args:
            units: The units to return this value in. Only supported is dd for
                degrees. Deafults to dd.

        Returns:
            Latitude in decimal degrees associated with the haul.
        """
        raise NotImplementedError('Use implementor.')

    def get_longitude(self, units: str = 'dd') -> float:
        """Get midpoint of the haul, approximating deprecated longitude_dd field in the API.

        Args:
            units: The units to return this value in. Only supported is dd for
                degrees. Deafults to dd.

        Returns:
            Longitude in decimal degrees associated with the haul.
        """
        raise NotImplementedError('Use implementor.')

    def get_latitude_end(self, units: str = 'dd') -> float:
        """Get the field labeled as latitude_dd_end in the API.

        Args:
            units: The units to return this value in. Only supported is dd for
                degrees. Deafults to dd.

        Returns:
            Latitude in decimal degrees associated with the haul.
        """
        raise NotImplementedError('Use implementor.')

    def get_longitude_end(self, units: str = 'dd') -> float:
        """Get the field labeled as longitude_dd_end in the API.

        Args:
            units: The units to return this value in. Only supported is dd for
                degrees. Deafults to dd.

        Returns:
            Longitude in decimal degrees associated with the haul.
        """
        raise NotImplementedError('Use implementor.')

    def get_species_code(self) -> OPT_FLOAT:
        """Get the field labeled as species_code in the API.

        Returns:
            Unique ID associated with the species observed or for which a zero
            catch record was inferred.
        """
        raise NotImplementedError('Use implementor.')

    def get_common_name(self) -> OPT_STR:
        """Get the field labeled as common_name in the API.

        Returns:
            The “common name” associated with the species observed or for which
            a zero catch record was inferred. Example: Pacific glass shrimp.
        """
        raise NotImplementedError('Use implementor.')

    def get_scientific_name(self) -> OPT_STR:
        """Get the field labeled as scientific_name in the API.

        Returns:
            The “scientific name” associated with the species observed or for
            which a zero catch record was inferred. Example: Pasiphaea pacifica.
        """
        raise NotImplementedError('Use implementor.')

    def get_taxon_confidence(self) -> OPT_STR:
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
            'duration_hr': self.get_duration(units='hr')
        }
