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


def check_result(target: requests.Response):
    """Assert that a result returned an acceptable status code.

    Args:
        target: The response to check.

    Raises:
        RuntimeError: Raised if the response returned indicates an issue or
            unexpected status code.
    """
    status_ok = target.status_code >= 100 and target.status_code < 400
    if not status_ok:
        message = 'Got non-OK response from remote: %d (%s)' % (
            target.status_code,
            target.text
        )
        raise RuntimeError(message)


def build_requestor(stream: bool = False) -> REQUESTOR:
    """Build a requestor strategy that uses the requests library.

    Returns:
        Newly built strategy.
    """
    return lambda x: requests.get(x, timeout=TIMEOUT, stream=stream)
