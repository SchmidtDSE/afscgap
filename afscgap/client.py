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
import queue
import typing

import requests

import afscgap.model

OPT_INT = typing.Optional[int]


class Cursor(typing.Iterable[afscgap.model.Record]):

    def __init__(self, base_url: str, limit: int, start_offset: int):
        self._base_url = base_url
        self._next_url = base_url
        self._limit = limit
        self._start_offset = start_offset
        self._queue = queue.Queue()
        self._done = False

    def get_base_url(self) -> str:
        return self._base_url

    def get_limit(self) -> int:
        return self._limit

    def get_start_offset(self) -> int:
        return self._start_offset

    def get_page_url(self, offset: OPT_INT = None,
        limit: OPT_INT = None) -> str:
        
        if offset is None:
            offset = self._start_offset

        if limit is None:
            limit = self._limit
        
        return self._base_url + '&offset=%d&limit=%d' % (offset, limit)

    def get_page(self, offset: OPT_INT = None,
        limit: OPT_INT = None) -> typing.List[afscgap.model.Record]:
        url = self.get_page_url(offset, limit)
        
        result = requests.get(url)
        self._check_result(result)
        
        result_parsed = result.json()
        items_raw = result_parsed['items']
        return [model.parse_record(x) for x in items_raw]

    def __iter__(self) -> typing.Iterator[afscgap.model.Record]:
        return self

    def __next__(self) -> afscgap.model.Record:
        if self._queue.empty():
            self._queue_next_page()

        if self._done:
            raise StopIteration()

    def _queue_next_page(self):
        if self._done:
            return

        result = requests.get(self._next_url)
        self._check_result(result)

        result_parsed = result.json()

        if result_parsed['hasMore']:
            self._done = False
            items_raw = result_parsed['items']

            items_parsed = map(model.parse_record, items_raw)
            for item_parsed in items_parsed:
                self._queue.add(item_parsed)

            self._next_url = self._find_next_url(result_parsed)
        else:
            self._done = True

    def _find_next_url(self, target: dict) -> str:
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
