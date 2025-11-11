from __future__ import annotations
from typing import Any, Mapping, Optional, Sequence, Dict
from .client import SeerClient, JSON
from .utils import get_category, put, join_csv

CATEGORY = "rx"

def list_rx(
    client: SeerClient,
    version: str,
    *,
    # filters
    q: Optional[str] = None,
    status: Optional[Sequence[str]] = None,
    assigned_to: Optional[str] = None,
    type: Optional[str] = None,                 # DRUG | REGIMEN
    modified_from: Optional[str] = None,        # YYYY-MM-DD
    modified_to: Optional[str] = None,          # YYYY-MM-DD
    published_from: Optional[str] = None,       # YYYY-MM-DD
    published_to: Optional[str] = None,         # YYYY-MM-DD
    been_published: Optional[bool] = None,
    hidden: Optional[bool] = None,
    mode: Optional[str] = None,                 # AND | OR
    # paging/sorting/output
    count: Optional[int] = 25,
    offset: Optional[int] = 0,
    order: Optional[str] = None,                # name, -name, status, -status, assigned_to, -assigned_to, last_modified, -last_modified, type, -type, ...
    output_type: Optional[str] = None,          # MIN | PARTIAL | FULL
    glossary: Optional[bool] = None,
    # additional filters
    category: Optional[Sequence[str]] = None,   # one or more category strings
    do_not_code: Optional[str] = None,          # YES | NO | SEE_REMARKS
    # passthrough
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/rx/{version}
    Return a list of Rx entries.

    Parameters
    ----------
    version : str
        Rx version (path parameter).
    q : str, optional
        Search query.
    status : Sequence[str], optional
        Status filter(s).
    assigned_to : str, optional
        Only include Rx items assigned to this value.
    type : str, optional
        RX classification: DRUG or REGIMEN.
    modified_from / modified_to / published_from / published_to : str, optional
        Date bounds in YYYY-MM-DD format.
    been_published / hidden : bool, optional
        Publication/visibility flags.
    mode : str, optional
        Search mode: AND or OR.
    count / offset : int, optional
        Pagination controls (defaults: 25, 0).
    order : str, optional
        Sort order (see API for allowed values).
    output_type : str, optional
        MIN | PARTIAL | FULL.
    glossary : bool, optional
        Return glossary matches.
    category : Sequence[str], optional
        Limit search to one or more categories.
    do_not_code : str, optional
        YES | NO | SEE_REMARKS.
    """
    endpoint = version  # path segment after /rest/rx/
    params: Dict[str, Any] = {}

    # filters
    put(params, "q", q)
    put(params, "assigned_to", assigned_to)
    put(params, "type", type)
    put(params, "modified_from", modified_from)
    put(params, "modified_to", modified_to)
    put(params, "published_from", published_from)
    put(params, "published_to", published_to)
    put(params, "been_published", been_published)
    put(params, "hidden", hidden)
    put(params, "mode", mode)
    # arrays
    put(params, "status", join_csv(status))
    put(params, "category", join_csv(category))

    # paging/sorting/output
    put(params, "count", count)
    put(params, "offset", offset)
    put(params, "order", order)
    put(params, "output_type", output_type)
    put(params, "glossary", glossary)

    # additional filters
    put(params, "do_not_code", do_not_code)

    if passthrough:
        params.update(passthrough)

    return get_category(client, CATEGORY, endpoint, params=params)


# Helper for /rest/rx/{version}/changelog
def list_rx_changelog(
    client: SeerClient,
    version: str,
    *,
    from_date: Optional[str] = None,   # YYYY-MM-DD
    to_date: Optional[str] = None,     # YYYY-MM-DD
    count: Optional[int] = None,       # <= 10 per API
    offset: Optional[int] = None,
    id: Optional[str] = None,          # entity ID filter
    order: Optional[str] = None,       # ASC | DESC (default DESC by API)
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/rx/{version}/changelog
    Return a list of Rx changelog entries.

    Parameters mirror the SEER API:
    - from_date / to_date: YYYY-MM-DD bounds
    - count: max 10 per request (API limit)
    - offset: results offset (default 0)
    - id: filter changelogs containing this entity ID
    - order: 'ASC' or 'DESC' (default DESC)
    """
    endpoint = f"{version}/changelog"
    params: Dict[str, Any] = {}

    put(params, "from", from_date)
    put(params, "to", to_date)
    if count is not None:
        safe_count = int(count)
        if safe_count > 10:
            safe_count = 10
        put(params, "count", safe_count)
    put(params, "offset", offset)
    put(params, "id", id)
    put(params, "order", order)

    if passthrough:
        params.update(passthrough)

    return get_category(client, CATEGORY, endpoint, params=params)


# Helper for /rest/rx/{version}/id/{id}
def get_rx_by_id(
    client: SeerClient,
    version: str,
    id: str,
    *,
    glossary: Optional[bool] = None,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/rx/{version}/id/{id}
    Return an Rx entry.

    Parameters
    ----------
    version : str
        Rx version.
    id : str
        Rx identifier.
    glossary : bool, optional
        If True, return glossary matches (default False).
    """
    endpoint = f"{version}/id/{id}"
    params: Dict[str, Any] = {}
    put(params, "glossary", glossary)
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


# Helper for /rest/rx/{version}/id/{id}/regimens
def list_rx_regimens_for_drug(
    client: SeerClient,
    version: str,
    id: str,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/rx/{version}/id/{id}/regimens
    Return a list of regimens containing the passed drug.

    Parameters
    ----------
    version : str
        Rx version.
    id : str
        Rx identifier.
    """
    endpoint = f"{version}/id/{id}/regimens"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


# Helper for /rest/rx/{version}/keywords
def list_rx_keywords(
    client: SeerClient,
    version: str,
    *,
    q: Optional[str] = None,
    count: Optional[int] = None,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/rx/{version}/keywords
    Return a list of keywords contained in the Rx entries.

    Parameters
    ----------
    version : str
        Rx version.
    q : str, optional
        Search query to filter keywords.
    count : int, optional
        Number of results to return.
    """
    endpoint = f"{version}/keywords"
    params: Dict[str, Any] = {}
    put(params, "q", q)
    put(params, "count", count)
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


# Helper for /rest/rx/{version}/status_summary
def list_rx_status_summary(
    client: SeerClient,
    version: str,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/rx/{version}/status_summary
    Return a list of Rx entries with status summary information.
    """
    endpoint = f"{version}/status_summary"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)

# Helper for /rest/rx/versions
def list_rx_versions(
    client: SeerClient,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/rx/versions
    Return a list of all versions of the Rx database.
    """
    endpoint = "versions"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)
