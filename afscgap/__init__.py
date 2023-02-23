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
import typing

import afscgap.client
import afscgap.model

STR_OR_DICT = typing.Union[str, dict]
FLOAT_PARAM = typing.Optional[typing.Union[float, dict]]
INT_PARAM = typing.Optional[typing.Union[int, dict]]
STR_PARAM = typing.Optional[STR_OR_DICT]


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
    limit: afscgap.client.OPT_INT = None,
    start_offset: afscgap.client.OPT_INT = None,
    base_url: afscgap.client.OPT_STR = None,
    requestor: afscgap.client.OPT_REQUESTOR = None,
    filter_incomplete: bool = False) -> afscgap.client.Cursor:
    """Execute a query against the AFSC GAP API.

    Args:
        year: Filter on year for the survey in which this observation was made.
            Pass None if no filter should be applied. Defaults to None.
        srvy: Filter on the short name of the survey in which this observation
            was made. Pass None if no filter should be applied. Defaults to
            None.
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

    Returns:
        Cursor to manage HTTP requests and query results.
    """

    all_dict = {
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
        'date_time': convert_from_iso8601(date_time),
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

    query_url = afscgap.client.get_query_url(all_dict, base=base_url)
    return afscgap.client.Cursor(
        query_url,
        limit=limit,
        start_offset=start_offset,
        requestor=requestor,
        filter_incomplete=filter_incomplete
    )


def convert_from_iso8601(target: STR_PARAM) -> STR_PARAM:
    """Convert strings from ISO 8601 format to API format.

    Args:
        target: The string or dictionary in which to perform the
            transformations.

    Returns:
        If given an ISO 8601 string, will convert from ISO 8601 to the API
        datetime string format. Similarly, if given a dictionary, all values
        matching an ISO 8601 string will be converted to the API datetime string
        format. If given None, returns None.
    """
    if target is None:
        return None
    elif isinstance(target, str):
        return afscgap.model.convert_from_iso8601(target)
    elif isinstance(target, dict):
        items = target.items()
        output_dict = {}

        for key, value in items:
            if isinstance(value, str):
                output_dict[key] = afscgap.model.convert_from_iso8601(value)
            else:
                output_dict[key] = value

        return output_dict
    else:
        return target
