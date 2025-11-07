"""
types.py — Shared request schema types and utilities

Defines reusable dataclasses and helper functions that model
common request parameters across USPTO Open Data Portal APIs:
  • Filter(name, [values...])
  • RangeFilter(field, valueFrom, valueTo)
  • Sort(field, order)
  • Pagination(offset, limit)
  • SortOrder enum (Asc/Desc)

Also includes small helpers:
  - comma_param(v): join a string sequence for comma-delimited API params.
  - string_or_json(v): encode dict/list parameters as compact JSON strings.
  - json_query_params(d): prepare GET query dictionaries with minimal JSON encoding.

Used by:
  - patent.applications
  - bulk.products
  - petitions.decisions
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Sequence, Union
import json
from .client import ApiError

# ---------- Shared request schema bits ----------

@dataclass
class Filter:
    name: str
    value: Sequence[str]

@dataclass
class RangeFilter:
    field: str
    valueFrom: str   # for dates: "yyyy-MM-dd"
    valueTo: str

class SortOrder(str, Enum):
    Asc = "Asc"
    asc = "asc"
    Desc = "Desc"
    desc = "desc"

@dataclass
class Sort:
    field: str
    order: SortOrder

@dataclass
class Pagination:
    offset: int = 0
    limit: int = 25

# ---------- Convenience protocol-ish helpers ----------

StrOrSeq = Union[str, Sequence[str]]

def comma_param(v: Optional[StrOrSeq]) -> Optional[str]:
    if not v:
        return None
    if isinstance(v, str):
        return v
    return ",".join([str(x) for x in v])

def string_or_json(v: Optional[Union[str, Mapping[str, Any], Sequence[Any]]]) -> Optional[str]:
    """
    For GET-style params that accept either a raw string or a JSON-encoded structure.
    If `v` is dict/list, encode compact JSON. If it's a str, return as-is.
    """
    if not v:
        return None
    if isinstance(v, str):
        return v
    
    return json.dumps(v, separators=(",", ":"))

def json_query_params(d: Mapping[str, Any]) -> Dict[str, Any]:
    """
    For GET requests: encode lists/dicts as compact JSON strings; keep scalars as-is.
    """
    params: Dict[str, Any] = {}
    for k, v in d.items():
        if isinstance(v, (list, dict)):
            params[k] = json.dumps(v, separators=(",", ":"))
        else:
            params[k] = v
    return params

# ---------- Generic GET/POST bridging for search-like endpoints ----------
def encode_get_params(body: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Convert a POST-style search body into GET query params expected by ODP.
    Rules:
      - q: as-is (string)
      - pagination: flatten to offset & limit
      - fields, facets: comma-separated strings
      - sort, filters, rangeFilters: JSON-encoded compact strings
      - everything else: pass through if scalar (e.g., 'format')
    """
    params: Dict[str, Any] = {}

    # q
    q = body.get("q")
    if q is not None:
        params["q"] = q

    # pagination -> offset/limit
    pag = body.get("pagination")
    if isinstance(pag, Mapping):
        off = pag.get("offset")
        lim = pag.get("limit")
        if off is not None:
            params["offset"] = int(off)
        if lim is not None:
            params["limit"] = int(lim)

    # fields/facets -> comma-separated
    fields = body.get("fields")
    if fields:
        params["fields"] = ",".join(map(str, fields))
    facets = body.get("facets")
    if facets:
        params["facets"] = ",".join(map(str, facets))

    # Complex arrays -> compact JSON
    for key in ("sort", "filters", "rangeFilters"):
        val = body.get(key)
        if val:
            params[key] = json.dumps(val, separators=(",", ":"))

    # Pass-through simple extras (e.g., 'format' for /search/download)
    for k, v in body.items():
        if k in ("q", "pagination", "fields", "facets", "sort", "filters", "rangeFilters"):
            continue
        # keep scalars only
        if isinstance(v, (str, int, float, bool)) and v is not False:
            params[k] = v

    return params


def search_auto_request_json(
    client,
    path: str,
    body: Dict[str, Any],
    *,
    method: str = "auto",
):
    """
    For endpoints that accept BOTH:
      GET  .../search?{encoded params}
      POST .../search  (JSON body)

    Behavior:
      - method="POST" → always POST
      - method="GET"  → always GET
      - method="auto" → try GET; on ANY error, try POST; if POST fails, raise POST error
    """
    m = method.upper()
    if m == "POST":
        return client.request_json("POST", path, json_body=body)
    if m == "GET":
        params = encode_get_params(body)
        return client.request_json("GET", path, params=params or None)

    # auto
    try:
        params = encode_get_params(body)
        return client.request_json("GET", path, params=params or None)
    except Exception:
        # Any error → try POST once
        return client.request_json("POST", path, json_body=body)


def search_auto_download(
    client,
    path: str,
    body: Dict[str, Any],
    *,
    method: str = "auto",
    dest_path: Optional[str] = None,
):
    """
    For endpoints that accept BOTH:
      GET  .../download?{encoded params}
      POST .../download  (JSON body)

    Behavior:
      - method="POST" → always POST
      - method="GET"  → always GET
      - method="auto" → try GET; on ANY error, try POST; if POST fails, raise POST error
    """
    m = method.upper()
    if m == "POST":
        return client.download("POST", path, json_body=body, dest_path=dest_path)
    if m == "GET":
        params = encode_get_params(body)
        return client.download("GET", path, params=params or None, dest_path=dest_path)

    # auto
    try:
        params = encode_get_params(body)
        return client.download("GET", path, params=params or None, dest_path=dest_path)
    except Exception:
        return client.download("POST", path, json_body=body, dest_path=dest_path)

# ---------- Troubleshooting utilities ----------

def maybe_pprint(obj: Any, enable: bool, header: str = "Request body:") -> None:
    """
    Print a formatted representation of `obj` when troubleshooting is enabled.

    Parameters
    ----------
    obj : Any
        Object (usually a dict) to pretty-print.
    enable : bool
        If True, pretty-print `obj`; otherwise do nothing.
    header : str
        Optional header to display above the printed data.
    """
    if not enable:
        return
    from pprint import pprint
    print(f"\n{header}:")
    pprint(obj)
    print()