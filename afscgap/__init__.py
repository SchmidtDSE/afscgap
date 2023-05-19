"""Library which allows for Pythonic access to the interacting with AFSC GAP.

This library supports Pythonic utilization of the API for the Ground
Fish Assessment Program (GAP), a dataset produced by the Resource Assessment
and Conservation Engineering (RACE) Division of the Alaska Fisheries Science
Center (AFSC) as part of the National Oceanic and Atmospheric Administration
(NOAA Fisheries). Note that this is a community-provided library and is not
officially endorsed by NOAA.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import typing
import warnings

import afscgap.client
import afscgap.inference
import afscgap.model

from afscgap.typesdef import FLOAT_PARAM
from afscgap.typesdef import INT_PARAM
from afscgap.typesdef import STR_PARAM

from afscgap.typesdef import OPT_FLOAT
from afscgap.typesdef import OPT_INT
from afscgap.typesdef import OPT_STR
from afscgap.typesdef import OPT_REQUESTOR

from afscgap.inference import OPT_HAUL_LIST

WARN_FUNCTION = typing.Optional[typing.Callable[[str], None]]

LARGE_WARNING = ' '.join([
    'Your query may return a very large amount of records.',
    'Be sure to interact with results in a memory efficient way.'
])


class Query:
    """Entrypoint for the AFSC GAP Python library.

    Facade for executing queries against AFSC GAP and builder to create those
    queries.
    """

    def __init__(self, base_url: OPT_STR = None, hauls_url: OPT_STR = None,
        requestor: OPT_REQUESTOR = None):
        """Create a new Query.

        Args:
            base_url: The URL at which the API can be found. If None, will use
                default (offical URL at time of release). See
                afscgap.client.DEFAULT_URL.
            hauls_url: The URL at which the flat file with hauls metadata can be
                found or None if a default should be used. Defaults to None.
            requestor: Strategy to use for making HTTP requests. If None, will
                use a default as defined by afscgap.client.Cursor.
        """
        # URLs for data
        self._base_url = base_url
        self._hauls_url = hauls_url
        self._requestor = requestor

        # Filter parameters
        self._year: FLOAT_PARAM = None
        self._srvy: STR_PARAM = None
        self._survey: STR_PARAM = None
        self._survey_id: FLOAT_PARAM = None
        self._cruise: FLOAT_PARAM = None
        self._haul: FLOAT_PARAM = None
        self._stratum: FLOAT_PARAM = None
        self._station: STR_PARAM = None
        self._vessel_name: STR_PARAM = None
        self._vessel_id: FLOAT_PARAM = None
        self._date_time: STR_PARAM = None
        self._latitude_dd: FLOAT_PARAM = None
        self._longitude_dd: FLOAT_PARAM = None
        self._species_code: FLOAT_PARAM = None
        self._common_name: STR_PARAM = None
        self._scientific_name: STR_PARAM = None
        self._taxon_confidence: STR_PARAM = None
        self._cpue_kgha: FLOAT_PARAM = None
        self._cpue_kgkm2: FLOAT_PARAM = None
        self._cpue_kg1000km2: FLOAT_PARAM = None
        self._cpue_noha: FLOAT_PARAM = None
        self._cpue_nokm2: FLOAT_PARAM = None
        self._cpue_no1000km2: FLOAT_PARAM = None
        self._weight_kg: FLOAT_PARAM = None
        self._count: FLOAT_PARAM = None
        self._bottom_temperature_c: FLOAT_PARAM = None
        self._surface_temperature_c: FLOAT_PARAM = None
        self._depth_m: FLOAT_PARAM = None
        self._distance_fished_km: FLOAT_PARAM = None
        self._net_width_m: FLOAT_PARAM = None
        self._net_height_m: FLOAT_PARAM = None
        self._area_swept_ha: FLOAT_PARAM = None
        self._duration_hr: FLOAT_PARAM = None
        self._tsn: INT_PARAM = None
        self._ak_survey_id: INT_PARAM = None

        # Query pararmeters
        self._limit: OPT_INT = None
        self._start_offset: OPT_INT = None
        self._filter_incomplete: bool = False
        self._presence_only: bool = True
        self._suppress_large_warning: bool = False
        self._warn_function: WARN_FUNCTION = None
        self._hauls_prefetch: OPT_HAUL_LIST = None

    def filter_year(self, eq: FLOAT_PARAM = None, min_val: OPT_FLOAT = None,
        max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on year for the survey in which this observation was made.

        Filter on year for the survey in which this observation was made,
        ovewritting all prior year filters on this Query if one was previously
        set.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            This object for chaining if desired.
        """
        self._year = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_srvy(self, eq: STR_PARAM = None, min_val: OPT_STR = None,
        max_val: OPT_STR = None) -> 'Query':
        """Filter on haul survey short name.

        Filter on the short name of the survey in which this observation was
        made. Pass None if no filter should be applied. Defaults to None. Note
        that common values include: NBS (N Bearing Sea), EBS (SE Bearing Sea),
        BSS (Bearing Sea Slope), GOA (Gulf of Alaska), and AI (Aleutian
        Islands). Overwrites all prior srvy filters if set on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            This object for chaining if desired.
        """
        self._srvy = self._create_str_param(eq, min_val, max_val)
        return self

    def filter_survey(self, eq: STR_PARAM = None, min_val: OPT_STR = None,
        max_val: OPT_STR = None) -> 'Query':
        """Filter on survey long name.

        Filter on long form description of the survey in which the observation
        was made. Overwrites all prior survey filters if set on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            This object for chaining if desired.
        """
        self._survey = self._create_str_param(eq, min_val, max_val)
        return self

    def filter_survey_id(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on unique numeric ID for the survey.

        Filter on unique numeric ID for the survey, overwritting prior survey ID
        filters if set on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            This object for chaining if desired.
        """
        self._survey_id = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_cruise(self, eq: FLOAT_PARAM = None, min_val: OPT_FLOAT = None,
        max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on cruise ID.

        Filter on an ID uniquely identifying the cruise in which the observation
        was made. Overwrites all prior cruise filters on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            This object for chaining if desired.
        """
        self._cruise = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_haul(self, eq: FLOAT_PARAM = None, min_val: OPT_FLOAT = None,
        max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on haul identifier.

        Filter on an ID uniquely identifying the haul in which this observation
        was made. Overwrites all prior haul filters on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            This object for chaining if desired.
        """
        self._haul = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_stratum(self, eq: FLOAT_PARAM = None, min_val: OPT_FLOAT = None,
        max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on unique ID for statistical area / survey combination.

        Filter on unique ID for statistical area / survey combination,
        overwritting all prior stratum filters on Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            This object for chaining if desired.
        """
        self._stratum = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_station(self, eq: STR_PARAM = None, min_val: OPT_STR = None,
        max_val: OPT_STR = None) -> 'Query':
        """Filter on station associated with the survey.

        Filter on station associated with the survey, overwritting all prior
        station filters on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            This object for chaining if desired.
        """
        self._station = self._create_str_param(eq, min_val, max_val)
        return self

    def filter_vessel_name(self, eq: STR_PARAM = None,
        min_val: OPT_STR = None, max_val: OPT_STR = None) -> 'Query':
        """Filter on unique ID describing the vessel that made this observation.

        Filter on unique ID describing the vessel that made this observation,
        overwritting all prior vessel name filters on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            This object for chaining if desired.
        """
        self._vessel_name = self._create_str_param(eq, min_val, max_val)
        return self

    def filter_vessel_id(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on name of the vessel at the time the observation was made.

        Filter on name of the vessel at the time the observation was made,
        overwritting all prior vessel ID filters on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            This object for chaining if desired.
        """
        self._vessel_id = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_date_time(self, eq: STR_PARAM = None, min_val: OPT_STR = None,
        max_val: OPT_STR = None) -> 'Query':
        """Filter on the date and time of the haul.

        Filter on the date and time of the haul as an ISO 8601 string. If given
        an ISO 8601 string, will afscgap.convert from ISO 8601 to the API
        datetime string format. Similarly, if given a dictionary, all values
        matching an ISO 8601 string will be afscgap.converted to the API
        datetime string format. Overwrites all prior date time filters on
        this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            This object for chaining if desired.
        """
        self._date_time = self._create_str_param(eq, min_val, max_val)
        return self

    def filter_latitude(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'dd') -> 'Query':
        """Filter on latitude in decimal degrees associated with the haul.

        Filter on latitude in decimal degrees associated with the haul,
        overwritting all prior latitude filters on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units in which the filter values are provided. Currently
                only dd supported. Ignored if given eq value containing ORDS
                query.

        Returns:
            This object for chaining if desired.
        """
        self._latitude_dd = self._create_float_param(
            afscgap.convert.unconvert_degrees(eq, units),
            afscgap.convert.unconvert_degrees(min_val, units),
            afscgap.convert.unconvert_degrees(max_val, units)
        )
        return self

    def filter_longitude(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'dd') -> 'Query':
        """Filter on longitude in decimal degrees associated with the haul.

        Filter on longitude in decimal degrees associated with the haul,
        overwritting all prior longitude filters on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units in which the filter values are provided. Currently
                only dd supported.

        Returns:
            This object for chaining if desired.
        """
        self._longitude_dd = self._create_float_param(
            afscgap.convert.unconvert_degrees(eq, units),
            afscgap.convert.unconvert_degrees(min_val, units),
            afscgap.convert.unconvert_degrees(max_val, units)
        )
        return self

    def filter_species_code(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on unique ID associated with the species observed.

        Filter on unique ID associated with the species observed, overwritting
        all prior species code filters on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            This object for chaining if desired.
        """
        self._species_code = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_common_name(self, eq: STR_PARAM = None, min_val: OPT_STR = None,
        max_val: OPT_STR = None) -> 'Query':
        """Filter on the "common name" associated with the species observed.

        Filter on the "common name" associated with the species observed,
        overwritting all prior common name filters on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            This object for chaining if desired.
        """
        self._common_name = self._create_str_param(eq, min_val, max_val)
        return self

    def filter_scientific_name(self, eq: STR_PARAM = None,
        min_val: OPT_STR = None, max_val: OPT_STR = None) -> 'Query':
        """Filter on the "scientific name" associated with the species observed.

        Filter on the "scientific name" associated with the species observed,
        overwritting all prior scientific name filters on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            This object for chaining if desired.
        """
        self._scientific_name = self._create_str_param(eq, min_val, max_val)
        return self

    def filter_taxon_confidence(self, eq: STR_PARAM = None,
        min_val: OPT_STR = None, max_val: OPT_STR = None) -> 'Query':
        """Filter on confidence flag regarding ability to identify species.

        Filter on confidence flag regarding ability to identify species,
        overwritting all taxon confidence filters on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            This object for chaining if desired.
        """
        self._taxon_confidence = self._create_str_param(eq, min_val, max_val)
        return self

    def filter_cpue_weight(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'kg/ha') -> 'Query':
        """Filter on catch per unit effort.

        Filter on catch per unit effort as weight divided by net area if
        available. Overwrites all prior CPUE weight filters applied to this
        Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units for the catch per unit effort provided. Options:
                kg/ha, kg/km2, kg1000/km2. Defaults to kg/ha. Ignored if given
                eq value containing ORDS query.

        Returns:
            This object for chaining if desired.
        """
        param = self._create_float_param(eq, min_val, max_val)

        self._cpue_kgha = None
        self._cpue_kgkm2 = None
        self._cpue_kg1000km2 = None

        if units == 'kg/ha':
            self._cpue_kgha = param
        elif units == 'kg/km2':
            self._cpue_kgkm2 = param
        elif units == 'kg1000/km2':
            self._cpue_kg1000km2 = param
        else:
            raise RuntimeError('Unrecognized units ' + units)

        return self

    def filter_cpue_count(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'count/ha') -> 'Query':
        """Filter catch per unit effort as count over area in hectares.

        Filter on catch number divided by net sweep area if available (count /
        hectares). Overwrites all prior CPUE count filters applied to this
        Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units for the given catch per unit effort. Options:
                count/ha, count/km2, and count1000/km2. Defaults to count/ha.
                Ignored if given eq value containing ORDS query.

        Returns:
            This object for chaining if desired.
        """
        param = self._create_float_param(eq, min_val, max_val)

        self._cpue_noha = None
        self._cpue_nokm2 = None
        self._cpue_no1000km2 = None

        if units == 'count/ha':
            self._cpue_noha = param
        elif units == 'count/km2':
            self._cpue_nokm2 = param
        elif units == 'count1000/km2':
            self._cpue_no1000km2 = param
        else:
            raise RuntimeError('Unrecognized units ' + units)

        return self

    def filter_weight(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'kg') -> 'Query':
        """Filter on taxon weight (kg) if available.

        Filter on taxon weight (kg) if available, overwrites all prior weight
        filters applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units in which the weight are given. Options are
                g, kg for grams and kilograms respectively. Deafults to kg.
                Ignored if given eq value containing ORDS query.

        Returns:
            This object for chaining if desired.
        """
        self._weight_kg = self._create_float_param(
            afscgap.convert.unconvert_weight(eq, units),
            afscgap.convert.unconvert_weight(min_val, units),
            afscgap.convert.unconvert_weight(max_val, units)
        )
        return self

    def filter_count(self, eq: FLOAT_PARAM = None, min_val: OPT_FLOAT = None,
        max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on total number of organism individuals in haul.

        Filter on total number of organism individuals in haul, overwrites all
        prior count filters applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded. Ignored if given eq value containing
                ORDS query.

        Returns:
            This object for chaining if desired.
        """
        self._count = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_bottom_temperature(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'c') -> 'Query':
        """Filter on bottom temperature.

        Filter on bottom temperature associated with observation if available in
        the units given. Overwrites all prior bottom temperature filters applied
        to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units in which the temperature filter values are given.
                Options: c or f for Celcius and Fahrenheit respectively.
                Defaults to c. Ignored if given eq value containing ORDS query.

        Returns:
            This object for chaining if desired.
        """
        self._bottom_temperature_c = self._create_float_param(
            afscgap.convert.unconvert_temperature(eq, units),
            afscgap.convert.unconvert_temperature(min_val, units),
            afscgap.convert.unconvert_temperature(max_val, units)
        )
        return self

    def filter_surface_temperature(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'c') -> 'Query':
        """Filter on surface temperature.

        Filter on surface temperature associated with observation if available
        in the units given. Overwrites all prior bottom temperature filters
        applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units in which the temperature filter values are given.
                Options: c or f for Celcius and Fahrenheit respectively.
                Defaults to c. Ignored if given eq value containing ORDS query.

        Returns:
            This object for chaining if desired.
        """
        self._surface_temperature_c = self._create_float_param(
            afscgap.convert.unconvert_temperature(eq, units),
            afscgap.convert.unconvert_temperature(min_val, units),
            afscgap.convert.unconvert_temperature(max_val, units)
        )
        return self

    def filter_depth(self, eq: FLOAT_PARAM = None, min_val: OPT_FLOAT = None,
        max_val: OPT_FLOAT = None, units: str = 'm') -> 'Query':
        """Filter on depth of the bottom in meters.

        Filter on depth of the bottom in meters, overwrites all prior depth
        filters applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units in which the distance are given. Options:
                m or km for meters and kilometers respectively. Defaults to m.
                Ignored if given eq value containing ORDS query.

        Returns:
            This object for chaining if desired.
        """
        self._depth_m = self._create_float_param(
            afscgap.convert.unconvert_distance(eq, units),
            afscgap.convert.unconvert_distance(min_val, units),
            afscgap.convert.unconvert_distance(max_val, units)
        )
        return self

    def filter_distance_fished(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'm') -> 'Query':
        """Filter on distance of the net fished.

        Filter on distance of the net fished, overwritting prior distance fished
        filters applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units in which the distance values are given. Options:
                m or km for meters and kilometers respectively. Defaults to m.
                Ignored if given eq value containing ORDS query.

        Returns:
            This object for chaining if desired.
        """
        def convert_to_km(target, units):
            in_meters = afscgap.convert.unconvert_distance(target, units)
            return afscgap.convert.convert_distance(in_meters, 'km')

        self._distance_fished_km = self._create_float_param(
            convert_to_km(eq, units),
            convert_to_km(min_val, units),
            convert_to_km(max_val, units)
        )
        return self

    def filter_net_width(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'm') -> 'Query':
        """Filter on distance of the net fished.

        Filter on distance of the net fished, overwritting prior net width
        filters applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            This object for chaining if desired.
        """
        self._net_width_m = self._create_float_param(
            afscgap.convert.unconvert_distance(eq, units),
            afscgap.convert.unconvert_distance(min_val, units),
            afscgap.convert.unconvert_distance(max_val, units)
        )
        return self

    def filter_net_height(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'm') -> 'Query':
        """Filter on height of the net fished.

        Filter on height of the net fished, overwritting prior net height
        filters applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            This object for chaining if desired.
        """
        self._net_height_m = self._create_float_param(
            afscgap.convert.unconvert_distance(eq, units),
            afscgap.convert.unconvert_distance(min_val, units),
            afscgap.convert.unconvert_distance(max_val, units)
        )
        return self

    def filter_area_swept(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'm') -> 'Query':
        """Filter on area covered by the net while fishing.

        Filter on area covered by the net while fishing, overwritting prior
        area swept filters applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units in which the area should be returned. Options:
                ha, m2, km2. Defaults to ha.

        Returns:
            This object for chaining if desired.
        """
        self._area_swept_ha = self._create_float_param(
            afscgap.convert.unconvert_area(eq, units),
            afscgap.convert.unconvert_area(min_val, units),
            afscgap.convert.unconvert_area(max_val, units)
        )
        return self

    def filter_duration(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'hr') -> 'Query':
        """Filter on duration of the haul.

        Filter on duration of the haul, ovewritting all prior duration filters
        applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units in which the duration should be returned. Options:
                day, hr, min. Defaults to hr.

        Returns:
            This object for chaining if desired.
        """
        self._duration_hr = self._create_float_param(
            afscgap.convert.unconvert_time(eq, units),
            afscgap.convert.unconvert_time(min_val, units),
            afscgap.convert.unconvert_time(max_val, units)
        )
        return self

    def filter_tsn(self, eq: INT_PARAM = None, min_val: OPT_INT = None,
        max_val: OPT_INT = None) -> 'Query':
        """Filter on taxonomic information system species code.

        Filter on taxonomic information system species code, overwritting all
        prior TSN filters applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            This object for chaining if desired.
        """
        self._tsn = self._create_int_param(eq, min_val, max_val)
        return self

    def filter_ak_survey_id(self, eq: INT_PARAM = None, min_val: OPT_INT = None,
        max_val: OPT_INT = None) -> 'Query':
        """Filter on AK identifier for the survey.

        Filter on AK identifier for the survey, overwritting all prior AK ID
        filters applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            This object for chaining if desired.
        """
        self._ak_survey_id = self._create_int_param(eq, min_val, max_val)
        return self

    def set_limit(self, limit: OPT_INT) -> 'Query':
        """Set the max number of results.

        Set the max number of results, overwritting prior limit settings on this
        Query.

        Args:
            limit: The maximum number of results to retrieve per HTTP request.
                If None or not provided, will use API's default.

        Returns:
            This object for chaining if desired.
        """
        self._limit = limit
        return self

    def set_start_offset(self, start_offset: OPT_INT) -> 'Query':
        """Indicate how many results to skip.

        Indicate how many results to skip, overwritting prior offset settings on
        this Query.

        Args:
            start_offset: The number of initial results to skip in retrieving
                results. If None or not provided, none will be skipped.

        Returns:
            This object for chaining if desired.
        """
        self._start_offset = start_offset
        return self

    def set_filter_incomplete(self, filter_incomplete: bool) -> 'Query':
        """Indicate if incomplete records should be filtered out.

        Indicate if incomplete records should be filtered out, overwritting
        prior incomplete filter settings on this Query.

        Args:
            filter_incomplete: Flag indicating if "incomplete" records should be
                filtered. If true, "incomplete" records are silently filtered
                from the results, putting them in the invalid records queue. If
                false, they are included and their is_complete() will return
                false. Defaults to false.

        Returns:
            This object for chaining if desired.
        """
        self._filter_incomplete = filter_incomplete
        return self

    def set_presence_only(self, presence_only: bool) -> 'Query':
        """Indicate if zero catch inference should be enabled.

        Indicate if zero catch inference should be enabled, overwritting prior
        abscence / zero catch data settings on this Query.

        Args:
            presence_only: Flag indicating if abscence / zero catch data should
                be inferred. If false, will run abscence data inference. If
                true, will return presence only data as returned by the NOAA API
                service. Defaults to true.

        Returns:
            This object for chaining if desired.
        """
        self._presence_only = presence_only
        return self

    def set_suppress_large_warning(self, supress: bool) -> 'Query':
        """Indicate if the large results warning should be supressed.

        Indicate if the large results warning should be supressed, overwritting
        prior large results warning supressions settings on this Query.

        Args:
            suppress_large_warning: Indicate if the library should warn when an
                operation may consume a large amount of memory. If true, the
                warning will not be emitted. Defaults to true.

        Returns:
            This object for chaining if desired.
        """
        self._suppress_large_warning = supress
        return self

    def set_warn_function(self, warn_function: WARN_FUNCTION) -> 'Query':
        """Indicate how warnings should be emitted.

        Indicate how warnings should be emitted, overwritting the prior warning
        function settings on this Query.

        Args:
            warn_function: Function to call with a message describing warnings
                encountered. If None, will use warnings.warn. Defaults to None.

        Returns:
            This object for chaining if desired.
        """
        self._warn_function = warn_function
        return self

    def set_hauls_prefetch(self, hauls_prefetch: OPT_HAUL_LIST) -> 'Query':
        """Indicate if hauls' data were prefetched.

        Indicate if hauls' data were prefetched, overwritting prior prefetch
        settings on this Query.

        Args:
            hauls_prefetch: If using presence_only=True, this is ignored.
                Otherwise, if None, will instruct the library to download hauls
                metadata. If not None, will use this as the hauls list for zero
                catch record inference.

        Returns:
            This object for chaining if desired.
        """
        self._hauls_prefetch = hauls_prefetch
        return self

    def execute(self) -> afscgap.cursor.Cursor:
        """Execute the query built up in this object.

        Execute the query built up in this object using its current state. Note
        that later changes to this builder will not impact prior returned
        Cursors from execute.

        Returns:
            Cursor to manage HTTP requests and query results.
        """
        all_dict_raw = {
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
            'ak_survey_id': self._ak_survey_id
        }

        api_cursor = afscgap.client.build_api_cursor(
            all_dict_raw,
            limit=self._limit,
            start_offset=self._start_offset,
            filter_incomplete=self._filter_incomplete,
            requestor=self._requestor,
            base_url=self._base_url
        )

        if self._presence_only:
            return api_cursor

        decorated_cursor = afscgap.inference.build_inference_cursor(
            all_dict_raw,
            api_cursor,
            requestor=self._requestor,
            hauls_url=self._hauls_url,
            hauls_prefetch=self._hauls_prefetch
        )

        if not self._suppress_large_warning:
            warn_function = self._warn_function
            if not warn_function:
                warn_function = lambda x: warnings.warn(x)

            warn_function(LARGE_WARNING)

        return decorated_cursor

    def _create_str_param(self, eq: STR_PARAM = None, min_val: OPT_STR = None,
        max_val: OPT_STR = None) -> STR_PARAM:
        """Create a new string parameter.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        """
        return self._create_param(eq, min_val, max_val)  # type: ignore

    def _create_float_param(self, eq: FLOAT_PARAM = None,
        min_val: FLOAT_PARAM = None,
        max_val: FLOAT_PARAM = None) -> FLOAT_PARAM:
        """Create a new float parameter.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
        """
        return self._create_param(eq, min_val, max_val)  # type: ignore

    def _create_int_param(self, eq: INT_PARAM = None, min_val: OPT_INT = None,
        max_val: OPT_INT = None) -> INT_PARAM:
        """Create a new int parameter.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
        Returns:
            Compatible param representation.
        """
        return self._create_param(eq, min_val, max_val)  # type: ignore

    def _create_param(self, eq=None, min_val=None, max_val=None):
        """Create a new parameter.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided. May also be
                a dictionary representing an ORDS query.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
        Returns:
            Compatible param representation.
        """
        eq_given = eq is not None
        min_val_given = min_val is not None
        max_val_given = max_val is not None

        if eq_given and (min_val_given and max_val_given):
            raise RuntimeError('Cannot query with both eq and min/max val.')

        if eq_given:
            return eq
        elif min_val_given or max_val_given:
            return [min_val, max_val]
        else:
            return None
