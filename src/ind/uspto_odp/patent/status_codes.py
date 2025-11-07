"""
patent.status_codes — Patent application status code lookup

Implements `/api/v1/patent/status-codes` (GET or POST).

Returns USPTO-defined application status codes and their
human-readable descriptions (e.g., "Patented Case", "Abandoned").

Use POST with a JSON body for complex queries or GET with a simple
`q` parameter for text filtering.

Example
-------
>>> from ind.uspto.client import USPTOClient
>>> from ind.uspto.patent.status_codes import get_status_codes
>>> client = USPTOClient(api_key="YOUR_KEY")
>>> res = get_status_codes(client)
>>> for entry in res.get("statusCodes", []):
...     print(entry)
"""

from __future__ import annotations
from typing import Any, Dict, Optional
from ..client import USPTOClient
from ..types import search_auto_request_json, maybe_pprint

def get_status_codes(
    client: USPTOClient,
    *,
    q: Optional[str] = None,
    method: str = "GET",
    troubleshoot: bool = False,
) -> Dict[str, Any]:
    """
    Retrieve patent application status codes and their descriptions.

    Endpoint:
        GET or POST /api/v1/patent/status-codes

    Parameters
    ----------
    client : USPTOClient
        The shared USPTO API client.
    q : str, optional
        Optional query string to filter status codes or descriptions.
        Example: "Patented Case"
    method : {"GET", "POST"}, default "GET"
        HTTP method to use. POST can be used to submit JSON payloads for
        more complex queries, while GET is suitable for simple retrieval.

    Returns
    -------
    Dict[str, Any]
        Parsed JSON response from the USPTO ODP API.

    Raises
    ------
    BadRequestError
        If the request is malformed (HTTP 400).
    ForbiddenError
        If the API key or user does not have access (HTTP 403).
    NotFoundError
        If no results were found (HTTP 404).
    PayloadTooLargeError
        If the response is too large (HTTP 413).
    RateLimitError
        If the USPTO rate limit is reached (HTTP 429).
    ServerError
        If a server-side error occurs (HTTP 5xx).

    Examples
    --------
    >>> from uspto_odp.client import USPTOClient
    >>> from uspto_odp.patent.status_codes import get_status_codes
    >>> client = USPTOClient(api_key="YOUR_KEY")
    >>> res = get_status_codes(client)
    >>> for entry in res.get("statusCodes", []):
    ...     print(entry)
    """
    path = "/api/v1/patent/status-codes"
    body = {"q": q} if q else {}
    maybe_pprint(body, troubleshoot, "Patent Status Codes Body")
    return search_auto_request_json(client, path, body, method=method)