"""
Type definitions for the afscgap project.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import typing

import requests


OPT_FLOAT = typing.Optional[float]
OPT_INT = typing.Optional[int]
OPT_STR = typing.Optional[str]

STR_OR_DICT = typing.Union[str, dict]
RANGE_TUPLE = typing.Tuple[float]
FLOAT_PARAM = typing.Optional[typing.Union[float, dict, RANGE_TUPLE]]
INT_PARAM = typing.Optional[typing.Union[int, dict, RANGE_TUPLE]]
STR_PARAM = typing.Optional[STR_OR_DICT]

REQUESTOR = typing.Callable[[str], requests.Response]
OPT_REQUESTOR = typing.Optional[REQUESTOR]
