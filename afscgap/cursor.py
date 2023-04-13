"""
Interfaces for cursor objects which iterate over real or inferred records.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""

import queue
import typing

import afscgap.model

from afscgap.typesdef import OPT_INT


class Cursor(typing.Iterable[afscgap.model.Record]):
    """Interface for objects allowing generation / retrieval of records."""

    def get_base_url(self) -> str:
        """Get the URL at which the first page of query results can be found.

        Returns:
            The URL for the query without pagination information.
        """
        raise NotImplementedError('Use implementor.')

    def get_limit(self) -> OPT_INT:
        """Get the page size limit.

        Returns:
            The maximum number of records to return per page.
        """
        raise NotImplementedError('Use implementor.')

    def get_start_offset(self) -> OPT_INT:
        """Get the number of inital records to ignore.

        Returns:
            The number of records being skipped at the start of the result set.
        """
        raise NotImplementedError('Use implementor.')

    def get_filtering_incomplete(self) -> bool:
        """Determine if this cursor is silently filtering incomplete records.

        Returns:
            Flag indicating if incomplete records should be silently filtered.
            If true, they will not be returned during iteration and placed in
            the queue at get_invalid(). If false, they will be returned and
            those incomplete records' get_complete() will return false.
        """
        raise NotImplementedError('Use implementor.')

    def get_page_url(self, offset: OPT_INT = None,
        limit: OPT_INT = None) -> str:
        """Get a URL at which a page can be found using this cursor's base url.

        Args:
            offset: The number of records to skip prior to the page.
            limit: The maximum number of records to return in the page.
        Returns:
            URL at which the requested page can be found.
        """
        raise NotImplementedError('Use implementor.')

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
        raise NotImplementedError('Use implementor.')

    def get_invalid(self) -> 'queue.Queue[dict]':
        """Get a queue of invalid / incomplete records found so far.

        Returns:
            Queue with dictionaries containing the raw data returned from the
            API that did not have valid values for all required fields. Note
            that this will include incomplete records as well if
            get_filtering_incomplete() is true and will not contain incomplete
            records otherwise.
        """
        raise NotImplementedError('Use implementor.')

    def to_dicts(self) -> typing.Iterable[dict]:
        """Create an iterator which converts Records to dicts.

        Returns:
            Iterator which returns dictionaries instead of Record objects but
            has otherwise the same beahavior as iterating in this Cursor
            directly.
        """
        raise NotImplementedError('Use implementor.')

    def get_next(self) -> typing.Optional[afscgap.model.Record]:
        """Get the next value for this Cursor.

        Returns:
            The next value waiting if cached in the cursor's results queue or
            as just retrieved from a new page gathered by HTTP request. Will
            return None if no remain.
        """
        raise NotImplementedError('Use implementor.')

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
        next_maybe = self.get_next()
        if next_maybe is not None:
            return next_maybe
        else:
            raise StopIteration()
