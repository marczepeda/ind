from __future__ import annotations
from typing import Any, Mapping, Optional, Dict
from .client import SeerClient, JSON
from .utils import get_category, put

CATEGORY = "recode"

def get_site_group(
    client: SeerClient,
    algorithm: str = "seer",  # 'seer' | 'iccc' | 'aya'
    *,
    site: str,
    hist: str,
    behavior: Optional[str] = None,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/recode/sitegroup/{algorithm}
    Return the site group for the site/histology/behavior combination based on a specified algorithm.

    Supported algorithms: 'seer' (default), 'iccc', 'aya'.
    Query parameters:
      - site: Primary site (required)
      - hist: Histology (required)
      - behavior: Behavior (optional)
    """
    endpoint = f"sitegroup/{algorithm}"
    params: Dict[str, Any] = {}
    put(params, "site", site)
    put(params, "hist", hist)
    put(params, "behavior", behavior)
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)

def list_sitegroup_algorithms(
    client: SeerClient,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/recode/sitegroup/algorithms
    Return the supported site group algorithms and versions.
    """
    endpoint = "sitegroup/algorithms"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)