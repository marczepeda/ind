from __future__ import annotations
from typing import Any, Mapping, Optional, Dict
from .client import SeerClient, JSON
from .utils import get_category, put

CATEGORY = "surgery"

def get_surgery_table(
    client: SeerClient,
    year: str,
    *,
    title: Optional[str] = None,
    site: Optional[str] = None,
    hist: Optional[str] = None,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/surgery/{year}/table
    Return a single surgery table.

    Either `title` OR a (site, hist) combination must be supplied.

    Parameters
    ----------
    year : str
        Year of the data; use "latest" for the latest available year.
    title : str, optional
        Table title.
    site : str, optional
        Primary site (required if `title` not provided).
    hist : str, optional
        Histology (required if `title` not provided).
    """
    if not title:
        if not (site and hist):
            raise ValueError("Either `title` or both `site` and `hist` must be provided.")

    endpoint = f"{year}/table"
    params: Dict[str, Any] = {}
    put(params, "title", title)
    put(params, "site", site)
    put(params, "hist", hist)
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


def list_surgery_tables(
    client: SeerClient,
    year: str,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/surgery/{year}/tables
    Return all the available table titles for the specified year.

    Parameters
    ----------
    year : str
        Year of the data; use "latest" for the latest available year.
    """
    endpoint = f"{year}/tables"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)
