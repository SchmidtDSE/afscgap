"""Library which allows for Pythonic access to the interacting with AFSC GAP.

This library supports Pythonic utilization of the Ground Fish Assessment Program (GAP) datasets
produced by the Resource Assessment and Conservation Engineering (RACE) Division of the Alaska
Fisheries Science Center (AFSC) as part of the National Oceanic and Atmospheric Administration
(NOAA Fisheries). Note that this is a community-provided library and is not officially endorsed by
NOAA.

(c) 2024 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import typing

import afscgap.cursor
import afscgap.flat
import afscgap.param

from afscgap.typesdef import OPT_FLOAT
from afscgap.typesdef import INT_PARAM
from afscgap.typesdef import STR_PARAM
from afscgap.typesdef import OPT_INT
from afscgap.typesdef import OPT_STR
from afscgap.typesdef import OPT_REQUESTOR

WARN_FUNCTION = typing.Optional[typing.Callable[[str], None]]

DEFAULT_URL = 'https://data.pyafscgap.org'


class Query:
    """Entrypoint for the AFSC GAP Python library.

    Facade for executing queries against AFSC GAP and builder to create those
    queries.
    """

    def __init__(self, base_url: OPT_STR = None, requestor: OPT_REQUESTOR = None):
        """Create a new Query.

        Args:
            base_url: The URL at which the flat files can be found. If None, will use
                default. See afscgap.DEFAULT_URL.
            requestor: Strategy to use for making HTTP requests. If None, will
                use a default as defined by afscgap.client.Cursor.
        """
        # URLs for data
        self._base_url = base_url
        self._requestor = requestor

        # Filter parameters
        self._year: afscgap.param.Param = afscgap.param.EmptyParam()
        self._srvy: afscgap.param.Param = afscgap.param.EmptyParam()
        self._survey: afscgap.param.Param = afscgap.param.EmptyParam()
        self._survey_id: afscgap.param.Param = afscgap.param.EmptyParam()
        self._cruise: afscgap.param.Param = afscgap.param.EmptyParam()
        self._haul: afscgap.param.Param = afscgap.param.EmptyParam()
        self._stratum: afscgap.param.Param = afscgap.param.EmptyParam()
        self._station: afscgap.param.Param = afscgap.param.EmptyParam()
        self._vessel_name: afscgap.param.Param = afscgap.param.EmptyParam()
        self._vessel_id: afscgap.param.Param = afscgap.param.EmptyParam()
        self._date_time: afscgap.param.Param = afscgap.param.EmptyParam()
        self._latitude_dd: afscgap.param.Param = afscgap.param.EmptyParam()
        self._longitude_dd: afscgap.param.Param = afscgap.param.EmptyParam()
        self._species_code: afscgap.param.Param = afscgap.param.EmptyParam()
        self._common_name: afscgap.param.Param = afscgap.param.EmptyParam()
        self._scientific_name: afscgap.param.Param = afscgap.param.EmptyParam()
        self._taxon_confidence: afscgap.param.Param = afscgap.param.EmptyParam()
        self._cpue_kgha: afscgap.param.Param = afscgap.param.EmptyParam()
        self._cpue_kgkm2: afscgap.param.Param = afscgap.param.EmptyParam()
        self._cpue_kg1000km2: afscgap.param.Param = afscgap.param.EmptyParam()
        self._cpue_noha: afscgap.param.Param = afscgap.param.EmptyParam()
        self._cpue_nokm2: afscgap.param.Param = afscgap.param.EmptyParam()
        self._cpue_no1000km2: afscgap.param.Param = afscgap.param.EmptyParam()
        self._weight_kg: afscgap.param.Param = afscgap.param.EmptyParam()
        self._count: afscgap.param.Param = afscgap.param.EmptyParam()
        self._bottom_temperature_c: afscgap.param.Param = afscgap.param.EmptyParam()
        self._surface_temperature_c: afscgap.param.Param = afscgap.param.EmptyParam()
        self._depth_m: afscgap.param.Param = afscgap.param.EmptyParam()
        self._distance_fished_km: afscgap.param.Param = afscgap.param.EmptyParam()
        self._net_width_m: afscgap.param.Param = afscgap.param.EmptyParam()
        self._net_height_m: afscgap.param.Param = afscgap.param.EmptyParam()
        self._area_swept_ha: afscgap.param.Param = afscgap.param.EmptyParam()
        self._duration_hr: afscgap.param.Param = afscgap.param.EmptyParam()

        # Query pararmeters
        self._limit: OPT_INT = None
        self._filter_incomplete: bool = False
        self._presence_only: bool = False
        self._suppress_large_warning: bool = False
        self._warn_function: WARN_FUNCTION = None

    def filter_year(self, eq: OPT_FLOAT = None, min_val: OPT_FLOAT = None,
        max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on year for the survey in which this observation was made.

        Filter on year for the survey in which this observation was made,
        ovewritting all prior year filters on this Query if one was previously
        set.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
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
                Error thrown if min_val or max_val also provided.
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
                Error thrown if min_val or max_val also provided.
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

    def filter_survey_id(self, eq: OPT_FLOAT = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on unique numeric ID for the survey.

        Filter on unique numeric ID for the survey, overwritting prior survey ID
        filters if set on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
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

    def filter_cruise(self, eq: OPT_FLOAT = None, min_val: OPT_FLOAT = None,
        max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on cruise ID.

        Filter on an ID uniquely identifying the cruise in which the observation
        was made. Overwrites all prior cruise filters on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
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

    def filter_haul(self, eq: OPT_FLOAT = None, min_val: OPT_FLOAT = None,
        max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on haul identifier.

        Filter on an ID uniquely identifying the haul in which this observation
        was made. Overwrites all prior haul filters on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
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

    def filter_stratum(self, eq: OPT_FLOAT = None, min_val: OPT_FLOAT = None,
        max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on unique ID for statistical area / survey combination.

        Filter on unique ID for statistical area / survey combination,
        overwritting all prior stratum filters on Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
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
                Error thrown if min_val or max_val also provided.
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
                Error thrown if min_val or max_val also provided.
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

    def filter_vessel_id(self, eq: OPT_FLOAT = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on name of the vessel at the time the observation was made.

        Filter on name of the vessel at the time the observation was made,
        overwritting all prior vessel ID filters on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
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
                Error thrown if min_val or max_val also provided.
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

    def filter_latitude(self, eq: OPT_FLOAT = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'dd') -> 'Query':
        """Filter on latitude in decimal degrees associated with the haul.

        Filter on latitude in decimal degrees associated with the haul,
        overwritting all prior latitude filters on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
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
        self._latitude_dd = self._create_float_param(
            afscgap.convert.convert(eq, units, 'dd'),
            afscgap.convert.convert(min_val, units, 'dd'),
            afscgap.convert.convert(max_val, units, 'dd')
        )
        return self

    def filter_longitude(self, eq: OPT_FLOAT = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'dd') -> 'Query':
        """Filter on longitude in decimal degrees associated with the haul.

        Filter on longitude in decimal degrees associated with the haul,
        overwritting all prior longitude filters on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
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
            afscgap.convert.convert(eq, units, 'dd'),
            afscgap.convert.convert(min_val, units, 'dd'),
            afscgap.convert.convert(max_val, units, 'dd')
        )
        return self

    def filter_species_code(self, eq: OPT_FLOAT = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on unique ID associated with the species observed.

        Filter on unique ID associated with the species observed, overwritting
        all prior species code filters on this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
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
                Error thrown if min_val or max_val also provided.
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
                Error thrown if min_val or max_val also provided.
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
                Error thrown if min_val or max_val also provided.
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

    def filter_cpue_weight(self, eq: OPT_FLOAT = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'kg/ha') -> 'Query':
        """Filter on catch per unit effort.

        Filter on catch per unit effort as weight divided by net area if
        available. Overwrites all prior CPUE weight filters applied to this
        Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units for the catch per unit effort provided. Options:
                kg/ha, kg/km2, kg1000/km2. Defaults to kg/ha.

        Returns:
            This object for chaining if desired.
        """
        param = self._create_float_param(eq, min_val, max_val)

        self._cpue_kgha = afscgap.param.EmptyParam()
        self._cpue_kgkm2 = afscgap.param.EmptyParam()
        self._cpue_kg1000km2 = afscgap.param.EmptyParam()

        if units == 'kg/ha':
            self._cpue_kgha = param
        elif units == 'kg/km2':
            self._cpue_kgkm2 = param
        elif units == 'kg1000/km2':
            self._cpue_kg1000km2 = param
        else:
            raise RuntimeError('Unrecognized units ' + units)

        return self

    def filter_cpue_count(self, eq: OPT_FLOAT = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'count/ha') -> 'Query':
        """Filter catch per unit effort as count over area in hectares.

        Filter on catch number divided by net sweep area if available (count /
        hectares). Overwrites all prior CPUE count filters applied to this
        Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units for the given catch per unit effort. Options:
                count/ha, count/km2, and count1000/km2. Defaults to count/ha.

        Returns:
            This object for chaining if desired.
        """
        param = self._create_float_param(eq, min_val, max_val)

        self._cpue_noha = afscgap.param.EmptyParam()
        self._cpue_nokm2 = afscgap.param.EmptyParam()
        self._cpue_no1000km2 = afscgap.param.EmptyParam()

        if units == 'count/ha':
            self._cpue_noha = param
        elif units == 'count/km2':
            self._cpue_nokm2 = param
        elif units == 'count1000/km2':
            self._cpue_no1000km2 = param
        else:
            raise RuntimeError('Unrecognized units ' + units)

        return self

    def filter_weight(self, eq: OPT_FLOAT = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'kg') -> 'Query':
        """Filter on taxon weight (kg) if available.

        Filter on taxon weight (kg) if available, overwrites all prior weight
        filters applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units in which the weight are given. Options are
                g, kg for grams and kilograms respectively. Deafults to kg.

        Returns:
            This object for chaining if desired.
        """
        self._weight_kg = self._create_float_param(
            afscgap.convert.convert(eq, units, 'kg'),
            afscgap.convert.convert(min_val, units, 'kg'),
            afscgap.convert.convert(max_val, units, 'kg')
        )
        return self

    def filter_count(self, eq: OPT_FLOAT = None, min_val: OPT_FLOAT = None,
        max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on total number of organism individuals in haul.

        Filter on total number of organism individuals in haul, overwrites all
        prior count filters applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            This object for chaining if desired.
        """
        self._count = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_bottom_temperature(self, eq: OPT_FLOAT = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'c') -> 'Query':
        """Filter on bottom temperature.

        Filter on bottom temperature associated with observation if available in
        the units given. Overwrites all prior bottom temperature filters applied
        to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units in which the temperature filter values are given.
                Options: c or f for Celcius and Fahrenheit respectively.
                Defaults to c.

        Returns:
            This object for chaining if desired.
        """
        self._bottom_temperature_c = self._create_float_param(
            afscgap.convert.convert(eq, units, 'c'),
            afscgap.convert.convert(min_val, units, 'c'),
            afscgap.convert.convert(max_val, units, 'c')
        )
        return self

    def filter_surface_temperature(self, eq: OPT_FLOAT = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'c') -> 'Query':
        """Filter on surface temperature.

        Filter on surface temperature associated with observation if available
        in the units given. Overwrites all prior bottom temperature filters
        applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units in which the temperature filter values are given.
                Options: c or f for Celcius and Fahrenheit respectively.
                Defaults to c.

        Returns:
            This object for chaining if desired.
        """
        self._surface_temperature_c = self._create_float_param(
            afscgap.convert.convert(eq, units, 'c'),
            afscgap.convert.convert(min_val, units, 'c'),
            afscgap.convert.convert(max_val, units, 'c')
        )
        return self

    def filter_depth(self, eq: OPT_FLOAT = None, min_val: OPT_FLOAT = None,
        max_val: OPT_FLOAT = None, units: str = 'm') -> 'Query':
        """Filter on depth of the bottom in meters.

        Filter on depth of the bottom in meters, overwrites all prior depth
        filters applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units in which the distance are given. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            This object for chaining if desired.
        """
        self._depth_m = self._create_float_param(
            afscgap.convert.convert(eq, units, 'm'),
            afscgap.convert.convert(min_val, units, 'm'),
            afscgap.convert.convert(max_val, units, 'm')
        )
        return self

    def filter_distance_fished(self, eq: OPT_FLOAT = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'm') -> 'Query':
        """Filter on distance of the net fished.

        Filter on distance of the net fished, overwritting prior distance fished
        filters applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            units: The units in which the distance values are given. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            This object for chaining if desired.
        """
        def convert_to_km(target, units):
            return afscgap.convert.convert(target, units, 'km')

        self._distance_fished_km = self._create_float_param(
            convert_to_km(eq, units),
            convert_to_km(min_val, units),
            convert_to_km(max_val, units)
        )
        return self

    def filter_net_width(self, eq: OPT_FLOAT = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'm') -> 'Query':
        """Filter on distance of the net fished.

        Filter on distance of the net fished, overwritting prior net width
        filters applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
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
            afscgap.convert.convert(eq, units, 'm'),
            afscgap.convert.convert(min_val, units, 'm'),
            afscgap.convert.convert(max_val, units, 'm')
        )
        return self

    def filter_net_height(self, eq: OPT_FLOAT = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'm') -> 'Query':
        """Filter on height of the net fished.

        Filter on height of the net fished, overwritting prior net height
        filters applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
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
            afscgap.convert.convert(eq, units, 'm'),
            afscgap.convert.convert(min_val, units, 'm'),
            afscgap.convert.convert(max_val, units, 'm')
        )
        return self

    def filter_area_swept(self, eq: OPT_FLOAT = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'm') -> 'Query':
        """Filter on area covered by the net while fishing.

        Filter on area covered by the net while fishing, overwritting prior
        area swept filters applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
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
            afscgap.convert.convert(eq, units, 'ha'),
            afscgap.convert.convert(min_val, units, 'ha'),
            afscgap.convert.convert(max_val, units, 'ha')
        )
        return self

    def filter_duration(self, eq: OPT_FLOAT = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None,
        units: str = 'hr') -> 'Query':
        """Filter on duration of the haul.

        Filter on duration of the haul, ovewritting all prior duration filters
        applied to this Query.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
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
            afscgap.convert.convert(eq, units, 'hr'),
            afscgap.convert.convert(min_val, units, 'hr'),
            afscgap.convert.convert(max_val, units, 'hr')
        )
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

    def execute(self) -> afscgap.cursor.Cursor:
        """Execute the query built up in this object.

        Execute the query built up in this object using its current state. Note
        that later changes to this builder will not impact prior returned
        Cursors from execute.

        Returns:
            Cursor to manage HTTP requests and query results.
        """
        params_dict = {
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
            'duration_hr': self._duration_hr
        }

        meta_params = afscgap.flat_model.ExecuteMetaParams(
            self._base_url if self._base_url else DEFAULT_URL,
            self._requestor,
            self._limit,
            self._filter_incomplete,
            self._presence_only,
            self._suppress_large_warning,
            self._warn_function
        )

        return afscgap.flat.execute(params_dict, meta_params)

    def _create_str_param(self, eq: STR_PARAM = None, min_val: OPT_STR = None,
        max_val: OPT_STR = None) -> afscgap.param.Param:
        """Create a new string parameter.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            Newly initalized parameter.
        """
        param_type = self._get_param_type(eq, min_val, max_val)
        strategy = {
            'empty': lambda: afscgap.param.EmptyParam(),
            'equals': lambda: afscgap.param.StrEqualsParam(eq),  # type: ignore
            'range': lambda: afscgap.param.StrRangeParam(min_val, max_val)  # type: ignore
        }[param_type]
        return strategy()  # type: ignore

    def _create_float_param(self, eq: OPT_FLOAT = None,
        min_val: OPT_FLOAT = None,
        max_val: OPT_FLOAT = None) -> afscgap.param.Param:
        """Create a new float parameter.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            Newly initalized parameter.
        """
        param_type = self._get_param_type(eq, min_val, max_val)
        strategy = {
            'empty': lambda: afscgap.param.EmptyParam(),
            'equals': lambda: afscgap.param.FloatEqualsParam(eq),    # type: ignore
            'range': lambda: afscgap.param.FloatRangeParam(min_val, max_val)   # type: ignore
        }[param_type]
        return strategy()  # type: ignore

    def _create_int_param(self, eq: INT_PARAM = None, min_val: OPT_INT = None,
        max_val: OPT_INT = None) -> afscgap.param.Param:
        """Create a new int parameter.

        Args:
            eq: The exact value that must be matched for a record to be
                returned. Pass None if no equality filter should be applied.
                Error thrown if min_val or max_val also provided.
            min_val: The minimum allowed value, inclusive. Pass None if no
                minimum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.
            max_val: The maximum allowed value, inclusive. Pass None if no
                maximum value filter should be applied. Defaults to None. Error
                thrown if eq also proivded.

        Returns:
            Newly initalized parameter.
        """
        param_type = self._get_param_type(eq, min_val, max_val)
        strategy = {
            'empty': lambda: afscgap.param.EmptyParam(),
            'equals': lambda: afscgap.param.IntEqualsParam(eq),  # type: ignore
            'range': lambda: afscgap.param.IntRangeParam(min_val, max_val)  # type: ignore
        }[param_type]
        return strategy()  # type: ignore

    def _get_param_type(self, eq, min_val, max_val) -> str:
        """Determine how the parameter should be interpreted.

        Args:
            eq: The value for equality or None if no equals filter.
            min_val: The minimum value or None if no minimum filter.
            max_val: The maximum value or None if no maximum filter.

        Returns:
            One of the following as a string: empty, equals, range.
        """
        if eq is None:
            if min_val is None and max_val is None:
                return 'empty'
            else:
                return 'range'
        else:
            if min_val is not None or max_val is not None:
                raise RuntimeError('Both range and equality filters provided.')
            else:
                return 'equals'
