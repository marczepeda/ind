from __future__ import annotations
from typing import Any, Mapping, Optional, Sequence, Dict
from .client import SeerClient, JSON
from .utils import get_category, put, join_csv, cap_count

CATEGORY = "disease"

def list_diseases(
    client: SeerClient,
    version: str,
    *,
    # filters
    q: Optional[str] = None,
    status: Optional[Sequence[str]] = None,
    assigned_to: Optional[str] = None,
    site_category: Optional[Sequence[str]] = None,
    type: Optional[str] = "HEMATO",  # SEER recommends including HEMATO to get production-ready data
    modified_from: Optional[str] = None,   # YYYY-MM-DD
    modified_to: Optional[str] = None,     # YYYY-MM-DD
    published_from: Optional[str] = None,  # YYYY-MM-DD
    published_to: Optional[str] = None,    # YYYY-MM-DD
    been_published: Optional[bool] = None,
    hidden: Optional[bool] = None,
    mode: Optional[str] = None,            # AND | OR
    # paging/sorting/output
    count: Optional[int] = 25,
    offset: Optional[int] = 0,
    order: Optional[str] = None,           # name, -name, status, -status, ...
    output_type: Optional[str] = None,     # MIN | PARTIAL | FULL
    glossary: Optional[bool] = None,
    # passthrough for any future params
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/disease/{version}
    Return a list of Disease entries.

    Notes
    -----
    * If `type` is not specified, this helper defaults it to "HEMATO" per SEER guidance
      (Solid Tumor data may be preview-only). Override `type` to None or "SOLID_TUMOR" to change.
    * `status` and `site_category` accept lists which are serialized as comma-separated values.
    * Booleans are serialized as "true"/"false" strings per SEER conventions.
    """
    endpoint = version  # path segment after /rest/disease/
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
    put(params, "site_category", join_csv(site_category))

    # paging/sorting/output
    put(params, "count", count)
    put(params, "offset", offset)
    put(params, "order", order)
    put(params, "output_type", output_type)
    put(params, "glossary", glossary)

    if passthrough:
        params.update(passthrough)

    return get_category(client, CATEGORY, endpoint, params=params)


# Single disease by ID and year
def get_disease_by_id_year(
    client: SeerClient,
    version: str,
    id: str,
    year: str,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/disease/{version}/id/{id}/{year}
    Return a single disease with only year-based information for the passed year included.

    Parameters
    ----------
    version : str
        Disease version.
    id : str
        Disease identifier.
    year : str
        Year to include year-based fields (only values that fall in the passed range will be included).
    """
    endpoint = f"{version}/id/{id}/{year}"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)

# Convenience: explicit hematopoietic-only wrapper
def list_diseases_hematopoietic(
    client: SeerClient,
    version: str,
    **kwargs: Any,
) -> JSON:
    """
    Same as list_diseases but forces type="HEMATO".
    """
    kwargs = dict(kwargs)
    kwargs["type"] = "HEMATO"
    return list_diseases(client, version, **kwargs)


# Changelog endpoint
def list_disease_changelog(
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
    GET /rest/disease/{version}/changelog
    Return a list of Disease changelog entries.

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
    safe_count = cap_count(count, max_value=10)
    put(params, "count", safe_count)
    put(params, "offset", offset)
    put(params, "id", id)
    put(params, "order", order)

    if passthrough:
        params.update(passthrough)

    return get_category(client, CATEGORY, endpoint, params=params)


# Keyword list endpoint
def list_disease_keywords(
    client: SeerClient,
    version: str,
    *,
    q: Optional[str] = None,
    count: Optional[int] = None,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/disease/{version}/keywords
    Return a list of keywords contained in the disease entries.

    Parameters
    ----------
    version : str
        Disease version.
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


# Status summary endpoint
def list_disease_status_summary(
    client: SeerClient,
    version: str,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/disease/{version}/status_summary
    Return a list of disease entries with status summary information.
    """
    endpoint = f"{version}/status_summary"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


# Determine if two morphologies (with diagnosis years) represent the same disease
def is_same_disease(
    client: SeerClient,
    version: str,
    *,
    d1: str,
    year1: str,
    d2: str,
    year2: str,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/disease/{version}/same   (endpoint name inferred)
    Determine whether two ICD-O-3 morphologies (with diagnosis years) represent the same disease
    according to SEER disease rules.

    Parameters
    ----------
    version : str
        Disease version.
    d1 : str
        Morphology code for the first disease (e.g., '8000/3').
    year1 : str
        Diagnosis year for the first disease (YYYY).
    d2 : str
        Morphology code for the second disease (e.g., '8500/3').
    year2 : str
        Diagnosis year for the second disease (YYYY).

    Notes
    -----
    * The exact path segment ('same') may vary in future API versions. If SEER changes the path,
      update the `endpoint` variable accordingly.
    """
    endpoint = f"{version}/same_primary"
    params: Dict[str, Any] = {
        "d1": d1,
        "year1": year1,
        "d2": d2,
        "year2": year2,
    }
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


# Retrieve a single disease entry by ID
def get_disease_by_id(
    client: SeerClient,
    version: str,
    id: str,
    *,
    glossary: Optional[bool] = None,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/disease/{version}/id/{id}
    Return a single disease entry.

    Parameters
    ----------
    version : str
        Disease version.
    id : str
        Disease identifier.
    glossary : bool, optional
        If True, return glossary matches (default False).
    """
    endpoint = f"{version}/id/{id}"
    params: Dict[str, Any] = {}
    put(params, "glossary", glossary)

    if passthrough:
        params.update(passthrough)

    return get_category(client, CATEGORY, endpoint, params=params)


# Primary site list endpoint
def list_disease_primary_sites(
    client: SeerClient,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/disease/primary_site
    Return the list of ICDO2/ICDO3 primary site codes and labels.
    """
    endpoint = "primary_site"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


# Primary site by code endpoint
def get_disease_primary_site_by_code(
    client: SeerClient,
    code: str,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/disease/primary_site/{code}
    Return the list of ICDO2/ICDO3 primary sites matching a code.

    Parameters
    ----------
    code : str
        The ICDO2/ICDO3 primary site code to query.
    """
    endpoint = f"primary_site/{code}"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


# Site categories (solid tumor–oriented)
def list_disease_site_categories(
    client: SeerClient,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/disease/site_categories
    Return the complete list of site categories for use in the search API.
    Note: Site categories are only relevant for solid tumor diseases.
    """
    endpoint = "site_categories"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)

# Disease database versions endpoint
def list_disease_versions(
    client: SeerClient,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/disease/versions
    Return a list of all versions of the disease database.
    """
    endpoint = "versions"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)