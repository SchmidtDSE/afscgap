"""
Tools for inferring missing, negative, or zero catch records.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import copy
import csv
import io
import itertools
import queue
import typing

import afscgap.convert
import afscgap.client
import afscgap.cursor
import afscgap.http_util
import afscgap.model
import afscgap.query_util

from afscgap.typesdef import OPT_FLOAT
from afscgap.typesdef import OPT_INT
from afscgap.typesdef import OPT_REQUESTOR
from afscgap.typesdef import OPT_STR

DEFAULT_HAULS_URL = 'https://pyafscgap.org/community/hauls.csv'
SPECIES_DICT = typing.Dict[str, afscgap.model.SpeciesRecord]

HAUL_LIST = typing.List[afscgap.model.Haul]
OPT_HAUL_LIST = typing.Optional[HAUL_LIST]
HAUL_FILTERABLE_FIELDS = [
    'year',
    'srvy',
    'survey',
    'survey_id',
    'cruise',
    'haul',
    'stratum',
    'station',
    'vessel_name',
    'vessel_id',
    'date_time',
    'latitude_dd',
    'longitude_dd',
    'bottom_temperature_c',
    'surface_temperature_c',
    'depth_m',
    'distance_fished_km',
    'net_width_m',
    'net_height_m',
    'area_swept_ha',
    'duration_hr'
]

PARAMS_CHECKER = typing.Callable[[afscgap.model.Haul], bool]


def build_inference_cursor(params: dict, inner_cursor: afscgap.cursor.Cursor,
    requestor: OPT_REQUESTOR = None, hauls_url: afscgap.client.OPT_STR = None,
    hauls_prefetch: OPT_HAUL_LIST = None):
    """Build a cursor which infers zero catch records.

    Args:
        params: Dictionary of filters to apply to the query where a value of
            None means no filter should be applied on that field.
        inner_cursor: Cursor which yields records which, when appearing, should
            not be later inferred as zero catch records.
        requestor: Strategy to make HTTP GET requests. If None, will default
            to requests.get.
        hauls_url: The URL at which the Hauls file can be found or None to use
            a default. Defaults to None.
        hauls_prefetch: List of hauls data to use. If None, will request from
            hauls_url. If not None, will use this instead.

    Returns:
        Cursor which 1) first iterates over the inner_cursor and then
        2) provides inferred zero catch records (for any hauls without observed
        data from inner_cursor for a species).
    """
    params_safe = copy.deepcopy(params)

    if 'date_time' in params_safe:
        params_safe['date_time'] = afscgap.convert.convert_from_iso8601(
            params_safe['date_time']
        )

    if hauls_prefetch is not None:
        hauls_data = hauls_prefetch
    else:
        hauls_data = get_hauls_data(
            params_safe,
            requestor=requestor,
            hauls_url=hauls_url
        )

    return NegativeInferenceCursorDecorator(inner_cursor, hauls_data)


def build_params_checker(params: dict) -> PARAMS_CHECKER:
    """Build a function that checks if a single Haul record should be filtered.

    Args:
        params: Dictionary of filters to apply to the query where a value of
            None means no filter should be applied on that field.

    Returns:
        Function which returns true if the record given to it should be included
        (is not filtered out) or false if it should be excluded from results to
        meet a query requirement (is filtered out).
    """

    def build_query_function(key: str, checker):
        return lambda target: checker(target[key])

    params_py = afscgap.query_util.interpret_query_to_py(params)
    params_py_items = params_py.items()
    params_py_items_given = filter(lambda x: x[1] is not None, params_py_items)
    params_py_items_valid = filter(
        lambda x: x[0] in HAUL_FILTERABLE_FIELDS,
        params_py_items_given
    )
    params_funcs = map(
        lambda x: build_query_function(x[0], x[1]),
        params_py_items_valid
    )
    params_funcs_realized = list(params_funcs)

    def check_all(target: afscgap.model.Haul) -> bool:
        target_dict = target.to_dict()
        not_allowed = filter(
            lambda x: not x(target_dict),
            params_funcs_realized
        )
        num_not_allowed = sum(map(lambda x: 1, not_allowed))
        return num_not_allowed == 0

    return check_all


def get_hauls_data(params: dict, requestor: OPT_REQUESTOR = None,
    hauls_url: afscgap.client.OPT_STR = None) -> HAUL_LIST:
    """Download Hauls from a URL and apply a filter specified by params.

    Args:
        params: Dictionary of filters to apply to the query where a value of
            None means no filter should be applied on that field.
        requestor: Strategy to make HTTP GET requests. If None, will default
            to requests.get.
        hauls_url: The URL at which the Hauls file can be found or None to use
            a default. Defaults to None.

    Returns:
        List of Haul data after having applied the filters described by params.
    """
    if hauls_url is None:
        hauls_url = DEFAULT_HAULS_URL

    params_checker = build_params_checker(params)

    if requestor is None:
        requestor = afscgap.http_util.build_requestor()

    response = requestor(hauls_url)
    afscgap.http_util.check_result(response)

    response.encoding = 'utf-8'
    response_io = io.StringIO(response.text, newline='')

    response_rows = csv.DictReader(response_io)
    response_hauls = map(parse_haul, response_rows)
    response_hauls_filtered = filter(params_checker, response_hauls)

    return list(response_hauls_filtered)


class NegativeInferenceCursorDecorator(afscgap.cursor.Cursor):
    """Cursor augmenting another cursor with inferred negative records.

    Cursor which exausts an inner cursor and then supplies inferred zero catch
    records. Specifically, a Cursor which 1) first iterates over the
    inner_cursor and then 2) provides inferred zero catch records (for any hauls
    without observed data from inner_cursor for a species).
    """

    def __init__(self, inner_cursor: afscgap.cursor.Cursor,
        hauls_data: HAUL_LIST):
        """Decorate a cursor.

        Args:
            inner_cursor: The cursor to augment and from which to observe
                presence data.
            hauls_data: Metadata on all hauls relevant to the query.
        """
        self._inner_cursor = inner_cursor
        self._hauls_data = hauls_data

        self._started_inference = False
        self._inferences_iter: typing.Iterator[afscgap.model.Record] = iter([])

        self._species_seen: SPECIES_DICT = dict()
        self._species_hauls_seen: typing.Set[str] = set()
        self._ak_survey_ids: typing.Dict[str, int] = dict()

    def get_base_url(self) -> str:
        """Get the URL at which the first page of query results can be found.

        Returns:
            The URL for the query without pagination information.
        """
        return self._inner_cursor.get_base_url()

    def get_limit(self) -> OPT_INT:
        """Get the page size limit.

        Returns:
            The maximum number of records to return per page.
        """
        return self._inner_cursor.get_limit()

    def get_start_offset(self) -> OPT_INT:
        """Get the number of inital records to ignore.

        Returns:
            The number of records being skipped at the start of the result set.
        """
        return self._inner_cursor.get_start_offset()

    def get_filtering_incomplete(self) -> bool:
        """Determine if this cursor is silently filtering incomplete records.

        Returns:
            Flag indicating if incomplete records should be silently filtered.
            If true, they will not be returned during iteration and placed in
            the queue at get_invalid(). If false, they will be returned and
            those incomplete records' get_complete() will return false.
        """
        return self._inner_cursor.get_filtering_incomplete()

    def get_page_url(self, offset: OPT_INT = None,
        limit: OPT_INT = None) -> str:
        """Get a URL at which a page can be found using this cursor's base url.

        Args:
            offset: The number of records to skip prior to the page.
            limit: The maximum number of records to return in the page.
        Returns:
            URL at which the requested page can be found.
        """
        return self._inner_cursor.get_page_url(offset=offset, limit=limit)

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
        return self._inner_cursor.get_page(
            offset=offset,
            limit=limit,
            ignore_invalid=ignore_invalid
        )

    def get_invalid(self) -> 'queue.Queue[dict]':
        """Get a queue of invalid / incomplete records found so far.

        Returns:
            Queue with dictionaries containing the raw data returned from the
            API that did not have valid values for all required fields. Note
            that this will include incomplete records as well if
            get_filtering_incomplete() is true and will not contain incomplete
            records otherwise.
        """
        return self._inner_cursor.get_invalid()

    def to_dicts(self) -> typing.Iterable[dict]:
        """Create an iterator which converts Records to dicts.

        Returns:
            Iterator which returns dictionaries instead of Record objects but
            has otherwise the same beahavior as iterating in this Cursor
            directly.
        """
        return self._inner_cursor.to_dicts()

    def get_next(self) -> typing.Optional[afscgap.model.Record]:
        """Get the next value for this Cursor.

        Returns:
            The next value waiting if cached in the cursor's results queue or
            as just retrieved from a new page gathered by HTTP request. Will
            return None if no remain.
        """
        if self._started_inference:
            return self._get_next_inferred()
        else:
            next_record_maybe = self._inner_cursor.get_next()

            if next_record_maybe:
                self._record_record_meta(next_record_maybe)
                return next_record_maybe
            else:
                self._start_inference()
                return self._get_next_inferred()

    def _record_record_meta(self, record: afscgap.model.Record):
        """Record metadata from a record, indicating a haul / species was seen.

        Args:
            record: The record observed.
        """
        key_with_species = self._get_haul_key(
            record,
            species=record.get_scientific_name()
        )
        self._species_hauls_seen.add(key_with_species)

        scientific_name = record.get_scientific_name()
        common_name = record.get_common_name()
        species_code = record.get_species_code()
        tsn = record.get_tsn_maybe()

        self._species_seen[scientific_name] = afscgap.model.SpeciesRecord(
            scientific_name,
            common_name,
            species_code,
            tsn
        )

        survey = record.get_survey()
        ak_survey_id = record.get_ak_survey_id()

        self._ak_survey_ids[survey] = ak_survey_id

    def _get_haul_key(self, record: afscgap.model.HaulKeyable,
        species: OPT_STR = None) -> str:
        """Get a string uniquely identifying an individual haul.

        Args:
            record: The record from which to derive a haul key.
            speices: If given, include the species in the key. If not given, the
                key will refer to the entire haul across all species. Note that
                this should be the scientific name for a species.

        Returns:
            String uniquely identifying a haul across the entire dataset.
        """
        ship_info_vals = [
            record.get_year(),
            record.get_vessel_id(),
            record.get_cruise(),
            record.get_haul()
        ]
        ship_info_vals_int = map(lambda x: round(x), ship_info_vals)
        ship_info_vals_str = map(str, ship_info_vals_int)
        ship_info_vals_csv = ','.join(ship_info_vals_str)

        without_species = '%s:%s' % (record.get_srvy(), ship_info_vals_csv)

        if species:
            return '%s/%s' % (without_species, species)
        else:
            return without_species

    def _start_inference(self):
        """Prepare to start inferrence.

        Indicate that the inner cursor is exhaused, preparing to run inferrence.
        """
        hauls_seen_with_key = map(
            lambda x: (self._get_haul_key(x), x),
            self._hauls_data
        )
        hauls_seen_by_key = dict(hauls_seen_with_key)

        scientific_names_seen = self._species_seen.keys()
        missing_keys = self._get_missing_keys(
            hauls_seen_by_key.keys(),
            scientific_names_seen,
            self._species_hauls_seen
        )

        missing_haul_keys_and_species_tuple = map(
            lambda x: x.split('/'),
            missing_keys
        )
        missing_haul_keys_and_species = map(
            lambda x: {'haulKey': x[0], 'species': x[1]},
            missing_haul_keys_and_species_tuple
        )
        missing_hauls_and_species = map(
            lambda x: {
                'haul': hauls_seen_by_key[x['haulKey']],
                'species': x['species']
            },
            missing_haul_keys_and_species
        )

        def make_inference_record(target: typing.Dict) -> afscgap.model.Record:
            scientific_name = target['species']
            haul = target['haul']

            species_record = self._species_seen[scientific_name]
            common_name = species_record.get_common_name()
            species_code = species_record.get_species_code()
            tsn = species_record.get_tsn()

            ak_survey_id = self._ak_survey_ids.get(haul.get_survey(), None)

            return ZeroCatchHaulDecorator(
                haul,
                scientific_name,
                common_name,
                species_code,
                tsn,
                ak_survey_id
            )

        inference_map = map(make_inference_record, missing_hauls_and_species)

        self._inferences_iter = iter(inference_map)
        self._started_inference = True

    def _get_next_inferred(self) -> typing.Optional[afscgap.model.Record]:
        """Get the next inferred zero catch record.

        Raises:
            StopIteration: Raised if no records left to infer.
            AssertionError: Raised if the cursor has not yet started inference.

        Returns:
            Next inferred absence data record.
        """
        assert self._started_inference

        try:
            return next(self._inferences_iter)
        except StopIteration:
            return None

    def _get_missing_keys(self, hauls_seen: typing.Iterable[str],
        scientific_names_seen: typing.Iterable[str],
        species_hauls_seen: typing.Set[str]) -> typing.Iterable[str]:
        """Determine which species haul keys were expected but not observed.

        Args:
            hauls_seen: The haus seen (non-species keys).
            scientific_names_seen: The name of the scientific names for species
                observed across the entire dataset yielded by the user query.
            species_hauls_seen: The haul / species keys or combinations actually
                observed.

        Returns:
            Haul / species keys expected but not found in species_hauls_seen
            given the hauls described in hauls_seen and the species seen in
            scientific_names_seen.
        """
        hauls_with_names = itertools.product(
            hauls_seen,
            scientific_names_seen
        )
        hauls_with_names_str = map(lambda x: '%s/%s' % x, hauls_with_names)
        missing_keys = filter(
            lambda x: x not in species_hauls_seen,
            hauls_with_names_str
        )
        return missing_keys


class ZeroCatchHaulDecorator(afscgap.model.Record):
    """Decorator for a Haul that makes it operate like a zero catch Record."""

    def __init__(self, haul: afscgap.model.Haul, scientific_name: str,
        common_name: str, species_code: float, tsn: OPT_INT,
        ak_survey_id: OPT_INT):
        """Decorate a Haul to conform to the Record interface.

        Args:
            haul: The haul to decorate.
            scientific_name: The scientific name of the species to be associated
                with this record.
            common_name: The common name of the species to be associated with
                this record.
            species_code: The species code of the species to be associated with
                this record.
            tsn: The taxonomic information system species code to be associated
                with this record if known.
            ak_survey_id: The AK survey ID to be associated with this record if
                known.
        """
        self._haul = haul
        self._scientific_name = scientific_name
        self._common_name = common_name
        self._species_code = species_code
        self._tsn = tsn
        self._ak_survey_id = ak_survey_id

    def get_year(self) -> float:
        """Get the year of the start date for the haul.

        Returns:
            Year for the haul.
        """
        return self._haul.get_year()

    def get_srvy(self) -> str:
        """Get the field labeled as srvy in the API.

        Returns:
            The name of the survey in which this haul was conducted. NBS (N
            Bearing Sea), EBS (SE Bearing Sea), BSS (Bearing Sea Slope), or GOA
            (Gulf of Alaska)
        """
        return self._haul.get_srvy()

    def get_survey(self) -> str:
        """Get the field labeled as survey in the API.

        Returns:
            Long form description of the survey in which the haul was conducted.
        """
        return self._haul.get_survey()

    def get_survey_id(self) -> float:
        """Get the field labeled as survey_id in the API.

        Returns:
            Unique numeric ID for the survey.
        """
        return self._haul.get_survey_id()

    def get_cruise(self) -> float:
        """Get the field labeled as cruise in the API.

        Returns:
            An ID uniquely identifying the cruise in which the haul was made.
            Multiple cruises in a survey.
        """
        return self._haul.get_cruise()

    def get_haul(self) -> float:
        """Get the field labeled as haul in the API.

        Returns:
            An ID uniquely identifying the haul. Multiple hauls per cruises.
        """
        return self._haul.get_haul()

    def get_stratum(self) -> float:
        """Get the field labeled as stratum in the API.

        Returns:
            Unique ID for statistical area / survey combination as described in
            the metadata or 0 if an experimental tow.
        """
        return self._haul.get_stratum()

    def get_station(self) -> str:
        """Get the field labeled as station in the API.

        Returns:
            Station associated with the survey.
        """
        return self._haul.get_station()

    def get_vessel_name(self) -> str:
        """Get the field labeled as vessel_name in the API.

        Returns:
            Unique ID describing the vessel that made this haul. Note this is
            left as a string but, in practice, is likely numeric.
        """
        return self._haul.get_vessel_name()

    def get_vessel_id(self) -> float:
        """Get the field labeled as vessel_id in the API.

        Returns:
            Name of the vessel at the time the haul was made. Note that there
            may be multiple names potentially associated with a vessel ID.
        """
        return self._haul.get_vessel_id()

    def get_date_time(self) -> str:
        """Get the field labeled as date_time in the API.

        Returns:
            The date and time of the haul which has been attempted to be
            transformed to an ISO 8601 string without timezone info. If it
            couldn’t be transformed, the original string is reported.
        """
        return self._haul.get_date_time()

    def get_latitude(self, units: str = 'dd') -> float:
        """Get the field labeled as latitude_dd in the API.

        Args:
            units: The units to return this value in. Only supported is dd for
                degrees. Deafults to dd.

        Returns:
            Latitude in decimal degrees associated with the haul.
        """
        return afscgap.model.assert_float_present(
            afscgap.convert.convert_degrees(
                self._haul.get_latitude_dd(),
                units
            )
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
            afscgap.convert.convert_degrees(
                self._haul.get_longitude_dd(),
                units
            )
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
        """Get rating of taxon identification confidence.

        Returns:
            Always returns Unassessed.
        """
        return 'Unassessed'

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
        return 0

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
        return 0

    def get_weight_maybe(self, units='kg') -> OPT_FLOAT:
        """Get the field labeled as weight_kg in the API.

        Args:
            units: The units in which the weight should be returned. Options are
                g, kg for grams and kilograms respectively. Deafults to kg.

        Returns:
            Taxon weight if available. See metadata. None if could not
            interpret as a float. If an inferred zero catch record, will be
            zero.
        """
        return 0

    def get_count_maybe(self) -> OPT_FLOAT:
        """Get total number of organism individuals in haul.

        Returns:
            Always returns 0.
        """
        return 0

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
            self._haul.get_bottom_temperature_c_maybe(),
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
            self._haul.get_surface_temperature_c_maybe(),
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
            afscgap.convert.convert_distance(self._haul.get_depth_m(), units)
        )

    def get_distance_fished(self, units: str = 'm') -> float:
        """Get the field labeled as distance_fished_km in the API.

        Args:
            units: The units in which the distance should be returned. Options:
                m or km for meters and kilometers respectively. Defaults to km.

        Returns:
            Distance of the net fished.
        """
        return afscgap.model.assert_float_present(
            afscgap.convert.convert_distance(
                self._haul.get_distance_fished_km() * 1000,
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
            self._haul.get_net_width_m_maybe(),
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
            self._haul.get_net_height_m_maybe(),
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
            afscgap.convert.convert_area(
                self._haul.get_area_swept_ha(),
                units
            )
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
            afscgap.convert.convert_time(self._haul.get_duration_hr(), units)
        )

    def get_tsn(self) -> int:
        """Get taxonomic information system species code.

        Returns:
            TSN for species.
        """
        return afscgap.model.assert_int_present(self._tsn)

    def get_tsn_maybe(self) -> OPT_INT:
        """Get taxonomic information system species code.

        Returns:
            TSN for species.
        """
        return self._tsn

    def get_ak_survey_id(self) -> int:
        """Get the field labeled as ak_survey_id in the API.

        Returns:
            AK survey ID if found.
        """
        return afscgap.model.assert_int_present(self._ak_survey_id)

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
            metadata. Always returns 0.
        """
        return 0

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
            hectares). See metadata. Always returns 0.
        """
        return 0

    def get_weight(self, units: str = 'kg') -> float:
        """Get the value of field weight_kg with validity assert.

        Args:
            units: The units in which the weight should be returned. Options are
                g, kg for grams and kilograms respectively. Deafults to kg.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Taxon weight (kg) if available. See metadata. Always returns 0.
        """
        return 0

    def get_count(self) -> float:
        """Get the value of field count with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Always returns 0
        """
        return 0

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
        tsn_given = self._tsn is not None
        ak_survey_id_given = self._ak_survey_id is not None
        return tsn_given and ak_survey_id_given and self._haul.is_complete()


def parse_haul(target: dict) -> afscgap.model.Haul:
    """Parse a Haul record from a row in the community Hauls flat file.

    Args:
        target: Dict describing a single row from the community-maintained
            Hauls flat file.

    Returns:
        Haul record constructed from the input row.
    """
    srvy = str(target['Srvy'])
    survey = str(target['Survey'])
    survey_id = float(target['Survey Id'])
    cruise = float(target['Cruise'])
    haul = float(target['Haul'])
    stratum = float(target['Stratum'])
    station = str(target['Station'])
    vessel_name = str(target['Vessel Name'])
    vessel_id = float(target['Vessel Id'])
    date_time = str(afscgap.convert.convert_to_iso8601(target['Date Time']))
    latitude_dd = float(target['Latitude Dd'])
    longitude_dd = float(target['Longitude Dd'])
    bottom_temperature_c = afscgap.model.get_opt_float(
        target['Bottom Temperature C']
    )
    surface_temperature_c = afscgap.model.get_opt_float(
        target['Surface Temperature C']
    )
    depth_m = float(target['Depth M'])
    distance_fished_km = float(target['Distance Fished Km'])
    net_width_m = afscgap.model.get_opt_float(target['Net Width M'])
    net_height_m = afscgap.model.get_opt_float(target['Net Height M'])
    area_swept_ha = float(target['Area Swept Ha'])
    duration_hr = float(target['Duration Hr'])

    return afscgap.model.Haul(
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
        bottom_temperature_c,
        surface_temperature_c,
        depth_m,
        distance_fished_km,
        net_width_m,
        net_height_m,
        area_swept_ha,
        duration_hr
    )
