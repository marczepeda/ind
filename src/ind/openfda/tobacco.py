"""
OpenFDA – Tobacco endpoints

Base:
    https://api.fda.gov/tobacco/

Implements the Tobacco Problem dataset:
    https://api.fda.gov/tobacco/problem.json

This module mirrors the structure of other OpenFDA endpoint modules in ind.openfda.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from .client import OpenFDAClient
from .types import APIResponse, Meta, MetaResults
from .utils import build_params
from .query import q

BASE = "/tobacco"
ENDPOINT_PROBLEM = "tobacco/problem"


def _wrap(data: Dict[str, Any]) -> APIResponse[Dict[str, Any]]:
    meta_raw = data.get("meta", {})
    res_raw = meta_raw.get("results", {})
    meta = Meta(
        disclaimer=meta_raw.get("disclaimer"),
        terms=meta_raw.get("terms"),
        license=meta_raw.get("license"),
        last_updated=meta_raw.get("last_updated"),
        results=MetaResults(
            total=res_raw.get("total"),
            skip=res_raw.get("skip"),
            limit=res_raw.get("limit"),
        ),
    )
    return APIResponse(meta=meta, results=data.get("results"))


# ----------------------------
# /tobacco/problem.json
# ----------------------------

def search_problems(
    client: OpenFDAClient,
    *,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    sort: Optional[str] = None,
    count: Optional[str] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> APIResponse[Dict[str, Any]]:
    """Query the Tobacco Problem endpoint."""
    params = build_params(search=search, limit=limit, skip=skip, sort=sort, count=count, extra=extra)
    data = client.request_json("GET", f"{BASE}/problem.json", params=params)
    return _wrap(data)


# ============================
# Convenience helpers (schema-validated via tobacco_problem.yaml)
# ============================

# Generic builder

def search_tobacco_problems_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_problems(client, search=q(field, term, endpoint=ENDPOINT_PROBLEM), **kw)


def count_tobacco_problems_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_problems(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar based on tobacco_problem.yaml fields

def search_tobacco_problems_by_report_id(client: OpenFDAClient, report_id: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_tobacco_problems_by_field(client, "report_id", report_id, **kw)


def search_tobacco_problems_by_date_submitted(client: OpenFDAClient, date: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_tobacco_problems_by_field(client, "date_submitted", date, **kw)


def search_tobacco_problems_by_tobacco_product(client: OpenFDAClient, product: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_tobacco_problems_by_field(client, "tobacco_products", product, **kw)


def search_tobacco_problems_by_reported_health_problem(client: OpenFDAClient, problem: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_tobacco_problems_by_field(client, "reported_health_problems", problem, **kw)


def search_tobacco_problems_by_reported_product_problem(client: OpenFDAClient, problem: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_tobacco_problems_by_field(client, "reported_product_problems", problem, **kw)


def search_tobacco_problems_by_nonuser_affected(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_tobacco_problems_by_field(client, "nonuser_affected", value, **kw)


def _range(field: str, start: str, end: str) -> str:
    return f"{field}:[{start} TO {end}]"


def search_tobacco_problems_between_date_submitted(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_problems(client, search=_range("date_submitted", start, end), **kw)


# Facet helpers for common buckets

def count_tobacco_problems_by_tobacco_product(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_tobacco_problems_by_field(client, "tobacco_products", limit=limit, **kw)


def count_tobacco_problems_by_reported_health_problem(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_tobacco_problems_by_field(client, "reported_health_problems", limit=limit, **kw)


def count_tobacco_problems_by_reported_product_problem(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_tobacco_problems_by_field(client, "reported_product_problems", limit=limit, **kw)