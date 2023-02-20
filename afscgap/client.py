"""
Logic for making actual HTTP requests and managaing pagination when interfacing
with AFSC GAP API.

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
import queue
import typing

import requests

import afscgap.model
from afscgap.util import OPT_INT
from afscgap.util import OPT_STR

DEFAULT_URL = 'https://apps-st.fisheries.noaa.gov/ods/foss/afsc_groundfish_survey/'
REQUESTOR = typing.Callable[[str], requests.Response]
OPT_REQUESTOR = typing.Optional[REQUESTOR]


def get_query_url(params: dict, base: OPT_STR = None) -> str:
    if base is None:
        base = DEFAULT_URL

    all_items = params.items()
    items_included = filter(lambda x: x[1] is not None, all_items)
    included_dict = dict(items_included)
    included_json = json.dumps(included_dict)

    return '%s?q=%s' % (base, included_json)


class Cursor(typing.Iterable[afscgap.model.Record]):

    def __init__(self, query_url: str, limit: OPT_INT = None,
        start_offset: OPT_INT = None, requestor: OPT_REQUESTOR = None):
        self._query_url = query_url
        self._limit = limit
        self._start_offset = start_offset
        self._queue = queue.Queue()
        self._done = False

        if requestor:
            self._request_strategy = requestor
        else:
            self._request_strategy = lambda x: requsets.get(x)

        self._next_url = self.get_page_url()

    def get_base_url(self) -> str:
        return self._query_url

    def get_limit(self) -> OPT_INT:
        return self._limit

    def get_start_offset(self) -> OPT_INT:
        return self._start_offset

    def get_page_url(self, offset: OPT_INT = None,
        limit: OPT_INT = None) -> str:
        
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
        limit: OPT_INT = None) -> typing.List[afscgap.model.Record]:
        url = self.get_page_url(offset, limit)
        
        result = self._request_strategy(url)
        self._check_result(result)
        
        result_parsed = result.json()
        items_raw = result_parsed['items']
        return [afscgap.model.parse_record(x) for x in items_raw]

    def to_dicts(self) -> typing.Iterable[dict]:
        return map(lambda x: x.to_dict(), self)

    def __iter__(self) -> typing.Iterator[afscgap.model.Record]:
        return self

    def __next__(self) -> afscgap.model.Record:
        self._queue_next_page_if_needed()

        if self._queue.empty():
            raise StopIteration()
        else:
            return self._queue.get()

    def _queue_next_page_if_needed(self):
        if self._queue.empty():
            self._queue_next_page()

    def _queue_next_page(self):
        if self._done:
            return

        result = self._request_strategy(self._next_url)
        self._check_result(result)

        result_parsed = result.json()

        items_raw = result_parsed['items']

        items_parsed = map(afscgap.model.parse_record, items_raw)
        for item_parsed in items_parsed:
            self._queue.put(item_parsed)

        next_url = self._find_next_url(result_parsed)
        self._done = next_url is None
        self._next_url = next_url

    def _find_next_url(self, target: dict) -> OPT_STR:
        if not target['hasMore']:
            return None

        links = target['links']
        matching = filter(lambda x: x['rel'] == 'next', links)
        matching_hrefs = map(lambda x: x['href'], matching)
        hrefs_realized = list(matching_hrefs)

        if len(hrefs_realized) == 0:
            raise RuntimeError('Could not find next URL but hasMore was true.')
        
        return hrefs_realized[0]

    def _check_result(self, target: requests.Response):
        if target.status != 200:
            message = 'Got non-OK response from API: %d (%s)' % (
                target.status,
                target.text
            )
            raise RuntimeError(message)
