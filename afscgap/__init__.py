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
LICENSE.txt.
"""
import typing
import warnings

import afscgap.client
import afscgap.inference
import afscgap.model

from afscgap.util import FLOAT_PARAM
from afscgap.util import INT_PARAM
from afscgap.util import STR_PARAM

from afscgap.util import OPT_INT
from afscgap.util import OPT_STR
from afscgap.util import OPT_REQUESTOR

WARN_FUNCTION = typing.Optional[typing.Callable[[str], None]]

LARGE_WARNING = ' '.join([
    'Your query may return a very large amount of records.',
    'Be sure to interact with results in a memory efficient way.'
])


def query(
    year: FLOAT_PARAM = None,
    srvy: STR_PARAM = None,
    survey: STR_PARAM = None,
    survey_id: FLOAT_PARAM = None,
    cruise: FLOAT_PARAM = None,
    haul: FLOAT_PARAM = None,
    stratum: FLOAT_PARAM = None,
    station: STR_PARAM = None,
    vessel_name: STR_PARAM = None,
    vessel_id: FLOAT_PARAM = None,
    date_time: STR_PARAM = None,
    latitude_dd: FLOAT_PARAM = None,
    longitude_dd: FLOAT_PARAM = None,
    species_code: FLOAT_PARAM = None,
    common_name: STR_PARAM = None,
    scientific_name: STR_PARAM = None,
    taxon_confidence: STR_PARAM = None,
    cpue_kgha: FLOAT_PARAM = None,
    cpue_kgkm2: FLOAT_PARAM = None,
    cpue_kg1000km2: FLOAT_PARAM = None,
    cpue_noha: FLOAT_PARAM = None,
    cpue_nokm2: FLOAT_PARAM = None,
    cpue_no1000km2: FLOAT_PARAM = None,
    weight_kg: FLOAT_PARAM = None,
    count: FLOAT_PARAM = None,
    bottom_temperature_c: FLOAT_PARAM = None,
    surface_temperature_c: FLOAT_PARAM = None,
    depth_m: FLOAT_PARAM = None,
    distance_fished_km: FLOAT_PARAM = None,
    net_width_m: FLOAT_PARAM = None,
    net_height_m: FLOAT_PARAM = None,
    area_swept_ha: FLOAT_PARAM = None,
    duration_hr: FLOAT_PARAM = None,
    tsn: INT_PARAM = None,
    ak_survey_id: INT_PARAM = None,
    limit: OPT_INT = None,
    start_offset: OPT_INT = None,
    base_url: OPT_STR = None,
    requestor: OPT_REQUESTOR = None,
    filter_incomplete: bool = False,
    presence_only: bool = True,
    suppress_large_warning: bool = False,
    hauls_url: OPT_STR = None,
    warn_function: WARN_FUNCTION = None) -> afscgap.cursor.Cursor:
    """Execute a query against the AFSC GAP API.

    Args:
        year: Filter on year for the survey in which this observation was made.
            Pass None if no filter should be applied. Defaults to None.
        srvy: Filter on the short name of the survey in which this observation
            was made. Pass None if no filter should be applied. Defaults to
            None. Note that common values include: NBS (N Bearing Sea), EBS (SE
            Bearing Sea), BSS (Bearing Sea Slope), GOA (Gulf of Alaska), and
            AI (Aleutian Islands).
        survey: Filter on long form description of the survey in which the
            observation was made. Pass None if no filter should be applied.
            Defaults to None.
        survey_id: Filter on unique numeric ID for the survey. Pass None if no
            filter should be applied. Defaults to None.
        cruise: Filter on an ID uniquely identifying the cruise in which the
            observation was made. Pass None if no filter should be applied.
            Defaults to None.
        haul: Filter on an ID uniquely identifying the haul in which this
            observation was made. Pass None if no filter should be applied.
            Defaults to None.
        stratum: Filter on unique ID for statistical area / survey combination.
            Pass None if no filter should be applied. Defaults to None.
        station: Filter on station associated with the survey. Pass None if no
            filter should be applied. Defaults to None.
        vessel_name: Filter on unique ID describing the vessel that made this
            observation. Pass None if no filter should be applied. Defaults to
            None.
        vessel_id: Filter on name of the vessel at the time the observation was
            made. Pass None if no filter should be applied. Defaults to None.
        date_time: Filter on the date and time of the haul as an ISO 8601
            string. Pass None if no filter should be applied. Defaults to None.
            If given an ISO 8601 string, will convert from ISO 8601 to the API
            datetime string format. Similarly, if given a dictionary, all values
            matching an ISO 8601 string will be converted to the API datetime
            string format.
        latitude_dd: Filter on latitude in decimal degrees associated with the
            haul. Pass None if no filter should be applied. Defaults to None.
        longitude_dd: Filter on longitude in decimal degrees associated with the
            haul. Pass None if no filter should be applied. Defaults to None.
        species_code: Filter on unique ID associated with the species observed.
            Pass None if no filter should be applied. Defaults to None.
        common_name: Filter on the “common name” associated with the species
            observed. Pass None if no filter should be applied. Defaults to
            None.
        scientific_name: Filter on the “scientific name” associated with the
            species observed. Pass None if no filter should be applied. Defaults
            to None.
        taxon_confidence: Filter on confidence flag regarding ability to
            identify species. Pass None if no filter should be applied. Defaults
            to None.
        cpue_kgha: Filter on catch weight divided by net area (kg / hectares) if
            available. Pass None if no filter should be applied. Defaults to
            None.
        cpue_kgkm2: Filter on catch weight divided by net area (kg / km^2) if
            available. Pass None if no filter should be applied. Defaults to
            None.
        cpue_kg1000km2: Filter on catch weight divided by net area (kg / km^2 *
            1000) if available. Pass None if no filter should be applied.
            Defaults to None.
        cpue_noha: Filter on catch number divided by net sweep area if available
            (count / hectares). Pass None if no filter should be applied.
            Defaults to None.
        cpue_nokm2: Filter on catch number divided by net sweep area if
            available (count / km^2). Pass None if no filter should be applied.
            Defaults to None.
        cpue_no1000km2: Filter on catch number divided by net sweep area if
            available (count / km^2 * 1000). Pass None if no filter should be
            applied. Defaults to None.
        weight_kg: Filter on taxon weight (kg) if available. Pass None if no
            filter should be applied. Defaults to None.
        count: Filter on total number of organism individuals in haul. Pass None
            if no filter should be applied. Defaults to None.
        bottom_temperature_c: Filter on bottom temperature associated with
            observation if available in Celsius. Pass None if no filter should
            be applied. Defaults to None.
        surface_temperature_c: Filter on surface temperature associated with
            observation if available in Celsius. Pass None if no filter should
            be applied. Defaults to None.
        depth_m: Filter on depth of the bottom in meters. Pass None if no filter
            should be applied. Defaults to None.
        distance_fished_km: Filter on distance of the net fished as km. Pass
            None if no filter should be applied. Defaults to None.
        net_width_m: Filter on distance of the net fished as m. Pass None if no
            filter should be applied. Defaults to None.
        net_height_m: Filter on height of the net fished as m. Pass None if no
            filter should be applied. Defaults to None.
        area_swept_ha: Filter on area covered by the net while fishing in
            hectares. Pass None if no filter should be applied. Defaults to
            None.
        duration_hr: Filter on duration of the haul as number of hours. Pass
            None if no filter should be applied. Defaults to None.
        tsn: Filter on taxonomic information system species code. Pass None if
            no filter should be applied. Defaults to None.
        ak_survey_id: Filter on AK identifier for the survey. Pass None if no
            filter should be applied. Defaults to None.
        limit: The maximum number of results to retrieve per HTTP request. If
            None or not provided, will use API's default.
        start_offset: The number of initial results to skip in retrieving
            results. If None or not provided, none will be skipped.
        base_url: The URL at which the API can be found. If None, will use
            default (offical URL at time of release). See
            afscgap.client.DEFAULT_URL.
        requestor: Strategy to use for making HTTP requests. If None, will use
            a default as defined by afscgap.client.Cursor.
        filter_incomplete: Flag indicating if "incomplete" records should be
            filtered. If true, "incomplete" records are silently filtered from
            the results, putting them in the invalid records queue. If false,
            they are included and their is_complete() will return false.
            Defaults to false.
        presence_only: Flag indicating if abscence / zero catch data should be
            inferred. If false, will run abscence data inference. If true, will
            return presence only data as returned by the NOAA API service.
            Defaults to true.
        suppress_large_warning: Indicate if the library should warn when an
            operation may consume a large amount of memory. If true, the warning
            will not be emitted. Defaults to true.
        hauls_url: The URL at which the flat file with hauls metadata can be
            found or None if a default should be used. Defaults to None.
        warn_function: Function to call with a message describing warnings
            encountered. If None, will use warnings.warn. Defaults to None.

    Returns:
        Cursor to manage HTTP requests and query results.
    """

    all_dict_raw = {
        'year': year,
        'srvy': srvy,
        'survey': survey,
        'survey_id': survey_id,
        'cruise': cruise,
        'haul': haul,
        'stratum': stratum,
        'station': station,
        'vessel_name': vessel_name,
        'vessel_id': vessel_id,
        'date_time': date_time,
        'latitude_dd': latitude_dd,
        'longitude_dd': longitude_dd,
        'species_code': species_code,
        'common_name': common_name,
        'scientific_name': scientific_name,
        'taxon_confidence': taxon_confidence,
        'cpue_kgha': cpue_kgha,
        'cpue_kgkm2': cpue_kgkm2,
        'cpue_kg1000km2': cpue_kg1000km2,
        'cpue_noha': cpue_noha,
        'cpue_nokm2': cpue_nokm2,
        'cpue_no1000km2': cpue_no1000km2,
        'weight_kg': weight_kg,
        'count': count,
        'bottom_temperature_c': bottom_temperature_c,
        'surface_temperature_c': surface_temperature_c,
        'depth_m': depth_m,
        'distance_fished_km': distance_fished_km,
        'net_width_m': net_width_m,
        'net_height_m': net_height_m,
        'area_swept_ha': area_swept_ha,
        'duration_hr': duration_hr,
        'tsn': tsn,
        'ak_survey_id': ak_survey_id
    }

    api_cursor = afscgap.client.build_api_cursor(
        all_dict_raw,
        limit=limit,
        start_offset=start_offset,
        filter_incomplete=filter_incomplete,
        requestor=requestor,
        base_url=base_url
    )

    if presence_only:
        return api_cursor

    decorated_cursor = afscgap.inference.build_inference_cursor(
        all_dict_raw,
        api_cursor,
        requestor=requestor,
        hauls_url=hauls_url
    )

    if not suppress_large_warning:
        if not warn_function:
            warn_function = lambda x: warnings.warn(x)

        warn_function(LARGE_WARNING)

    return decorated_cursor
