"""
Tools for inferring missing, negative, or zero catch records.

(c) 2023 The Eric and Wendy Schmidt Center for Data Science and the Environment
at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.txt.
"""
import itertools
import typing

import afscgap.client
import afscgap.model

from afscgap.util import OPT_INT
from afscgap.util import OPT_REQUESTOR
from afscgap.util import OPT_STR


class SpeciesRecord:

    def __init__(self, scientific_name: str, common_name: str,
        species_code: float, tsn: OPT_INT):
        self._scientific_name = scientific_name
        self._common_name = common_name
        self._species_code = species_code
        self._tsn = tsn
    
    def get_scientific_name(self) -> str:
        return self._scientific_name
    
    def get_common_name(self) -> str:
        return self._common_name
    
    def get_species_code(self) -> float:
        return self._species_code
    
    def get_tsn(self) -> OPT_INT:
        return self._tsn


class NegativeInferenceCursorDecorator(afscgap.client.Cursor):

    def __init__(self, inner_cursor: afscgap.client.Cursor,
        hauls_data: typing.List[afscgap.model.Haul]):
        self._inner_cursor = inner_cursor

        if hauls_data:
            self._hauls_getter = lambda: hauls_data
        else:
            self._hauls_getter = lambda: self._get_hauls(requestor, hauls_url)

        self._started_inference = False
        self._inferences_iter: typing.Iterator[afscgap.model.Record] = iter([])

        self._species_seen: typing.Dict[str, SpeciesRecord] = dict()
        self._species_hauls_seen: typing.Set[str] = set()
        self._ak_survey_ids: typing.Dict[str, int]

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
        return self._inner_cursor.get_page_url(
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
        key_with_species = self._get_haul_key(
            record,
            species=record.get_scientific_name()
        )
        self._species_hauls_seen.add(key_with_species)

        scientific_name = record.get_scientific_name()
        common_name = record.get_common_name()
        species_code = record.get_species_code()
        tsn = record.get_tsn_maybe()

        self._species_seen[scientific_name] = SpeciesRecord(
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
        ship_info_vals = [
            record.get_year(),
            record.get_vessel_id(),
            record.get_cruise(),
            record.get_haul()
        ]
        ship_info_vals_int = map(lambda x: round(x), key_vals)
        ship_info_vals_str = map(str, key_vals_int)
        ship_info_vals_csv = ','.join(key_vals_int)

        without_species = '%s:%s' % (record.get_srvy(), key_num_vals_csv)

        if include_species:
            return '%s/%s' % (without_species, species)
        else:
            return without_species

    def _start_inference(self):
        hauls_seen = self._get_hauls()
        hauls_seen_with_key = map(
            lambda x: (self._get_haul_key(x), x),
            hauls_seen
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
            missing_keys
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
        try:
            return next(self._inferences_iter)
        except StopIteration:
            return None

    def _get_missing_keys(self, hauls_seen: typing.Iterable[str],
        scientific_names_seen: typing.Iterable[str],
        species_hauls_seen: typing.Set[str]) -> typing.Iterable[str]:
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

    def __init__(self, haul: afscgap.model.Haul, scientific_name: str,
        common_name: str, species_code: float, tsn: OPT_INT,
        ak_survey_id: OPT_INT):
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

    def get_latitude_dd(self) -> float:
        """Get the field labeled as latitude_dd in the API.

        Returns:
            Latitude in decimal degrees associated with the haul.
        """
        return self._haul.get_latitude_dd()

    def get_longitude_dd(self) -> float:
        """Get the field labeled as longitude_dd in the API.

        Returns:
            Longitude in decimal degrees associated with the haul.
        """
        return self._haul.get_longitude_dd()

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

    def get_cpue_kgha_maybe(self) -> OPT_FLOAT:
        """Get catch weight divided by net area (kg / hectares).

        Returns:
            Always returns 0.
        """
        return 0

    def get_cpue_kgkm2_maybe(self) -> OPT_FLOAT:
        """Get catch weight divided by net area (kg / km^2).

        Returns:
            Always returns 0.
        """
        return 0

    def get_cpue_kg1000km2_maybe(self) -> OPT_FLOAT:
        """Get catch weight divided by net area (kg / km^2 * 1000).

        Returns:
            Always returns 0.
        """
        return 0

    def get_cpue_noha_maybe(self) -> OPT_FLOAT:
        """Get catch number divided by net sweep area.

        Returns:
            Always returns 0.
        """
        return 0

    def get_cpue_nokm2_maybe(self) -> OPT_FLOAT:
        """Get catch number divided by net sweep area.

        Returns:
            Always returns 0.
        """
        return 0

    def get_cpue_no1000km2_maybe(self) -> OPT_FLOAT:
        """Get catch number divided by net sweep area.

        Returns:
            Always returns 0.
        """
        return 0

    def get_weight_kg_maybe(self) -> OPT_FLOAT:
        """Get taxon weight (kg).

        Returns:
            Always returns 0.
        """
        return 0

    def get_count_maybe(self) -> OPT_FLOAT:
        """Get total number of organism individuals in haul.

        Returns:
            Always returns 0.
        """
        return 0

    def get_bottom_temperature_c_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as bottom_temperature_c in the API.

        Returns:
            Bottom temperature associated with haul if available in
            Celsius. None if not given or could not interpret as a float.
        """
        return self._haul.get_bottom_temperature_c_maybe()

    def get_surface_temperature_c_maybe(self) -> OPT_FLOAT:
        """Get the field labeled as surface_temperature_c in the API.

        Returns:
            Surface temperature associated with haul if available in
            Celsius. None if not given or could not interpret as a float.
        """
        return self._haul.get_surface_temperature_c_maybe()

    def get_depth_m(self) -> float:
        """Get the field labeled as depth_m in the API.

        Returns:
            Depth of the bottom in meters.
        """
        return self._haul.get_depth_m()

    def get_distance_fished_km(self) -> float:
        """Get the field labeled as distance_fished_km in the API.

        Returns:
            Distance of the net fished as km.
        """
        return self._haul.get_distance_fished_km()

    def get_net_width_m(self) -> float:
        """Get the field labeled as net_width_m in the API.

        Returns:
            Distance of the net fished as m.
        """
        return self._haul.get_net_width_m()

    def get_net_height_m(self) -> float:
        """Get the field labeled as net_height_m in the API.

        Returns:
            Height of the net fished as m.
        """
        return self._haul.get_area_swept_m()

    def get_area_swept_ha(self) -> float:
        """Get the field labeled as area_swept_ha in the API.

        Returns:
            Area covered by the net while fishing in hectares.
        """
        return self._haul.get_area_swept_ha()

    def get_duration_hr(self) -> float:
        """Get the field labeled as duration_hr in the API.

        Returns:
            Duration of the haul as number of hours.
        """
        return self._haul.get_duration_hr()

    def get_tsn(self) -> int:
        """Get taxonomic information system species code.

        Returns:
            TSN for species.
        """
        assert self._tsn is not None
        return self._tsn

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
        assert self._ak_survey_id is not None
        return self._ak_survey_id

    def get_ak_survey_id_maybe(self) -> OPT_INT:
        """Get the field labeled as ak_survey_id in the API.

        Returns:
            AK identifier for the survey or None if not given.
        """
        return self._ak_survey_id

    def get_cpue_kgha(self) -> float:
        """Get the value of field cpue_kgha with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Always returns 0.
        """
        return 0

    def get_cpue_kgkm2(self) -> float:
        """Get the value of field cpue_kgkm2 with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Always returns 0
        """
        return 0

    def get_cpue_kg1000km2(self) -> float:
        """Get the value of field cpue_kg1000km2 with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Always returns 0
        """
        return 0

    def get_cpue_noha(self) -> float:
        """Get the value of field cpue_noha with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Always returns 0
        """
        return 0

    def get_cpue_nokm2(self) -> float:
        """Get the value of field cpue_nokm2 with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Always returns 0
        """
        return 0

    def get_cpue_no1000km2(self) -> float:
        """Get the value of field cpue_no1000km2 with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Always returns 0
        """
        return 0

    def get_weight_kg(self) -> float:
        """Get the value of field weight_kg with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Always returns 0
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

    def get_bottom_temperature_c(self) -> float:
        """Get the value of field bottom_temperature_c with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Bottom temperature associated with observation if available in
            Celsius.
        """
        return self._haul.get_bottom_temperature_c()

    def get_surface_temperature_c(self) -> float:
        """Get the value of field surface_temperature_c with validity assert.

        Raises:
            AssertionError: Raised if this field was not given by the API or
            could not be parsed as expected.

        Returns:
            Surface temperature associated with observation if available in
            Celsius. None if not
        """
        return self._haul.get_surface_temperature_c()

    def is_complete(self) -> bool:
        """Determine if this record has all of its values filled in.

        Returns:
            True if all optional fields have a parsed value with the expected
            type and false otherwise.
        """
        tsn_given = self._tsn is not None
        ak_survey_id_given = self._ak_survey_id is not None
        return tsn_given and ak_survey_id_given and self._haul.is_complete()

    def to_dict(self) -> dict:
        """Serialize this Record to a dictionary form.

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
            'latitude_dd': self.get_latitude_dd(),
            'longitude_dd': self.get_longitude_dd(),
            'species_code': self.get_species_code(),
            'common_name': self.get_common_name(),
            'scientific_name': self.get_scientific_name(),
            'taxon_confidence': self.get_taxon_confidence(),
            'cpue_kgha': self.get_cpue_kgha(),
            'cpue_kgkm2': self.get_cpue_kgkm2(),
            'cpue_kg1000km2': self.get_cpue_kg1000km2(),
            'cpue_noha': self.get_cpue_noha(),
            'cpue_nokm2': self.get_cpue_nokm2(),
            'cpue_no1000km2': self.get_cpue_no1000km2(),
            'weight_kg': self.get_weight_kg(),
            'count': self.get_count(),
            'bottom_temperature_c': self.get_bottom_temperature_c_maybe(),
            'surface_temperature_c': self.get_surface_temperature_c_maybe(),
            'depth_m': self.get_depth_m(),
            'distance_fished_km': self.get_distance_fished_km(),
            'net_width_m': self.get_net_width_m(),
            'net_height_m': self.get_net_height_m(),
            'area_swept_ha': self.get_area_swept_ha(),
            'duration_hr': self.get_duration_hr(),
            'tsn': self.get_tsn_maybe(),
            'ak_survey_id': self.get_ak_survey_id()
        }