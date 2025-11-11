from __future__ import annotations
from typing import Any, Mapping, Optional, Union, Dict
from .client import SeerClient, JSON
from .utils import get_category, put

CATEGORY = "naaccr"

def list_naaccr_items(
    client: SeerClient,
    version: str,
    *,
    version_implemented: Optional[str] = None,   # version the field was added to NAACCR standard
    q: Optional[str] = None,                      # URL-encoded search query
    count: Optional[int] = None,                  # number of items to return; if None, API returns all
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/naaccr/{version}
    Return all NAACCR item identifiers and names (optionally filtered).

    Parameters
    ----------
    version : str
        Record layout version (path parameter).
    version_implemented : str, optional
        Only include items whose VersionImplemented matches this value.
    q : str, optional
        Search query (should be URL-encoded if necessary).
    count : int, optional
        Number of data items to return. If not specified, the API returns all items.
    """
    endpoint = version
    params: Dict[str, Any] = {}
    put(params, "version_implemented", version_implemented)
    put(params, "q", q)
    put(params, "count", count)

    if passthrough:
        params.update(passthrough)

    return get_category(client, CATEGORY, endpoint, params=params)

def get_naaccr_item_by_id(
    client: SeerClient,
    version: str,
    id: str,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/naaccr/{version}/{id}
    Return a single NAACCR item by XML ID or item number.

    Parameters
    ----------
    version : str
        Record layout version (path parameter).
    id : str
        NAACCR XML ID or item number.
    """
    endpoint = f"{version}/{id}"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)

def list_naaccr_versions(
    client: SeerClient,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/naaccr/versions
    Return a list of information about all supported NAACCR versions.
    """
    endpoint = "versions"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)