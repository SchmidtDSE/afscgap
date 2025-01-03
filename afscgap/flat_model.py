"""
Model implementation for prejoined Avro flat files.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import typing

import afscgap.convert
import afscgap.model
import afscgap.param

from afscgap.typesdef import OPT_FLOAT
from afscgap.typesdef import OPT_REQUESTOR
from afscgap.typesdef import OPT_INT
from afscgap.typesdef import OPT_STR

PARAMS_DICT = typing.Dict[str, afscgap.param.Param]
RECORDS = typing.Iterable[afscgap.model.Record]
WARN_FUNCTION = typing.Optional[typing.Callable[[str], None]]

RECORD_REQUIRED_FIELDS = [
    'area_swept_km2',
    'bottom_temperature_c',
    'common_name',
    'complete',
    'count',
    'cpue_kgkm2',
    'cpue_nokm2',
    'curise',
    'date_time',
    'depth_m',
    'distance_fished_km',
    'duration_hr',
    'haul',
    'latitude_dd_end',
    'latitude_dd_start',
    'longitude_dd_end',
    'longitude_dd_start',
    'net_height_m',
    'net_width_m',
    'scientific_name',
    'species_code',
    'srvy',
    'station',
    'stratum',
    'surface_temperature_c',
    'survey',
    'survey_definition_id',
    'taxon_confidence',
    'vessel_id',
    'vessel_name',
    'weight_kg',
    'year'
]


class ExecuteMetaParams:
    """Description of how to execute requests for prejoined Avro flat files.

    Collection of configuration parameters of how to execute requests for pre-joined Avro flat files
    such as changing the server from which to request those files.
    """

    def __init__(self, base_url: str, requestor: OPT_REQUESTOR, limit: OPT_INT,
        filter_incomplete: bool, presence_only: bool, suppress_large_warning: bool,
        warn_func: WARN_FUNCTION):
        """Create a new set of configuration values.

        Args:
            base_url: The URL at which the flat files can be found over HTTPS.
            requestor: A requests-like requestor object to use in executing GET requests or None if
                to use a default.
            limit: The maximum number of records to return or None if all matching records should be
                returned.
            filter_incomplete: Indicate if incomplete records should be filtered out from the
                results set.
            presence_only: Indicate if only presence values are required such that zero catch
                inference records can be ignored.
            suppress_large_warning: Indiciate if the large results set warning should be suppressed,
                False if the user should be warned about downloading a very large dataset or True
                otherwise.
            warn_func: Function to call with a string to emit a warning.
        """
        self._base_url = base_url
        self._requestor = requestor
        self._limit = limit
        self._filter_incomplete = filter_incomplete
        self._presence_only = presence_only
        self._suppress_large_warning = suppress_large_warning
        self._warn_func = warn_func

    def get_base_url(self) -> str:
        """Get the URL at which prejoined flat files can be found.

        Returns:
            The URL at which the flat files can be found over HTTPS.
        """
        return self._base_url

    def get_requestor(self) -> OPT_REQUESTOR:
        """Get the requests-like requestor object with which to retrieve records.

        Returns:
            A requests-like requestor object to use in executing GET requests or None if to use a
            default.
        """
        return self._requestor

    def get_limit(self) -> OPT_INT:
        """Get the maximum number of matching records to return.

        Returns:
            The maximum number of records to return or None if all matching records should be
            returned.
        """
        return self._limit

    def get_filter_incomplete(self) -> bool:
        """Get if "incomplete" records should be filtered out.

        Returns:
            Flag indicating if incomplete records should be filtered out from the results set.
        """
        return self._filter_incomplete

    def get_presence_only(self) -> bool:
        """Determine if zero catch inference records should be included.

        Returns:
            Indicate if only presence values are required such that zero catch inference records can
            be ignored.
        """
        return self._presence_only

    def get_suppress_large_warning(self) -> bool:
        """Determine if the user should see large dataset warnings.

        Returns:
            Indiciate if the large results set warning should be suppressed, False if the user
            should be warned about downloading a very large dataset or True otherwise.
        """
        return self._suppress_large_warning

    def get_warn_func(self) -> WARN_FUNCTION:
        """Get the function with which warnings may be emitted.

        Returns:
            Function to call with a string to emit a warning.
        """
        return self._warn_func


class HaulKey:
    """Record describing the key for a flat file haul.

    Record describing the key for a haul within prejoined flat files which can be used in referring
    to sets of records from a haul (catches) prior to retrieving the collection in its entirety.
    """

    def __init__(self, year: int, survey: str, haul: int):
        """Create a new haul key record.

        Args:
            year: The year of the haul.
            survey: The name of the survey for which the haul was conducted. This should be the full
                name like Gulf of Alaska.
            haul: The haul ID.
        """
        self._year = year
        self._survey = survey
        self._haul = haul

    def get_year(self) -> int:
        """Get the year in which the haul was conducted.

        Returns:
            The year of the haul.
        """
        return self._year

    def get_survey(self) -> str:
        """Get the name of the survey for which this haul was conducted.

        Returns:
            The name of the survey for which the haul was conducted. This should be the full name
            like Gulf of Alaska.
        """
        return self._survey

    def get_haul(self) -> int:
        """Get the ID of the haul.

        Returns:
            The haul ID.
        """
        return self._haul

    def get_key(self) -> str:
        """Get a string uniquely identifying a haul.

        Returns:
            Unique string describing this haul.
        """
        return '%d_%s_%d' % (self._year, self._survey, self._haul)

    def get_path(self) -> str:
        """Get the path at which the flat file for this haul is expected.

        Returns:
            Get the URL at which the joined Avro flat file is expected to be found at the flat file
            server.
        """
        return '/joined/%s.avro' % self.get_key()

    def __hash__(self):
        return hash(self.__repr__())

    def __repr__(self):
        return self.get_key()

    def __eq__(self, other):
        if isinstance(other, HaulKey):
            return self.get_key() == other.get_key()
        else:
            return False

    def __ne__(self, other):
        return (not self.__eq__(other))


HAUL_KEYS = typing.Iterable[HaulKey]


class FlatRecord(afscgap.model.Record):
    """Object describing the contents of a pre-joined flat Avro file."""

    def __init__(self, inner):
        """Create a new object decorating a raw parsed Avro record.

        Args:
            inner: The Avro record to decorate into a FlatRecord object, conforming to the interface
                put forward by afscgap.model.Record.
        """
        self._inner = inner

    def get_year(self) -> float:
        """Get the field labeled as year in the API.

        Returns:
            Year for the survey in which this observation was made or for which
            an inferred zero catch record was generated.
        """
        return self._assert_float(self._inner['year'])

    def get_srvy(self) -> str:
        """Get the field labeled as srvy in the API.

        Returns:
            The name of the survey in which this observation or inference was
            made. NBS (N Bearing Sea), EBS (SE Bearing Sea), BSS (Bearing Sea
            Slope), or GOA (Gulf of Alaska)
        """
        return self._assert_str(self._inner['srvy'])

    def get_survey(self) -> str:
        """Get the field labeled as survey in the API.

        Returns:
            Long form description of the survey in which the observation was
            made or for which an inferred zero catch record was made.
        """
        return self._assert_str(self._inner['survey'])

    def get_survey_id(self) -> float:
        """Get the field labeled as survey_id in the API.

        Returns:
            Unique numeric ID for the survey.
        """
        return self._assert_int(self._inner['survey_definition_id'])

    def get_cruise(self) -> float:
        """Get the field labeled as cruise in the API.

        Returns:
            An ID uniquely identifying the cruise in which the observation or
            inferrence was made. Multiple cruises in a survey.
        """
        return self._assert_int(self._inner['cruise'])

    def get_haul(self) -> float:
        """Get the field labeled as haul in the API.

        Returns:
            An ID uniquely identifying the haul in which this observation or
            inference was made. Multiple hauls per cruises.
        """
        return self._assert_int(self._inner['haul'])

    def get_stratum(self) -> float:
        """Get the field labeled as stratum in the API.

        Returns:
            Unique ID for statistical area / survey combination as described in
            the metadata or 0 if an experimental tow.
        """
        return self._assert_int(self._inner['stratum'])

    def get_station(self) -> str:
        """Get the field labeled as station in the API.

        Returns:
            Station associated with the survey.
        """
        return self._assert_str(self._inner['station'])

    def get_vessel_name(self) -> str:
        """Get the field labeled as vessel_name in the API.

        Returns:
            Unique ID describing the vessel that made this observation or
            inference.
        """
        return self._assert_str(self._inner['vessel_name'])

    def get_vessel_id(self) -> float:
        """Get the field labeled as vessel_id in the API.

        Returns:
            Name of the vessel at the time the observation was made with
            multiple names potentially associated with a vessel ID. May be
            emulated in the case of inferred records
        """
        return self._assert_int(self._inner['vessel_id'])

    def get_date_time(self) -> str:
        """Get the field labeled as date_time in the API.

        Returns:
            The date and time of the haul which has been attempted to be
            transformed to an ISO 8601 string without timezone info. If it
            couldn’t be transformed, the original string is reported.
        """
        return self._assert_str(self._inner['date_time'])

    def get_latitude_start(self, units: str = 'dd') -> float:
        """Get the field labeled as latitude_dd_start in the API.

        Args:
            units: The units to return this value in. Only supported is dd for
                degrees. Deafults to dd.

        Returns:
            Latitude in decimal degrees associated with the haul.
        """
        value = self._assert_float(self._inner['latitude_dd_start'])
        return self._assert_float(afscgap.convert.convert(value, 'dd', units))

    def get_longitude_start(self, units: str = 'dd') -> float:
        """Get the field labeled as longitude_dd_start in the API.

        Args:
            units: The units to return this value in. Only supported is dd for
                degrees. Deafults to dd.

        Returns:
            Longitude in decimal degrees associated with the haul.
        """
        value = self._assert_float(self._inner['longitude_dd_start'])
        return self._assert_float(afscgap.convert.convert(value, 'dd', units))

    def get_latitude(self, units: str = 'dd') -> float:
        """Get midpoint of the haul, approximating deprecated latitude_dd field in the API.

        Args:
            units: The units to return this value in. Only supported is dd for
                degrees. Deafults to dd.

        Returns:
            Latitude in decimal degrees associated with the haul.
        """
        start = self.get_latitude_start()
        end = self.get_latitude_end()
        mid = (start + end) / 2
        return self._assert_float(afscgap.convert.convert(mid, 'dd', units))

    def get_longitude(self, units: str = 'dd') -> float:
        """Get midpoint of the haul, approximating deprecated longitude_dd field in the API.

        Args:
            units: The units to return this value in. Only supported is dd for
                degrees. Deafults to dd.

        Returns:
            Longitude in decimal degrees associated with the haul.
        """
        start = self.get_longitude_start()
        end = self.get_longitude_end()
        mid = (start + end) / 2
        return self._assert_float(afscgap.convert.convert(mid, 'dd', units))

    def get_latitude_end(self, units: str = 'dd') -> float:
        """Get the field labeled as latitude_dd_end in the API.

        Args:
            units: The units to return this value in. Only supported is dd for
                degrees. Deafults to dd.

        Returns:
            Latitude in decimal degrees associated with the haul.
        """
        value = self._assert_float(self._inner['latitude_dd_end'])
        return self._assert_float(afscgap.convert.convert(value, 'dd', units))

    def get_longitude_end(self, units: str = 'dd') -> float:
        """Get the field labeled as longitude_dd_end in the API.

        Args:
            units: The units to return this value in. Only supported is dd for
                degrees. Deafults to dd.

        Returns:
            Longitude in decimal degrees associated with the haul.
        """
        value = self._assert_float(self._inner['longitude_dd_end'])
        return self._assert_float(afscgap.convert.convert(value, 'dd', units))

    def get_species_code(self) -> OPT_FLOAT:
        """Get the field labeled as species_code in the API.

        Returns:
            Unique ID associated with the species observed or for which a zero
            catch record was inferred.
        """
        return self._assert_int_maybe(self._inner['species_code'])

    def get_common_name(self) -> OPT_STR:
        """Get the field labeled as common_name in the API.

        Returns:
            The “common name” associated with the species observed or for which
            a zero catch record was inferred. Example: Pacific glass shrimp.
        """
        return self._assert_str_maybe(self._inner['common_name'])

    def get_scientific_name(self) -> OPT_STR:
        """Get the field labeled as scientific_name in the API.

        Returns:
            The “scientific name” associated with the species observed or for
            which a zero catch record was inferred. Example: Pasiphaea pacifica.
        """
        value = self._inner['scientific_name']
        return self._assert_str_maybe(value)

    def get_taxon_confidence(self) -> OPT_STR:
        """Get the field labeled as taxon_confidence in the API.

        Returns:
            Confidence flag regarding ability to identify species (High,
            Moderate, Low). In practice, this can also be Unassessed.
        """
        return self._assert_str_maybe(self._inner['taxon_confidence'])

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
        value = self._inner['cpue_kgkm2']

        if value is None:
            return None

        return afscgap.convert.convert(value, 'kg/km2', units)

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
        value = self._inner['cpue_nokm2']

        if value is None:
            return None

        return afscgap.convert.convert(value, 'no/km2', units)

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
        value = self._inner['weight_kg']

        if value is None:
            return None

        return afscgap.convert.convert(value, 'kg', units)

    def get_count_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as count in the API.

        Returns:
            Total number of organism individuals in haul. None if could not
            interpret as a float. If an inferred zero catch record, will be
            zero.
        """
        return self._inner['count']

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
        value = self._inner['bottom_temperature_c']

        if value is None:
            return None

        return afscgap.convert.convert(value, 'c', units)

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
        value = self._inner['surface_temperature_c']

        if value is None:
            return None

        return afscgap.convert.convert(value, 'c', units)

    def get_depth(self, units: str = 'm') -> float:
        """Get the field labeled as depth_m in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            Depth of the bottom.
        """
        value = self._assert_float(self._inner['depth_m'])
        return self._assert_float(afscgap.convert.convert(value, 'm', units))

    def get_distance_fished(self, units: str = 'm') -> float:
        """Get the field labeled as distance_fished_km in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            Distance of the net fished.
        """
        value = self._assert_float(self._inner['distance_fished_km'])
        return self._assert_float(afscgap.convert.convert(value, 'km', units))

    def get_net_width(self, units: str = 'm') -> float:
        """Get the field labeled as net_width_m in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            Distance of the net fished after asserting it is given.
        """
        value = self._assert_float(self._inner['net_width_m'])
        return self._assert_float(afscgap.convert.convert(value, 'm', units))

    def get_net_height(self, units: str = 'm') -> float:
        """Get the field labeled as net_height_m in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            Height of the net fished after asserting it is given.
        """
        value = self._assert_float(self._inner['net_height_m'])
        return self._assert_float(afscgap.convert.convert(value, 'm', units))

    def get_net_width_maybe(self, units: str = 'm') -> OPT_FLOAT:
        """Get the field labeled as net_width_m in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            Distance of the net fished or None if not given.
        """
        value = self._inner['net_width_m']

        if value is None:
            return None

        return afscgap.convert.convert(value, 'm', units)

    def get_net_height_maybe(self, units: str = 'm') -> OPT_FLOAT:
        """Get the field labeled as net_height_m in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            Height of the net fished or None if not given.
        """
        value = self._inner['net_height_m']

        if value is None:
            return None

        return afscgap.convert.convert(value, 'm', units)

    def get_area_swept(self, units: str = 'ha') -> float:
        """Get the field labeled as area_swept_ha in the API.

        Args:
            units: The units in which the area should be returned. Options:
                ha, m2, km2. Defaults to ha.

        Returns:
            Area covered by the net while fishing in desired units.
        """
        value = self._assert_float(self._inner['area_swept_km2'])
        return self._assert_float(afscgap.convert.convert(value, 'km2', units))

    def get_duration(self, units: str = 'hr') -> float:
        """Get the field labeled as duration_hr in the API.

        Args:
            units: The units in which the duration should be returned. Options:
                day, hr, min. Defaults to hr.

        Returns:
            Duration of the haul.
        """
        value = self._assert_float(self._inner['duration_hr'])
        return self._assert_float(afscgap.convert.convert(value, 'hr', units))

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
        value = self._assert_float(self._inner['cpue_kgkm2'])
        return self._assert_float(afscgap.convert.convert(value, 'kg/km2', units))

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
        value = self._assert_float(self._inner['cpue_nokm2'])
        return self._assert_float(afscgap.convert.convert(value, 'no/km2', units))

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
        value = self._assert_float(self._inner['weight_kg'])
        return self._assert_float(afscgap.convert.convert(value, 'kg', units))

    def get_count(self) -> float:
        """Get the value of field count with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Total number of organism individuals in haul. Will be zero if a zero
            catch record.
        """
        return self._assert_int(self._inner['count'])

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
        value = self._assert_float(self._inner['bottom_temperature_c'])
        return self._assert_float(afscgap.convert.convert(value, 'c', units))

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
        value = self._assert_float(self._inner['surface_temperature_c'])
        return self._assert_float(afscgap.convert.convert(value, 'c', units))

    def is_complete(self) -> bool:
        """Determine if this record has all of its values filled in.

        Returns:
            True if all optional fields have a parsed value with the expected
            type and false otherwise.
        """
        if not self._inner['complete']:
            return False

        fields_missing = filter(lambda x: self._inner.get(x, None) is None, RECORD_REQUIRED_FIELDS)
        num_missing = sum(map(lambda x: 1, fields_missing))
        return num_missing == 0

    def get_inner(self):
        """Get the raw parsed Avro payload.

        Returns:
            The raw parsed Avro payload.
        """
        return self._inner

    def _assert_float(self, target) -> float:
        assert target is not None
        return float(target)

    def _assert_float_maybe(self, target) -> OPT_FLOAT:
        return None if target is None else float(target)

    def _assert_str(self, target) -> str:
        assert target is not None
        return str(target)

    def _assert_str_maybe(self, target) -> OPT_STR:
        return None if target is None else str(target)

    def _assert_int(self, target) -> int:
        assert target is not None
        return int(target)

    def _assert_int_maybe(self, target) -> OPT_INT:
        return None if target is None else int(target)
