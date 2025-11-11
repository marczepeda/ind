from __future__ import annotations
from typing import Any, Mapping, Optional, Sequence, Dict
from .client import SeerClient, JSON
from .utils import get_category, put, join_csv

CATEGORY = "glossary"

def list_glossary(
    client: SeerClient,
    version: str,
    *,
    # filters
    q: Optional[str] = None,
    status: Optional[Sequence[str]] = None,
    assigned_to: Optional[str] = None,
    category: Optional[Sequence[str]] = None,       # GENERAL, SOLID_TUMOR, HEMATO, NON_NEOPLASTIC, SEERRX, SEER_TRAINING, LYMPH_NODES, STAGING
    modified_from: Optional[str] = None,            # YYYY-MM-DD
    modified_to: Optional[str] = None,              # YYYY-MM-DD
    published_from: Optional[str] = None,           # YYYY-MM-DD
    published_to: Optional[str] = None,             # YYYY-MM-DD
    been_published: Optional[bool] = None,
    hidden: Optional[bool] = None,
    mode: Optional[str] = None,                     # AND | OR
    # paging/sorting/output
    count: Optional[int] = 25,
    offset: Optional[int] = 0,
    order: Optional[str] = None,                    # name, -name, status, -status, ...
    output_type: Optional[str] = None,              # MIN | PARTIAL | FULL
    glossary: Optional[bool] = None,
    # passthrough for any future params
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/glossary/{version}
    Return a list of glossary entries.

    Notes
    -----
    * `status` and `category` accept lists serialized as comma-separated values.
    * Booleans are serialized as "true"/"false" strings per SEER conventions.
    """
    endpoint = version  # path segment after /rest/glossary/
    params: Dict[str, Any] = {}

    # filters
    put(params, "q", q)
    put(params, "assigned_to", assigned_to)
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

    if passthrough:
        params.update(passthrough)

    return get_category(client, CATEGORY, endpoint, params=params)

def get_glossary_by_id(
    client: SeerClient,
    version: str,
    id: str,
    *,
    glossary: Optional[bool] = None,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/glossary/{version}/id/{id}
    Return a glossary entry.

    Parameters
    ----------
    version : str
        Glossary version.
    id : str
        Glossary identifier.
    glossary : bool, optional
        If True, return glossary matches (default False).
    """
    endpoint = f"{version}/id/{id}"
    params: Dict[str, Any] = {}
    put(params, "glossary", glossary)
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


# New helper for changelog endpoint
def list_glossary_changelog(
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
    GET /rest/glossary/{version}/changelog
    Return a list of glossary changelog entries.

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


# New helper for keywords endpoint
def list_glossary_keywords(
    client: SeerClient,
    version: str,
    *,
    q: Optional[str] = None,
    count: Optional[int] = None,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/glossary/{version}/keywords
    Return a list of keywords contained in the glossary entries.

    Parameters
    ----------
    version : str
        Glossary version.
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


# New helper for status summary endpoint
def list_glossary_status_summary(
    client: SeerClient,
    version: str,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/glossary/{version}/status_summary
    Return a list of glossary entries with status summary information.
    """
    endpoint = f"{version}/status_summary"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


# Glossary database versions endpoint
def list_glossary_versions(
    client: SeerClient,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/glossary/versions
    Return a list of all versions of the glossary database.
    """
    endpoint = "versions"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)