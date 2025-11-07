"""
patent.applications — Patent Application endpoints

Implements the complete `/api/v1/patent/applications/*` family of endpoints,
including search, download, and per-application data retrieval.

Endpoints
----------
Search:
  • GET/POST /api/v1/patent/applications/search
  • GET/POST /api/v1/patent/applications/search/download

Per-application resources:
  • GET /api/v1/patent/applications/{applicationNumberText}
  • GET /api/v1/patent/applications/{applicationNumberText}/meta-data
  • GET /api/v1/patent/applications/{applicationNumberText}/adjustment
  • GET /api/v1/patent/applications/{applicationNumberText}/assignment
  • GET /api/v1/patent/applications/{applicationNumberText}/attorney
  • GET /api/v1/patent/applications/{applicationNumberText}/continuity
  • GET /api/v1/patent/applications/{applicationNumberText}/foreign-priority
  • GET /api/v1/patent/applications/{applicationNumberText}/transactions
  • GET /api/v1/patent/applications/{applicationNumberText}/documents
  • GET /api/v1/patent/applications/{applicationNumberText}/associated-documents

Features
---------
- Automatic GET→POST fallback on HTTP 413 “Payload Too Large”.
- Streamed file downloads for `/search/download`.
- Strongly-typed request filters (Filter, RangeFilter, Sort, Pagination).
- All errors normalized via USPTOClient’s exception hierarchy.

Example
-------
>>> from ind.uspto.client import USPTOClient
>>> from ind.uspto.patent import search_applications
>>> client = USPTOClient(api_key="YOUR_KEY")
>>> res = search_applications(client, q='applicationMetaData.applicationTypeLabelName:Utility')
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional, Sequence

from ..client import USPTOClient, PayloadTooLargeError
from ..types import (
    Filter, RangeFilter, SortOrder, Sort, Pagination,
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
def search_applications(
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
    GET/POST /api/v1/patent/applications/search

    - q: OpenSearch/Lucene-style query string.
    - filters: list of Filter(name, [values...])
    - range_filters: list of RangeFilter(field, valueFrom, valueTo) ('yyyy-MM-dd' for dates)
    - sort: list of Sort(field, order) where order ∈ {Asc, asc, Desc, desc}
    - fields: list of field names to include
    - pagination: Pagination(offset, limit)
    - facets: list of facet field names
    - method: "auto" tries GET first and falls back to POST on 413
    - troubleshoot: if True, pretty-print the built request body before sending
    """
    path = "/api/v1/patent/applications/search"
    body = _build_request_dict(q, filters, range_filters, sort, fields, pagination, facets)
    maybe_pprint(body, troubleshoot, "Patent Applications Search Body")
    return search_auto_request_json(client, path, body, method=method)

def download_search(
    client: USPTOClient,
    *,
    q: Optional[str] = None,
    filters: Optional[Sequence[Filter]] = None,
    range_filters: Optional[Sequence[RangeFilter]] = None,
    sort: Optional[Sequence[Sort]] = None,
    fields: Optional[Iterable[str]] = None,
    pagination: Optional[Pagination] = None,
    facets: Optional[Iterable[str]] = None,
    method: str = "auto",            # "auto" | "GET" | "POST"
    dest_path: Optional[str] = None, # if set, stream to file and return path
    troubleshoot: bool = False,
) -> bytes | str:
    """
    GET/POST /api/v1/patent/applications/search/download

    Returns:
      - bytes content (if dest_path is None)
      - dest_path string (if provided)
    """
    path = "/api/v1/patent/applications/search/download"
    body = _build_request_dict(q, filters, range_filters, sort, fields, pagination, facets)
    maybe_pprint(body, troubleshoot, "Patent Applications Download Body")
    return search_auto_download(client, path, body, method=method, dest_path=dest_path)

# =======================
# Per-application subresources
# =======================
def get_application(
    client: USPTOClient,
    application_number: str,
) -> Dict[str, Any]:
    """
    GET /api/v1/patent/applications/{applicationNumberText}
    """
    return client.request_json("GET", f"/api/v1/patent/applications/{application_number}")


def get_meta_data(client: USPTOClient, application_number: str) -> Dict[str, Any]:
    """GET /api/v1/patent/applications/{applicationNumberText}/meta-data"""
    return client.request_json("GET", f"/api/v1/patent/applications/{application_number}/meta-data")


def get_adjustment(client: USPTOClient, application_number: str) -> Dict[str, Any]:
    """GET /api/v1/patent/applications/{applicationNumberText}/adjustment"""
    return client.request_json("GET", f"/api/v1/patent/applications/{application_number}/adjustment")


def get_assignment(client: USPTOClient, application_number: str) -> Dict[str, Any]:
    """GET /api/v1/patent/applications/{applicationNumberText}/assignment"""
    return client.request_json("GET", f"/api/v1/patent/applications/{application_number}/assignment")


def get_attorney(client: USPTOClient, application_number: str) -> Dict[str, Any]:
    """GET /api/v1/patent/applications/{applicationNumberText}/attorney"""
    return client.request_json("GET", f"/api/v1/patent/applications/{application_number}/attorney")


def get_continuity(client: USPTOClient, application_number: str) -> Dict[str, Any]:
    """GET /api/v1/patent/applications/{applicationNumberText}/continuity"""
    return client.request_json("GET", f"/api/v1/patent/applications/{application_number}/continuity")


def get_foreign_priority(client: USPTOClient, application_number: str) -> Dict[str, Any]:
    """GET /api/v1/patent/applications/{applicationNumberText}/foreign-priority"""
    return client.request_json("GET", f"/api/v1/patent/applications/{application_number}/foreign-priority")


def get_transactions(client: USPTOClient, application_number: str) -> Dict[str, Any]:
    """GET /api/v1/patent/applications/{applicationNumberText}/transactions"""
    return client.request_json("GET", f"/api/v1/patent/applications/{application_number}/transactions")


def get_documents(client: USPTOClient, application_number: str) -> Dict[str, Any]:
    """GET /api/v1/patent/applications/{applicationNumberText}/documents"""
    return client.request_json("GET", f"/api/v1/patent/applications/{application_number}/documents")


def get_associated_documents(client: USPTOClient, application_number: str) -> Dict[str, Any]:
    """GET /api/v1/patent/applications/{applicationNumberText}/associated-documents"""
    return client.request_json("GET", f"/api/v1/patent/applications/{application_number}/associated-documents")


__all__ = [
    # schema types
    "Filter", "RangeFilter", "SortOrder", "Sort", "Pagination",
    # search
    "search_applications", "download_search",
    # per-application
    "get_application", "get_meta_data", "get_adjustment", "get_assignment",
    "get_attorney", "get_continuity", "get_foreign_priority", "get_transactions",
    "get_documents", "get_associated_documents",
]