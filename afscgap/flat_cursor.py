"""
Interfaces for cursor objects which iterate over records from prejoined flat records.

Interfaces for cursor objects which iterate over records from prejoined flat records, either those
appearing in the underlying unjoined dataset or zero catch inferred records.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import queue
import typing

import afscgap.cursor
import afscgap.model

from afscgap.flat_model import RECORDS
from afscgap.typesdef import OPT_INT


class FlatCursor(afscgap.cursor.Cursor):
    """Cursor over flat avro "prejoined" results."""

    def __init__(self, records: RECORDS):
        """Create a new prejoined cursor.

        Create a new cursor over prejoined flat files which have already been parsed or which are
        emitted prejoined.

        Args:
            records: The inner iterator that should be decorated by this cursor.
        """
        self._records = records
        self._records_iter = iter(self._records)

    def get_limit(self) -> OPT_INT:
        """Get the overall limit.

        Returns:
            The maximum number of records to return.
        """
        return None

    def get_filtering_incomplete(self) -> bool:
        """Determine if this cursor is silently filtering incomplete records.

        Returns:
            Flag indicating if incomplete records should be silently filtered.
            If true, they will not be returned during iteration and placed in
            the queue at get_invalid(). If false, they will be returned and
            those incomplete records' get_complete() will return false.
        """
        return False

    def get_invalid(self) -> 'queue.Queue[dict]':
        """Get a queue of invalid / incomplete records found so far.

        Returns:
            Queue with dictionaries containing the raw data returned from the
            remote that did not have valid values for all required fields. Note
            that this will include incomplete records as well if
            get_filtering_incomplete() is true and will not contain incomplete
            records otherwise.
        """
        return queue.Queue()

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
        try:
            return next(self._records_iter)
        except StopIteration:
            return None


class CompleteCursor(afscgap.cursor.Cursor):
    """Cursor decorator which only yields complete records."""

    def __init__(self, inner: afscgap.cursor.Cursor):
        """Create a new decorator for another cursor which filters for complete records.

        Args:
            inner: The cursor to decorate.
        """
        self._inner = inner
        self._invalid: queue.Queue[dict] = queue.Queue()

    def get_limit(self) -> OPT_INT:
        """Get the overall limit.

        Returns:
            The maximum number of records to return.
        """
        return self._inner.get_limit()

    def get_filtering_incomplete(self) -> bool:
        """Determine if this cursor is silently filtering incomplete records.

        Returns:
            Flag indicating if incomplete records should be silently filtered.
            If true, they will not be returned during iteration and placed in
            the queue at get_invalid(). If false, they will be returned and
            those incomplete records' get_complete() will return false.
        """
        return True

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
        done = False

        next_candidate = None

        while not done:
            next_candidate = self._inner.get_next()

            if next_candidate is None:
                return None

            is_complete = next_candidate.is_complete()

            if not is_complete:
                next_candidate_cast: afscgap.flat_model.FlatRecord = next_candidate  # type: ignore
                self._invalid.put(next_candidate_cast.get_inner())

            done = is_complete

        return next_candidate


class LimitCursor(afscgap.cursor.Cursor):
    """Create a decorator which limits cursor iteration to a certain count of returned records."""

    def __init__(self, inner: afscgap.cursor.Cursor, limit: int):
        """Create a new limit decorator around an existing cursor.

        Create a new limit decorator around an existing cursor which terminates iteration either
        after a limit is reached or no additional records are available.

        Args:
            inner: The cursor to decorate.
            limit: The integer count of records after which iteration will be terminated.
        """
        self._inner = inner
        self._limit = limit
        self._remaining = limit

    def get_limit(self) -> OPT_INT:
        """Get the overall limit.

        Returns:
            The maximum number of records to return.
        """
        return self._limit

    def get_filtering_incomplete(self) -> bool:
        """Determine if this cursor is silently filtering incomplete records.

        Returns:
            Flag indicating if incomplete records should be silently filtered.
            If true, they will not be returned during iteration and placed in
            the queue at get_invalid(). If false, they will be returned and
            those incomplete records' get_complete() will return false.
        """
        return self._inner.get_filtering_incomplete()

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
        if self._remaining == 0:
            return None

        next_candidate = self._inner.get_next()

        if next_candidate is None:
            return None
        else:
            self._remaining -= 1
            return next_candidate
