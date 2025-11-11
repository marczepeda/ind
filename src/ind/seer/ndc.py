

from __future__ import annotations
from typing import Any, Mapping, Optional, Sequence, Union, Dict
from .client import SeerClient, JSON
from .utils import get_category, put, join_csv, cap_count

CATEGORY = "ndc"

def list_ndc(
    client: SeerClient,
    *,
    q: Optional[str] = None,                      # URL-encoded search query
    has_seer_info: Optional[bool] = None,         # include only drugs with SEER-maintained info
    category: Optional[Sequence[str]] = None,     # HORMONAL_THERAPY | ANCILLARY | CHEMOTHERAPY | IMMUNOTHERAPY | RADIOPHARMACEUTICAL
    include_removed: Optional[bool] = None,       # include drugs removed from FDA database
    page: Optional[int] = 1,                      # default 1
    per_page: Optional[int] = 25,                 # default 25
    order: Optional[str] = None,                  # ndc | -ndc | date_added | -date_added | date_modified | -date_modified | proprietary_name | -proprietary_name
    added_since: Optional[str] = None,            # YYYY-MM-DD
    modified_since: Optional[str] = None,         # YYYY-MM-DD
    removed_since: Optional[str] = None,          # YYYY-MM-DD
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/ndc
    Return matching drugs.

    Parameters
    ----------
    q : str, optional
        Search query (should be URL encoded by the caller if needed).
    has_seer_info : bool, optional
        If True, only include drugs with SEER-maintained information.
    category : Sequence[str], optional
        Limit results to one or more categories (comma-separated in request).
    include_removed : bool, optional
        If True, include items flagged as removed from the FDA database.
    page : int, optional
        Page number (default 1).
    per_page : int, optional
        Entries per page (default 25).
    order : str, optional
        Sort field/direction (see API docs for allowed values).
    added_since / modified_since / removed_since : str, optional
        Date filters in YYYY-MM-DD format.
    """
    endpoint = ""  # base /rest/ndc
    params: Dict[str, Any] = {}

    put(params, "q", q)
    put(params, "has_seer_info", has_seer_info)
    put(params, "category", join_csv(category))
    put(params, "include_removed", include_removed)
    put(params, "page", page)
    put(params, "per_page", per_page)
    put(params, "order", order)
    put(params, "added_since", added_since)
    put(params, "modified_since", modified_since)
    put(params, "removed_since", removed_since)

    if passthrough:
        params.update(passthrough)

    return get_category(client, CATEGORY, endpoint, params=params)


def get_ndc_by_code(
    client: SeerClient,
    code: str,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/ndc/code/{code}
    Return a single drug product. All possible packages are included in each product.

    Parameters
    ----------
    code : str
        NDC code to retrieve.
    """
    endpoint = f"code/{code}"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)