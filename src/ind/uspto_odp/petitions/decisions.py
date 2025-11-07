"""
petitions.decisions — Petition Decision endpoints

Implements petition decision search, download, and single-record retrieval.

Endpoints
----------
Search:
  • POST/GET /api/v1/petition/decisions/search
  • POST/GET /api/v1/petition/decisions/search/download

Single Decision:
  • GET /api/v1/petition/decisions/{petitionDecisionRecordIdentifier}

Features
---------
- Unified request schema (Filter, RangeFilter, Sort, Pagination, facets).
- Optional `format` parameter for `/search/download` (e.g., CSV).
- Automatic GET→POST fallback on HTTP 413 “Payload Too Large”.
- Optional `includeDocuments=true` for detailed decision files.

Example
-------
>>> from ind.uspto.client import USPTOClient
>>> from ind.uspto.petitions import search_decisions, get_decision
>>> client = USPTOClient(api_key="YOUR_KEY")
>>> res = search_decisions(client, q='finalDecidingOfficeName:OFFICE OF PETITIONS')
>>> pid = res["petitionDecisionDataBag"][0]["petitionDecisionRecordIdentifier"]
>>> detail = get_decision(client, pid, include_documents=True)
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional, Sequence

from ..client import USPTOClient, PayloadTooLargeError
from ..types import (
    Filter, RangeFilter, Sort, Pagination,
    encode_get_params, search_auto_request_json, search_auto_download, maybe_pprint
)

# =======================
# Internal helpers
# =======================

def _build_request_dict(
    q: Optional[str],
    filters: Optional[Sequence[Filter]],
    range_filters: Optional[Sequence[RangeFilter]],
    sort: Optional[Sequence[Sort]],
    fields: Optional[Iterable[str]],
    pagination: Optional[Pagination],
    facets: Optional[Iterable[str]],
) -> Dict[str, Any]:
    req: Dict[str, Any] = {}
    if q is not None:
        req["q"] = q
    if filters:
        req["filters"] = [{"name": f.name, "value": list(f.value)} for f in filters]
    if range_filters:
        req["rangeFilters"] = [
            {"field": r.field, "valueFrom": r.valueFrom, "valueTo": r.valueTo}
            for r in range_filters
        ]
    if sort:
        req["sort"] = [{"field": s.field, "order": s.order.value} for s in sort]
    if fields:
        req["fields"] = list(fields)
    if pagination:
        req["pagination"] = {"offset": pagination.offset, "limit": pagination.limit}
    if facets:
        req["facets"] = list(facets)
    return req

# =======================
# Search endpoints
# =======================

def search_decisions(
    client: USPTOClient,
    *,
    q: Optional[str] = None,
    filters: Optional[Sequence[Filter]] = None,
    range_filters: Optional[Sequence[RangeFilter]] = None,
    sort: Optional[Sequence[Sort]] = None,
    fields: Optional[Iterable[str]] = None,
    pagination: Optional[Pagination] = None,
    facets: Optional[Iterable[str]] = None,
    method: str = "auto",  # "auto" | "GET" | "POST"
    troubleshoot: bool = False,
) -> Dict[str, Any]:
    """
    POST/GET /api/v1/petition/decisions/search

    - All request fields are optional.
    - "auto": try GET (query params) and fall back to POST with JSON body on 413.
    """
    path = "/api/v1/petition/decisions/search"
    body = _build_request_dict(q, filters, range_filters, sort, fields, pagination, facets)
    maybe_pprint(body, troubleshoot, "Petition Decisions Search Body")
    return search_auto_request_json(client, path, body, method=method)

def download_search_decisions(
    client: USPTOClient,
    *,
    q: Optional[str] = None,
    filters: Optional[Sequence[Filter]] = None,
    range_filters: Optional[Sequence[RangeFilter]] = None,
    sort: Optional[Sequence[Sort]] = None,
    fields: Optional[Iterable[str]] = None,
    pagination: Optional[Pagination] = None,
    facets: Optional[Iterable[str]] = None,      # only documented in POST body; we allow parity
    format: Optional[str] = None,                # e.g., "csv" or "json" (per docs)
    method: str = "auto",                        # "auto" | "GET" | "POST"
    dest_path: Optional[str] = None,             # if provided, stream to file; else return bytes
    troubleshoot: bool = False,
) -> bytes | str:
    """
    POST/GET /api/v1/petition/decisions/search/download

    Returns:
      - bytes (if dest_path is None)
      - dest_path (if provided)
    """
    path = "/api/v1/petition/decisions/search/download"
    body = _build_request_dict(q, filters, range_filters, sort, fields, pagination, facets)
    if format:
        # Only part of the POST example, but GET supports a 'format' query param per docs.
        body["format"] = format
    maybe_pprint(body, troubleshoot, "Petition Decisions Download Body")
    return search_auto_download(client, path, body, method=method, dest_path=dest_path)

# =======================
# Single decision by identifier
# =======================

def get_decision(
    client: USPTOClient,
    petition_decision_record_identifier: str,
    *,
    include_documents: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    GET /api/v1/petition/decisions/{petitionDecisionRecordIdentifier}

    Parameters
    ----------
    petition_decision_record_identifier : str
        The petition decision record identifier (UUID-like value from search results).
    include_documents : bool, optional
        If True, include 'documentBag' in the response. If None, omit the parameter.

    Returns
    -------
    dict
        Parsed JSON response with a 'petitionDecisionDataBag' list; may include 'documentBag'.
    """
    path = f"/api/v1/petition/decisions/{petition_decision_record_identifier}"
    params: Dict[str, Any] = {}
    if include_documents is True:
        params["includeDocuments"] = "true"
    elif include_documents is False:
        params["includeDocuments"] = "false"
    else:
        params = None

    return client.request_json("GET", path, params=params)