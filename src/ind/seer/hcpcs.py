

from __future__ import annotations
from typing import Any, Mapping, Optional, Sequence, Dict
from .client import SeerClient, JSON
from .utils import get_category, put, join_csv

CATEGORY = "hcpcs"

def list_hcpcs(
    client: SeerClient,
    *,
    q: Optional[str] = None,                     # URL-encoded search query
    category: Optional[Sequence[str]] = None,    # one or more category values
    page: Optional[int] = 1,                     # default 1
    per_page: Optional[int] = 25,                # default 25
    order: Optional[str] = None,                 # hcpcs_code | -hcpcs_code | date_added | -date_added | date_modified | -date_modified
    added_since: Optional[str] = None,           # YYYY-MM-DD
    modified_since: Optional[str] = None,        # YYYY-MM-DD
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/hcpcs
    Return matching procedures.

    Parameters
    ----------
    q : str, optional
        Search query (should be URL encoded by the caller if needed).
    category : Sequence[str], optional
        Limit results to one or more categories (comma-separated in request).
    page : int, optional
        Page number (default 1).
    per_page : int, optional
        Entries per page (default 25).
    order : str, optional
        Sort order: hcpcs_code, -hcpcs_code, date_added, -date_added, date_modified, -date_modified.
    added_since : str, optional
        Include entries added on or after YYYY-MM-DD.
    modified_since : str, optional
        Include entries added or modified on or after YYYY-MM-DD.
    """
    endpoint = ""  # base /rest/hcpcs
    params: Dict[str, Any] = {}

    put(params, "q", q)
    put(params, "category", join_csv(category))
    put(params, "page", page)
    put(params, "per_page", per_page)
    put(params, "order", order)
    put(params, "added_since", added_since)
    put(params, "modified_since", modified_since)

    if passthrough:
        params.update(passthrough)

    return get_category(client, CATEGORY, endpoint, params=params)


# Helper to retrieve a single procedure by HCPCS code
def get_hcpcs_by_code(
    client: SeerClient,
    code: str,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/hcpcs/code/{code}
    Return a single procedure by its HCPCS code.

    Parameters
    ----------
    code : str
        HCPCS code.
    """
    endpoint = f"code/{code}"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)