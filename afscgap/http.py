"""
Utilities for HTTP requests as part of afscgap.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
import requests

from afscgap.typesdef import REQUESTOR

TIMEOUT = 60 * 5  # 5 minutes

ACCEPTABLE_CODES = [200]


def check_result(target: requests.Response):
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


def build_requestor() -> REQUESTOR:
    """Build a requestor strategy that uses the requests library.

    Returns:
        Newly built strategy.
    """
    return lambda x: requests.get(x, timeout=TIMEOUT)
