"""
.. include:: ../README.md

<br>
<br>

# API docs

Library which allows for Pythonic access to the interacting with AFSC GAP.

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
        self._year = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_srvy(self, eq: STR_PARAM = None, min_val: OPT_STR = None,
        max_val: OPT_STR = None) -> 'Query':
        """Filter on haul survey short name.

        Filter on the short name of the survey in which this observation was
        made. Pass None if no filter should be applied. Defaults to None. Note
        that common values include: NBS (N Bearing Sea), EBS (SE Bearing Sea),
        BSS (Bearing Sea Slope), GOA (Gulf of Alaska), and AI (Aleutian
        Islands).

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
        self._srvy = self._create_str_param(eq, min_val, max_val)
        return self

    def filter_survey(self, eq: STR_PARAM = None, min_val: OPT_STR = None,
        max_val: OPT_STR = None) -> 'Query':
        """Filter on survey long name.

        Filter on long form description of the survey in which the observation
        was made.

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
        self._survey = self._create_str_param(eq, min_val, max_val)
        return self

    def filter_survey_id(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on unique numeric ID for the survey.

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
        self._survey_id = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_cruise(self, eq: FLOAT_PARAM = None, min_val: OPT_FLOAT = None,
        max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on cruise ID.

        Filter on an ID uniquely identifying the cruise in which the observation
        was made.

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
        self._cruise = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_haul(self, eq: FLOAT_PARAM = None, min_val: OPT_FLOAT = None,
        max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on haul identifier.

        Filter on an ID uniquely identifying the haul in which this observation
        was made.

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
        self._haul = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_stratum(self, eq: FLOAT_PARAM = None, min_val: OPT_FLOAT = None,
        max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on unique ID for statistical area / survey combination.

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
        self._stratum = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_station(self, eq: STR_PARAM = None, min_val: OPT_STR = None,
        max_val: OPT_STR = None) -> 'Query':
        """Filter on station associated with the survey.

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
        self._station = self._create_str_param(eq, min_val, max_val)
        return self

    def filter_vessel_name(self, eq: STR_PARAM = None,
        min_val: OPT_STR = None, max_val: OPT_STR = None) -> 'Query':
        """Filter on unique ID describing the vessel that made this observation.

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
        self._vessel_name = self._create_str_param(eq, min_val, max_val)
        return self

    def filter_vessel_id(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on name of the vessel at the time the observation was made.

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
        self._vessel_id = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_date_time(self, eq: STR_PARAM = None, min_val: OPT_STR = None,
        max_val: OPT_STR = None) -> 'Query':
        """Filter on the date and time of the haul.

        Filter on the date and time of the haul as an ISO 8601 string. If given
        an ISO 8601 string, will convert from ISO 8601 to the API datetime
        string format. Similarly, if given a dictionary, all values matching an
        ISO 8601 string will be converted to the API datetime string format.

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
        self._date_time = self._create_str_param(eq, min_val, max_val)
        return self

    def filter_latitude_dd(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on latitude in decimal degrees associated with the haul.

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
        self._latitude_dd = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_longitude_dd(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on longitude in decimal degrees associated with the haul.

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
        self._longitude_dd = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_species_code(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on unique ID associated with the species observed.

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
        self._species_code = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_common_name(self, eq: STR_PARAM = None, min_val: OPT_STR = None,
        max_val: OPT_STR = None) -> 'Query':
        """Filter on the “common name” associated with the species observed.

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
        self._common_name = self._create_str_param(eq, min_val, max_val)
        return self

    def filter_scientific_name(self, eq: STR_PARAM = None,
        min_val: OPT_STR = None, max_val: OPT_STR = None) -> 'Query':
        """Filter on the "scientific name" associated with the species observed.

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
        self._scientific_name = self._create_str_param(eq, min_val, max_val)
        return self

    def filter_taxon_confidence(self, eq: STR_PARAM = None,
        min_val: OPT_STR = None, max_val: OPT_STR = None) -> 'Query':
        """Filter on confidence flag regarding ability to identify species.

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
        self._taxon_confidence = self._create_str_param(eq, min_val, max_val)
        return self

    def filter_cpue_kgha(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on catch per unit effort as kg/ha.

        Filter on catch per unit effort as weight divided by net area (kg /
        hectares) if available.

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
        self._cpue_kgha = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_cpue_kgkm2(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on catch per unit effort as kg/km2.

        Filter on catch per unit effort as weight divided by net area (kg /
        km^2) if available.

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
        self._cpue_kgkm2 = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_cpue_kg1000km2(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on catch per unit effort as kg1000/km2*1000.

        Filter on catch weight divided by net area (kg / km^2 * 1000) if
        available.

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
        self._cpue_kg1000km2 = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_cpue_noha(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter catch per unit effort as count over area in hectares.

        Filter on catch number divided by net sweep area if available (count /
        hectares).

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
        self._cpue_noha = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_cpue_nokm2(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter catch per unit effort as count over area in km^2.

        Filter on catch number divided by net sweep area if available (count /
        km^2).

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
        self._cpue_nokm2 = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_cpue_no1000km2(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter catch per unit effort as count over area in km^2 * 1000.

        Filter on catch number divided by net sweep area if available (count /
        km^2 * 1000).

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
        self._cpue_no1000km2 = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_weight_kg(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on taxon weight (kg) if available.

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
        self._weight_kg = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_count(self, eq: FLOAT_PARAM = None, min_val: OPT_FLOAT = None,
        max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on total number of organism individuals in haul.

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
        self._count = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_bottom_temperature_c(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on bottom temperature.

        Filter on bottom temperature associated with observation if available in
        Celsius.

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
        self._bottom_temperature_c = self._create_float_param(
            eq,
            min_val,
            max_val
        )
        return self

    def filter_surface_temperature_c(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on surface temperature.

        Filter on surface temperature associated with observation if available
        in Celsius.

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
        self._surface_temperature_c = self._create_float_param(
            eq,
            min_val,
            max_val
        )
        return self

    def filter_depth_m(self, eq: FLOAT_PARAM = None, min_val: OPT_FLOAT = None,
        max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on depth of the bottom in meters.

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
        self._depth_m = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_distance_fished_km(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on distance of the net fished as km.

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
        self._distance_fished_km = self._create_float_param(
            eq,
            min_val,
            max_val
        )
        return self

    def filter_net_width_m(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on distance of the net fished as m.

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
        self._net_width_m = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_net_height_m(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on height of the net fished as m.

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
        self._net_height_m = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_area_swept_ha(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on area covered by the net while fishing in hectares.

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
        self._area_swept_ha = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_duration_hr(self, eq: FLOAT_PARAM = None,
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> 'Query':
        """Filter on duration of the haul as number of hours.

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
        self._duration_hr = self._create_float_param(eq, min_val, max_val)
        return self

    def filter_tsn(self, eq: INT_PARAM = None, min_val: OPT_INT = None,
        max_val: OPT_INT = None) -> 'Query':
        """Filter on taxonomic information system species code.

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
        self._tsn = self._create_int_param(eq, min_val, max_val)
        return self

    def filter_ak_survey_id(self, eq: INT_PARAM = None, min_val: OPT_INT = None,
        max_val: OPT_INT = None) -> 'Query':
        """Filter on AK identifier for the survey.

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
        self._ak_survey_id = self._create_int_param(eq, min_val, max_val)
        return self

    def set_limit(self, limit: OPT_INT = None) -> 'Query':
        """Set the max number of results.

        Args:
            limit: The maximum number of results to retrieve per HTTP request.
                If None or not provided, will use API's default.
        """
        self._limit = limit
        return self

    def set_start_offset(self, start_offset: OPT_INT = None) -> 'Query':
        """Indicate how many results to skip.

        Args:
            start_offset: The number of initial results to skip in retrieving
                results. If None or not provided, none will be skipped.
        """
        self._start_offset = start_offset
        return self

    def set_filter_incomplete(self, filter_incomplete: bool = False) -> 'Query':
        """Indicate if incomplete records should be filtered out.

        Args:
            filter_incomplete: Flag indicating if "incomplete" records should be
                filtered. If true, "incomplete" records are silently filtered
                from the results, putting them in the invalid records queue. If
                false, they are included and their is_complete() will return
                false. Defaults to false.
        """
        self._filter_incomplete = filter_incomplete
        return self

    def set_presence_only(self, presence_only: bool = True) -> 'Query':
        """Indicate if zero catch inference should be enabled.

        Args:
            presence_only: Flag indicating if abscence / zero catch data should
                be inferred. If false, will run abscence data inference. If
                true, will return presence only data as returned by the NOAA API
                service. Defaults to true.
        """
        self._presence_only = presence_only
        return self

    def set_suppress_large_warning(self, supress: bool = False) -> 'Query':
        """Indicate if the large results warning should be supressed.

        Args:
            suppress_large_warning: Indicate if the library should warn when an
                operation may consume a large amount of memory. If true, the
                warning will not be emitted. Defaults to true.
        """
        self._suppress_large_warning = supress
        return self

    def set_warn_function(self, warn_function: WARN_FUNCTION = None) -> 'Query':
        """Indicate how warnings should be emitted.

        Args:
            warn_function: Function to call with a message describing warnings
                encountered. If None, will use warnings.warn. Defaults to None.
        """
        self._warn_function = warn_function
        return self

    def set_hauls_prefetch(self,
        hauls_prefetch: OPT_HAUL_LIST = None) -> 'Query':
        """Indicate if hauls' data were prefetched.

        Args:
            hauls_prefetch: If using presence_only=True, this is ignored.
                Otherwise, if None, will instruct the library to download hauls
                metadata. If not None, will use this as the hauls list for zero
                catch record inference.
        """
        self._hauls_prefetch = hauls_prefetch
        return self

    def execute(self) -> afscgap.cursor.Cursor:
        """Execute the query built up in this object.

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
        min_val: OPT_FLOAT = None, max_val: OPT_FLOAT = None) -> FLOAT_PARAM:
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
