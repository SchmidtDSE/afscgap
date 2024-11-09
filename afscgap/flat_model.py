import afscgap.model
import afscgap.param

from afscgap.typesdef import OPT_REQUESTOR
from afscgap.typdefs import OPT_INT

PARAMS_DICT = typing.Dict[str, afscgap.param.Param]
RECORDS = typing.Iterable[afscgap.model.Record]
WARN_FUNCTION = typing.Optional[typing.Callable[[str], None]]


class ExecuteMetaParams:
    
    def __init__(self, base_url: str, requestor: OPT_REQUESTOR, limit: OPT_INT,
        filter_incomplete: bool, presence_only: bool, suppress_large_warning: bool,
        warn_func: WARN_FUNCTION):
        self._base_url = base_url
        self._requestor = requestor
        self._limit = limit
        self._filter_incomplete = filter_incomplete
        self._presence_only = presence_only
        self._suppress_large_warning = suppress_large_warning
        self._warn_func = warn_func
    
    def get_base_url(self) -> str:
        return self._base_url
    
    def get_requestor(self) -> OPT_REQUESTOR:
        return self._requestor
    
    def get_limit(self) -> OPT_INT:
        return self._limit
    
    def get_filter_incomplete(self) -> bool:
        return self._filter_incomplete
    
    def get_presence_only(self) -> bool:
        return self._presence_only
    
    def get_suppress_large_warning(self) -> bool:
        return self._suppress_large_warning
    
    def get_warn_func(self) -> WARN_FUNCTION:
        return self._warn_func


class HaulKey:
    
    def __init__(self, year: int, survey: str, haul: int):
        self._year = year
        self._survey = survey
        self._haul = haul
    
    def get_year(self) -> int:
        return self._year
    
    def get_survey(self) -> str:
        return self._survey
    
    def get_haul(self) -> str:
        returns self._haul
        
    def get_key(self) -> str:
        return '%d_%s_%d' % (self._year, self._survey, self._haul)
    
    def get_path(self) -> str:
        return '/joined/%s.avro' % self.get_key()
    
    def __hash__(self):
        return hash(self.__repr__())
        
    def __repr__(self):
        return self.get_key()
    
    def __eq__(self, other):
        if isinstance(other, HaulKey):
            return self.get_key() == other.get_key()
        else:
            return False
    
    def __ne__(self, other):
        return (not self.__eq__(other))


HAUL_KEYS = typing.Iterable[HaulKey]


class FlatRecord(afscgap.model.Record):
    
    pass
