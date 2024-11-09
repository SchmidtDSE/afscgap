import queue
import typing

import afscgap.cursor
import afscgap.model

from afscgap.flat_model import RECORDS


class FlatCursor(afscgap.cursor.Cursor):
    
    def __init__(self, records: RECORDS):
        self._records = records
        
    
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
            API that did not have valid values for all required fields. Note
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
            return next(records)
        except StopIteration:
            return None


class CompleteCursor(afscgap.cursor.Cursor):
    
    def __init__(self, inner: afscgap.cursor.Cursor):
        self._inner = inner
        self._invalid = queue.Queue()
    
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
        return self._inner.to_dicts()
    
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
                self._invalid.add(next_candidate)
            
            done = is_complete
        
        return next_candidate
            
    
class LimitCursor(afscgap.cursor.Cursor):
    
    def __init__(self, inner: afscgap.cursor.Cursor, limit: int):
        self._inner = inner
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
        return self._inner.to_dicts()
    
    def get_next(self) -> typing.Optional[afscgap.model.Record]:
        """Get the next value for this Cursor.

        Returns:
            The next value waiting if cached in the cursor's results queue or
            as just retrieved from a new page gathered by HTTP request. Will
            return None if no remain.
        """
        if self._remining == 0:
            return None

        next_candidate = self._inner.get_next()
        
        if next_candidate is None:
            return None
        else:
            self._remaining -= 1
            return next_candidate
