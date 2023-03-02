"""
Convienence functions and definitions.

(c) 2023 The Eric and Wendy Schmidt Center for Data Science and the Environment
at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.txt.
"""
import typing

import requests

OPT_FLOAT = typing.Optional[float]
OPT_INT = typing.Optional[int]
OPT_RECORD = typing.Optional[afscgap.model.Record]
OPT_STR = typing.Optional[str]

REQUESTOR = typing.Callable[[str], requests.Response]
OPT_REQUESTOR = typing.Optional[REQUESTOR]
