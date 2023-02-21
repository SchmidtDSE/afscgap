"""
Main entrypoint into the afscgap library which allows for Pythonic access to the
interacting with the API for the Ground Fish Assessment Program (GAP), a dataset 
produced by the Resource Assessment and Conservation Engineering (RACE) Division 
of the Alaska Fisheries Science Center (AFSC) as part of the National Oceanic
and Atmospheric Administration (NOAA Fisheries). Note that this is a community-
provided library and is not officially endorsed by NOAA.

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
import json
import typing

import afscgap.client

FLOAT_PARAM = typing.Optional[typing.Union[float, dict]]
INT_PARAM = typing.Optional[typing.Union[int, dict]]
STR_PARAM = typing.Optional[typing.Union[str, dict]]


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

    query_url = afscgap.client.get_query_url(all_dict, base=base_url)
    return afscgap.client.Cursor(
        query_url,
        limit=limit,
        start_offset=start_offset,
        requestor=requestor,
        filter_incomplete=filter_incomplete
    )
