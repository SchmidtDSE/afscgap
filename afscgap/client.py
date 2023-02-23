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

ACCEPTABLE_CODES = [200]
DEFAULT_DOMAIN = 'https://apps-st.fisheries.noaa.gov'
DEFAULT_URL = DEFAULT_DOMAIN + '/ods/foss/afsc_groundfish_survey/'
REQUESTOR = typing.Callable[[str], requests.Response]
OPT_REQUESTOR = typing.Optional[REQUESTOR]
TIMEOUT = 60 * 5  # 5 minutes


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


class Cursor(typing.Iterable[afscgap.model.Record]):
    """Object to make HTTP and manage interpretation of results."""

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
            self._request_strategy = lambda x: requests.get(x, timeout=TIMEOUT)

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
        self._check_result(result)

        result_parsed = result.json()
        items_raw = result_parsed['items']

        parsed_maybe = map(afscgap.model.try_parse, items_raw)
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

    def __iter__(self) -> typing.Iterator[afscgap.model.Record]:
        """Indicate that this Cursor can be iterated on.

        Returns:
            This object as an iterator.
        """
        return self

    def __next__(self) -> afscgap.model.Record:
        """Get the next value for this Cursor inside an interator operation.

        Returns:
            The next value waiting if cached in the cursor's results queue or
            as just retrieved from a new page gathered by HTTP request.

        Raises:
            StopIteration: Raised if no data remain.
        """
        self._load_next_page()

        if self._queue.empty():
            raise StopIteration()
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
        self._check_result(result)

        result_parsed = result.json()

        items_raw = result_parsed['items']

        items_parsed = map(afscgap.model.try_parse, items_raw)

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

    def _check_result(self, target: requests.Response):
        """Assert that a result returned an acceptable status code.

        Args:
            target: The response to check.

        Raises:
            RuntimeError: Raised if the response returned indicates an issue or
                unexpected status code.
        """
        if target.status_code not in ACCEPTABLE_CODES:
            message = 'Got non-OK response from API: %d (%s)' % (
                target.status_code,
                target.text
            )
            raise RuntimeError(message)
