"""
Logic for making actual HTTP requests and managaing pagination when interfacing
with the NOAA-run AFSC GAP API.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import copy
import json
import queue
import typing

import afscgap.convert
import afscgap.cursor
import afscgap.http_util
import afscgap.model
import afscgap.query_util

from afscgap.typesdef import OPT_FLOAT
from afscgap.typesdef import OPT_INT
from afscgap.typesdef import OPT_REQUESTOR
from afscgap.typesdef import OPT_STR

DEFAULT_DOMAIN = 'https://apps-st.fisheries.noaa.gov'
DEFAULT_URL = DEFAULT_DOMAIN + '/ods/foss/afsc_groundfish_survey/'


def build_api_cursor(params: dict, limit: OPT_INT = None,
    start_offset: OPT_INT = None, filter_incomplete: bool = False,
    requestor: OPT_REQUESTOR = None,
    base_url: OPT_STR = None) -> afscgap.cursor.Cursor:
    """Build a cursor which will iterate over API service results.

    Args:
        params: Dictionary of filters to apply to the query where a value of
            None means no filter should be applied on that field.
        limit: The maximum number of records to return per page.
        start_offset: The number of records being skipped (number of records
            prior to query_url).
        filter_incomplete: Flag indicating if incomplete records should be
            silently filtered. If true, they will not be returned during
            iteration and placed in the queue at get_invalid(). If false,
            they will be returned and those incomplete records'
            get_complete() will return false. Defaults to false.
        requestor: Strategy to make HTTP GET requests. If None, will default
            to requests.get.
        base_url: The URL at which the API service can be found or None to use
            a default. Defaults to None.

    Returns:
        Cursor which iterates over the results from the API service.
    """
    params_safe = copy.deepcopy(params)
    params_safe['date_time'] = afscgap.convert.convert_from_iso8601(
        params_safe['date_time']
    )
    params_ords = afscgap.query_util.interpret_query_to_ords(params_safe)

    query_url = get_query_url(params_ords, base=base_url)

    return ApiServiceCursor(
        query_url,
        limit=limit,
        start_offset=start_offset,
        requestor=requestor,
        filter_incomplete=filter_incomplete
    )


def get_query_url(params: dict, base: OPT_STR = None) -> str:
    """Get the URL at which a query can be made.

    Args:
        params: Dictionary of filters to apply to the query where a value of
            None means no filter should be applied on that field.
        base: The URL at which the API service can be found. If None, will use
            DEFAULT_URL. Defaults to None.

    Returns:
        URL at which an HTTP GET request can be made to execute the desired
        query.
    """
    if base is None:
        base = DEFAULT_URL

    all_items = params.items()
    items_included = filter(lambda x: x[1] is not None, all_items)
    included_dict = dict(items_included)
    included_json = json.dumps(included_dict)

    return '%s?q=%s' % (base, included_json)


class ApiServiceCursor(afscgap.cursor.Cursor):
    """Object for requests and interpreting API service results."""

    def __init__(self, query_url: str, limit: OPT_INT = None,
        start_offset: OPT_INT = None, filter_incomplete: bool = False,
        requestor: OPT_REQUESTOR = None):
        """Create a new cursor to manage a request.

        Args:
            query_url: The URL for the query without pagination information.
            limit: The maximum number of records to return per page.
            start_offset: The number of records being skipped (number of records
                prior to query_url).
            filter_incomplete: Flag indicating if incomplete records should be
                silently filtered. If true, they will not be returned during
                iteration and placed in the queue at get_invalid(). If false,
                they will be returned and those incomplete records'
                get_complete() will return false. Defaults to false.
            requestor: Strategy to make HTTP GET requests. If None, will default
                to requests.get.
        """
        self._query_url = query_url
        self._limit = limit
        self._start_offset = start_offset
        self._filter_incomplete = filter_incomplete
        self._queue: queue.Queue[afscgap.model.Record] = queue.Queue()
        self._invalid_queue: queue.Queue[dict] = queue.Queue()
        self._done = False

        if requestor:
            self._request_strategy = requestor
        else:
            self._request_strategy = afscgap.http_util.build_requestor()

        self._next_url = self.get_page_url()

    def get_base_url(self) -> str:
        """Get the URL at which the first page of query results can be found.

        Returns:
            The URL for the query without pagination information.
        """
        return self._query_url

    def get_limit(self) -> OPT_INT:
        """Get the page size limit.

        Returns:
            The maximum number of records to return per page.
        """
        return self._limit

    def get_start_offset(self) -> OPT_INT:
        """Get the number of inital records to ignore.

        Returns:
            The number of records being skipped at the start of the result set.
        """
        return self._start_offset

    def get_filtering_incomplete(self) -> bool:
        """Determine if this cursor is silently filtering incomplete records.

        Returns:
            Flag indicating if incomplete records should be silently filtered.
            If true, they will not be returned during iteration and placed in
            the queue at get_invalid(). If false, they will be returned and
            those incomplete records' get_complete() will return false.
        """
        return self._filter_incomplete

    def get_page_url(self, offset: OPT_INT = None,
        limit: OPT_INT = None) -> str:
        """Get a URL at which a page can be found using this cursor's base url.

        Args:
            offset: The number of records to skip prior to the page.
            limit: The maximum number of records to return in the page.
        Returns:
            URL at which the requested page can be found.
        """

        if offset is None:
            offset = self._start_offset

        if limit is None:
            limit = self._limit

        pagination_params = []

        if offset:
            pagination_params.append('offset=%d' % offset)

        if limit:
            pagination_params.append('limit=%d' % limit)

        if len(pagination_params) > 0:
            pagination_params_str = '&'.join(pagination_params)
            return self._query_url + '&' + pagination_params_str
        else:
            return self._query_url

    def get_page(self, offset: OPT_INT = None,
        limit: OPT_INT = None,
        ignore_invalid: bool = False) -> typing.List[afscgap.model.Record]:
        """Get a page using this cursor's base url.

        Args:
            offset: The number of records to skip prior to the page.
            limit: The maximum number of records to return in the page.
            ignore_invalid: Flag indicating how to handle invalid records. If
                true, will silently throw away records which could not be
                parsed. If false, will raise an exception if a record can not
                be parsed.

        Returns:
            Results from the page which, regardless of ignore_invalid, may
            contain a mixture of complete and incomplete records.
        """
        url = self.get_page_url(offset, limit)

        result = self._request_strategy(url)
        afscgap.http_util.check_result(result)

        result_parsed = result.json()
        items_raw = result_parsed['items']

        parsed_maybe = map(try_parse, items_raw)
        parsed_with_none = map(lambda x: x.get_parsed(), parsed_maybe)

        if ignore_invalid:
            parsed_no_none = filter(lambda x: x is not None, parsed_with_none)
            return list(parsed_no_none)  # type: ignore
        else:
            parsed = list(parsed_with_none)

            if None in parsed:
                raise RuntimeError('Encountered invalid record.')

            return parsed  # type: ignore

    def get_invalid(self) -> 'queue.Queue[dict]':
        """Get a queue of invalid / incomplete records found so far.

        Returns:
            Queue with dictionaries containing the raw data returned from the
            API that did not have valid values for all required fields. Note
            that this will include incomplete records as well if
            get_filtering_incomplete() is true and will not contain incomplete
            records otherwise.
        """
        return self._invalid_queue

    def to_dicts(self) -> typing.Iterable[dict]:
        """Create an iterator which converts Records to dicts.

        Returns:
            Iterator which returns dictionaries instead of Record objects but
            has otherwise the same beahavior as iterating in this Cursor
            directly.
        """
        return map(lambda x: x.to_dict(), self)

    def get_next(self) -> typing.Optional[afscgap.model.Record]:
        """Get the next value for this Cursor.

        Returns:
            The next value waiting if cached in the cursor's results queue or
            as just retrieved from a new page gathered by HTTP request. Will
            return None if no remain.
        """
        self._load_next_page()

        if self._queue.empty():
            return None
        else:
            return self._queue.get()

    def _load_next_page(self):
        """Request and parse additional results if they exist.

        Request and parse the next page(s) of results if one exists, putting it
        into the waiting results queues. Note that this will contiune to
        request new pages until finding valid results or no results remain.
        """
        while self._queue.empty() and not self._done:
            self._queue_next_page()

    def _queue_next_page(self):
        """Request the next page of waiting results.

        Request the next page of waiting results, putting newly returned data
        into the waiting queues and updating the next url / done internal
        state in the process.
        """
        if self._done:
            return

        result = self._request_strategy(self._next_url)
        afscgap.http_util.check_result(result)

        result_parsed = result.json()

        items_raw = result_parsed['items']

        items_parsed = map(try_parse, items_raw)

        # If we are filtering incomplete records, we will not allow incomplete.
        allow_incomplete = not self._filter_incomplete

        for parse_result in items_parsed:
            if parse_result.meets_requirements(allow_incomplete):
                self._queue.put(parse_result.get_parsed())
            else:
                self._invalid_queue.put(parse_result.get_raw_record())

        next_url = self._find_next_url(result_parsed)
        self._done = next_url is None
        self._next_url = next_url

    def _find_next_url(self, target: dict) -> OPT_STR:
        """Look for the URL with the next page of results if it exists.

        Args:
            target: The raw complete parsed JSON response from the API.

        Returns:
            The URL where the next page of results can be found via HTTP GET
            request or None if target indicates that no results remain.
        """
        if not target['hasMore']:
            return None

        links = target['links']
        matching = filter(lambda x: x['rel'] == 'next', links)
        matching_hrefs = map(lambda x: x['href'], matching)
        hrefs_realized = list(matching_hrefs)

        if len(hrefs_realized) == 0:
            raise RuntimeError('Could not find next URL but hasMore was true.')

        return hrefs_realized[0]


class ApiRecord(afscgap.model.Record):
    """Data structure describing a single record returned by the API."""

    def __init__(self, year: float, srvy: str, survey: str, survey_id: float,
        cruise: float, haul: float, stratum: float, station: str,
        vessel_name: str, vessel_id: float, date_time: str, latitude_dd: float,
        longitude_dd: float, species_code: float, common_name: str,
        scientific_name: str, taxon_confidence: str, cpue_kgha: OPT_FLOAT,
        cpue_kgkm2: OPT_FLOAT, cpue_kg1000km2: OPT_FLOAT, cpue_noha: OPT_FLOAT,
        cpue_nokm2: OPT_FLOAT, cpue_no1000km2: OPT_FLOAT, weight_kg: OPT_FLOAT,
        count: OPT_FLOAT, bottom_temperature_c: OPT_FLOAT,
        surface_temperature_c: OPT_FLOAT, depth_m: float,
        distance_fished_km: float, net_width_m: OPT_FLOAT,
        net_height_m: OPT_FLOAT, area_swept_ha: float, duration_hr: float,
        tsn: OPT_INT, ak_survey_id: int):
        """Create a new record.

        Args:
            year: Year for the survey in which this observation was made.
            srvy: The name of the survey in which this observation was made.
                NBS (N Bearing Sea), EBS (SE Bearing Sea), BSS (Bearing Sea
                Slope), or GOA (Gulf of Alaska)
            survey: Long form description of the survey in which the observation
                was made.
            survey_id: Unique numeric ID for the survey.
            cruise: An ID uniquely identifying the cruise in which the
                observation was made. Multiple cruises in a survey.
            haul: An ID uniquely identifying the haul in which this observation
                was made. Multiple hauls per cruises.
            stratum: Unique ID for statistical area / survey combination as
                described in the metadata or 0 if an experimental tow.
            station: Station associated with the survey.
            vessel_name: Unique ID describing the vessel that made this
                observation. This is left as a string but, in practice, is
                likely numeric.
            vessel_id: Name of the vessel at the time the observation was made
                with multiple names potentially associated with a vessel ID.
            date_time: The date and time of the haul which has been attempted to
                be transformed to an ISO 8601 string without timezone info.
                If it couldn’t be transformed, the original string.
            latitude_dd: Latitude in decimal degrees associated with the haul.
            longitude_dd: Longitude in decimal degrees associated with the haul.
            species_code: Unique ID associated with the species observed.
            common_name: The “common name” associated with the species observed.
            scientific_name: The “scientific name” associated with the species
                observed.
            taxon_confidence: Confidence flag regarding ability to identify
                species (High, Moderate, Low). In practice, this can also be
                Unassessed.
            cpue_kgha: Catch weight divided by net area (kg / hectares) if
                available. None if could not interpret as a float.
            cpue_kgkm2: Catch weight divided by net area (kg / km^2) if
                available. None if could not interpret as a float.
            cpue_kg1000km2: Catch weight divided by net area (kg / km^2 * 1000)
                if available. See metadata. None if could not interpret as a
                float.
            cpue_noha: Catch number divided by net sweep area if available
                (count / hectares). None if could not interpret as a float.
            cpue_nokm2: Catch number divided by net sweep area if available
                (count / km^2). See metadata. None if could not interpret as a
                float.
            cpue_no1000km2: Catch number divided by net sweep area if available
                (count / km^2 * 1000). See metadata. None if could not interpret
                as a float.
            weight_kg: Taxon weight (kg) if available. See metadata. None if
                could not interpret as a float.
            count: Total number of organism individuals in haul. None if could
                not interpret as a float.
            bottom_temperature_c: Bottom temperature associated with observation
                if available in Celsius. None if not given or could not
                interpret as a float.
            surface_temperature_c: Surface temperature associated with
                observation if available in Celsius. None if not given or could
                not interpret as a float.
            depth_m: Depth of the bottom in meters.
            distance_fished_km: Distance of the net fished as km.
            net_width_m: Distance of the net fished as m.
            net_height_m: Height of the net fished as m.
            area_swept_ha: Area covered by the net while fishing in hectares.
            duration_hr: Duration of the haul as number of hours.
            tsn: Taxonomic information system species code.
            ak_survey_id: AK identifier for the survey.
        """
        self._year = year
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
        self._species_code = species_code
        self._common_name = common_name
        self._scientific_name = scientific_name
        self._taxon_confidence = taxon_confidence
        self._cpue_kgha = cpue_kgha
        self._cpue_kgkm2 = cpue_kgkm2
        self._cpue_kg1000km2 = cpue_kg1000km2
        self._cpue_noha = cpue_noha
        self._cpue_nokm2 = cpue_nokm2
        self._cpue_no1000km2 = cpue_no1000km2
        self._weight_kg = weight_kg
        self._count = count
        self._bottom_temperature_c = bottom_temperature_c
        self._surface_temperature_c = surface_temperature_c
        self._depth_m = depth_m
        self._distance_fished_km = distance_fished_km
        self._net_width_m = net_width_m
        self._net_height_m = net_height_m
        self._area_swept_ha = area_swept_ha
        self._duration_hr = duration_hr
        self._tsn = tsn
        self._ak_survey_id = ak_survey_id

    def get_year(self) -> float:
        """Get the field labeled as year in the API.

        Returns:
            Year for the survey in which this observation was made.
        """
        return self._year

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
            Long form description of the survey in which the observation was
            made.
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
            An ID uniquely identifying the cruise in which the observation was
            made. Multiple cruises in a survey.
        """
        return self._cruise

    def get_haul(self) -> float:
        """Get the field labeled as haul in the API.

        Returns:
            An ID uniquely identifying the haul in which this observation was
            made. Multiple hauls per cruises.
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
            Unique ID describing the vessel that made this observation. This is
            left as a string but, in practice, is likely numeric.
        """
        return self._vessel_name

    def get_vessel_id(self) -> float:
        """Get the field labeled as vessel_id in the API.

        Returns:
            Name of the vessel at the time the observation was made with
            multiple names potentially associated with a vessel ID.
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

    def get_latitude(self, units: str = 'dd') -> float:
        """Get the field labeled as latitude_dd in the API.

        Args:
            units: The units to return this value in. Only supported is dd for
                degrees. Deafults to dd.

        Returns:
            Latitude in decimal degrees associated with the haul.
        """
        return afscgap.model.assert_float_present(
            afscgap.convert.convert_degrees(self._latitude_dd, units)
        )

    def get_longitude(self, units: str = 'dd') -> float:
        """Get the field labeled as longitude_dd in the API.

        Args:
            units: The units to return this value in. Only supported is dd for
                degrees. Deafults to dd.

        Returns:
            Longitude in decimal degrees associated with the haul.
        """
        return afscgap.model.assert_float_present(
            afscgap.convert.convert_degrees(self._longitude_dd, units)
        )

    def get_species_code(self) -> float:
        """Get the field labeled as species_code in the API.

        Returns:
            Unique ID associated with the species observed.
        """
        return self._species_code

    def get_common_name(self) -> str:
        """Get the field labeled as common_name in the API.

        Returns:
            The “common name” associated with the species observed. Example:
            Pacific glass shrimp.
        """
        return self._common_name

    def get_scientific_name(self) -> str:
        """Get the field labeled as scientific_name in the API.

        Returns:
            The “scientific name” associated with the species observed. Example:
            Pasiphaea pacifica.
        """
        return self._scientific_name

    def get_taxon_confidence(self) -> str:
        """Get the field labeled as taxon_confidence in the API.

        Returns:
            Confidence flag regarding ability to identify species (High,
            Moderate, Low). In practice, this can also be Unassessed.
        """
        return self._taxon_confidence

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
        return {
            'kg/ha': self._cpue_kgha,
            'kg/km2': self._cpue_kgkm2,
            'kg1000/km2': self._cpue_kg1000km2
        }[units]

    def get_cpue_count_maybe(self, units: str = 'kg/ha') -> OPT_FLOAT:
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
        return {
            'count/ha': self._cpue_noha,
            'count/km2': self._cpue_nokm2,
            'count1000/km2': self._cpue_no1000km2
        }[units]

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
        return afscgap.convert.convert_weight(self._weight_kg, units)

    def get_count_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as count in the API.

        Returns:
            Total number of organism individuals in haul. None if could not
            interpret as a float.
        """
        return self._count

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
        return afscgap.convert.convert_temperature(
            self._bottom_temperature_c,
            units
        )

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
        return afscgap.convert.convert_temperature(
            self._surface_temperature_c,
            units
        )

    def get_depth(self, units: str = 'm') -> float:
        """Get the field labeled as depth_m in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            Depth of the bottom.
        """
        return afscgap.model.assert_float_present(
            afscgap.convert.convert_distance(self._depth_m, units)
        )

    def get_distance_fished(self, units: str = 'm') -> float:
        """Get the field labeled as distance_fished_km in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            Distance of the net fished.
        """
        return afscgap.model.assert_float_present(
            afscgap.convert.convert_distance(
                self._distance_fished_km * 1000,
                units
            )
        )

    def get_net_width_maybe(self, units: str = 'm') -> OPT_FLOAT:
        """Get the field labeled as net_width_m in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            Distance of the net fished or None if not given.
        """
        return afscgap.convert.convert_distance(
            self._net_width_m,
            units
        )

    def get_net_height_maybe(self, units: str = 'm') -> OPT_FLOAT:
        """Get the field labeled as net_height_m in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            Height of the net fished or None if not given.
        """
        return afscgap.convert.convert_distance(
            self._net_height_m,
            units
        )

    def get_net_width(self, units: str = 'm') -> float:
        """Get the field labeled as net_width_m in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            Distance of the net fished after asserting it is given.
        """
        return afscgap.model.assert_float_present(
            self.get_net_width_maybe(units=units)
        )

    def get_net_height(self, units: str = 'm') -> float:
        """Get the field labeled as net_height_m in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to m.

        Returns:
            Height of the net fished after asserting it is given.
        """
        return afscgap.model.assert_float_present(
            self.get_net_height_maybe(units=units)
        )

    def get_area_swept(self, units: str = 'ha') -> float:
        """Get the field labeled as area_swept_ha in the API.

        Args:
            units: The units in which the area should be returned. Options:
                ha, m2, km2. Defaults to ha.

        Returns:
            Area covered by the net while fishing in desired units.
        """
        return afscgap.model.assert_float_present(
            afscgap.convert.convert_area(self._area_swept_ha, units)
        )

    def get_duration(self, units: str = 'hr') -> float:
        """Get the field labeled as duration_hr in the API.

        Args:
            units: The units in which the duration should be returned. Options:
                day, hr, min. Defaults to hr.

        Returns:
            Duration of the haul.
        """
        return afscgap.model.assert_float_present(
            afscgap.convert.convert_time(self._duration_hr, units)
        )

    def get_tsn(self) -> int:
        """Get the field labeled as tsn in the API.

        Returns:
            Taxonomic information system species code.
        """
        return afscgap.model.assert_int_present(self._tsn)

    def get_tsn_maybe(self) -> OPT_INT:
        """Get the field labeled as tsn in the API or None.

        Returns:
            Taxonomic information system species code if it could be parsed as
            an int and None otherwise.
        """
        return self._tsn

    def get_ak_survey_id(self) -> int:
        """Get the field labeled as ak_survey_id in the API.

        Returns:
            AK identifier for the survey.
        """
        return self._ak_survey_id

    def get_ak_survey_id_maybe(self) -> OPT_INT:
        """Get the field labeled as ak_survey_id in the API.

        Returns:
            AK identifier for the survey or None if not given.
        """
        return self._ak_survey_id

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
            metadata.
        """
        return afscgap.model.assert_float_present(
            self.get_cpue_weight_maybe(units=units)
        )

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
            hectares). See metadata.
        """
        return afscgap.model.assert_float_present(
            self.get_cpue_count_maybe(units=units)
        )

    def get_weight(self, units: str = 'kg') -> float:
        """Get the value of field weight_kg with validity assert.

        Args:
            units: The units in which the weight should be returned. Options are
                g, kg for grams and kilograms respectively. Deafults to kg.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Taxon weight (kg) if available. See metadata.
        """
        return afscgap.model.assert_float_present(
            self.get_weight_maybe(units=units)
        )

    def get_count(self) -> float:
        """Get the value of field count with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Total number of organism individuals in haul.
        """
        return afscgap.model.assert_float_present(self._count)

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
        return afscgap.model.assert_float_present(
            self.get_bottom_temperature_maybe(units=units)
        )

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
        return afscgap.model.assert_float_present(
            self.get_surface_temperature_maybe(units=units)
        )

    def is_complete(self) -> bool:
        """Determine if this record has all of its values filled in.

        Returns:
            True if all optional fields have a parsed value with the expected
            type and false otherwise.
        """
        optional_fields = [
            self._cpue_kgha,
            self._cpue_kgkm2,
            self._cpue_kg1000km2,
            self._cpue_noha,
            self._cpue_nokm2,
            self._cpue_no1000km2,
            self._weight_kg,
            self._count,
            self._bottom_temperature_c,
            self._surface_temperature_c,
            self._tsn
        ]

        has_none = None in optional_fields
        all_fields_present = not has_none
        has_valid_date_time = afscgap.convert.is_iso8601(self._date_time)

        return all_fields_present and has_valid_date_time


def parse_record(target: dict) -> afscgap.model.Record:
    """Parse a record from a returned item dictionary.

    Args:
        target: The dictionary from which values should be read.

    Raises:
        ValueError: Exception raised if a field has an unexpected type or cannot
            be parsed to an expected type.
        KeyError: Exception raised if an expected field is not found.

    Returns:
        Newly parsed record.
    """
    year = float(target['year'])
    srvy = str(target['srvy'])
    survey = str(target['survey'])
    survey_id = float(target['survey_id'])
    cruise = float(target['cruise'])
    haul = float(target['haul'])
    stratum = float(target['stratum'])
    station = str(target['station'])
    vessel_name = str(target['vessel_name'])
    vessel_id = float(target['vessel_id'])
    date_time = afscgap.convert.convert_to_iso8601(str(target['date_time']))
    latitude_dd = float(target['latitude_dd'])
    longitude_dd = float(target['longitude_dd'])
    species_code = float(target['species_code'])
    common_name = str(target['common_name'])
    scientific_name = str(target['scientific_name'])
    taxon_confidence = str(target['taxon_confidence'])
    cpue_kgha = afscgap.model.get_opt_float(target['cpue_kgha'])
    cpue_kgkm2 = afscgap.model.get_opt_float(target['cpue_kgkm2'])
    cpue_kg1000km2 = afscgap.model.get_opt_float(target['cpue_kg1000km2'])
    cpue_noha = afscgap.model.get_opt_float(target['cpue_noha'])
    cpue_nokm2 = afscgap.model.get_opt_float(target['cpue_nokm2'])
    cpue_no1000km2 = afscgap.model.get_opt_float(target['cpue_no1000km2'])
    weight_kg = afscgap.model.get_opt_float(target['weight_kg'])
    count = afscgap.model.get_opt_float(target['count'])
    bottom_temperature_c = afscgap.model.get_opt_float(
        target['bottom_temperature_c']
    )
    surface_temperature_c = afscgap.model.get_opt_float(
        target['surface_temperature_c']
    )
    depth_m = float(target['depth_m'])
    distance_fished_km = float(target['distance_fished_km'])
    net_width_m = afscgap.model.get_opt_float(target['net_width_m'])
    net_height_m = afscgap.model.get_opt_float(target['net_height_m'])
    area_swept_ha = float(target['area_swept_ha'])
    duration_hr = float(target['duration_hr'])
    tsn = afscgap.model.get_opt_int(target['tsn'])
    ak_survey_id = int(target['ak_survey_id'])

    return ApiRecord(
        year,
        srvy,
        survey,
        survey_id,
        cruise,
        haul,
        stratum,
        station,
        vessel_name,
        vessel_id,
        date_time,
        latitude_dd,
        longitude_dd,
        species_code,
        common_name,
        scientific_name,
        taxon_confidence,
        cpue_kgha,
        cpue_kgkm2,
        cpue_kg1000km2,
        cpue_noha,
        cpue_nokm2,
        cpue_no1000km2,
        weight_kg,
        count,
        bottom_temperature_c,
        surface_temperature_c,
        depth_m,
        distance_fished_km,
        net_width_m,
        net_height_m,
        area_swept_ha,
        duration_hr,
        tsn,
        ak_survey_id
    )


class ParseRecordResult:
    """Object with the results of trying to parse a record from the API.

    Object with the results of trying to parse a record from the API, allowing
    for internal record keeping within the afscgap library. Note that this is
    an internal data structure and not expected to reach client code.
    """

    def __init__(self, raw_record: dict,
        parsed: typing.Optional[afscgap.model.Record]):
        """Create a new record of a parse attempt.

        Args:
            raw_record: Item from the API's JSON response payload that the
                library attempted to parse.
            parsed: The Record read if successful or None if it could not be
                parsed.
        """
        self._raw_record = raw_record
        self._parsed = parsed

    def get_raw_record(self) -> dict:
        """Get the input raw JSON record.

        Returns:
            Item from the API's JSON response payload that the library attempted
            to parse.
        """
        return self._raw_record

    def get_parsed(self) -> typing.Optional[afscgap.model.Record]:
        """Get the record that was parsed if successful.

        Returns:
            The Record read if successful or None if it could not be parsed.
        """
        return self._parsed

    def meets_requirements(self, allow_incomplete: bool) -> bool:
        """Determine if this record is "valid" according to the client code.

        Args:
            allow_incomplete: Flag indicating if incomplete records are
                considered valid. If true, incomplete records will be considered
                valid. If false, incomplete records will be considered invalid.
                Incomplete means missing any optional fields or failing to
                achieve an ISO 8601 date_time value.

        Returns:
            True if this record was parsed successfully and meets the
            requirements specified for being considered "valid" per the
            allow_incomplete flag. False otherwise.
        """
        if self._parsed is None:
            return False

        return allow_incomplete or self._parsed.is_complete()


def try_parse(target: dict) -> ParseRecordResult:
    """Attempt parsing a Record from an input item dictionary from the API.

    Params:
        target: The dictionary from which to parse. This should be an item
            from the items array in the returned JSON payload from the API.

    Returns:
        Parse result describing if the dictionary was parsed successfully.
    """
    try:
        return ParseRecordResult(target, parse_record(target))
    except (ValueError, KeyError):
        return ParseRecordResult(target, None)
