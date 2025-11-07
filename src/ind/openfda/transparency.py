

from __future__ import annotations
"""
OpenFDA – Transparency endpoints

Base:
    https://api.fda.gov/transparency/

Implements Complete Response Letters (CRL):
    https://api.fda.gov/transparency/crl.json

This mirrors other ind.openfda modules:
- typed APIResponse wrapper
- endpoint wrapper (search)
- schema-validated convenience helpers using `q()`
- simple count and date-range helpers
"""

from typing import Any, Dict, Mapping, Optional

from .client import OpenFDAClient
from .types import APIResponse, Meta, MetaResults
from .utils import build_params
from .query import q

BASE = "/transparency"
ENDPOINT_CRL = "transparency/crl"


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
# /transparency/crl.json
# ----------------------------

def search_crl(
    client: OpenFDAClient,
    *,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    sort: Optional[str] = None,
    count: Optional[str] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> APIResponse[Dict[str, Any]]:
    """Query the Complete Response Letters (CRL) dataset."""
    params = build_params(search=search, limit=limit, skip=skip, sort=sort, count=count, extra=extra)
    data = client.request_json("GET", f"{BASE}/crl.json", params=params)
    return _wrap(data)


# ============================
# Convenience helpers (schema-validated via transparency_crl.yaml)
# ============================

# Generic builder / facet

def search_crl_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Build `search=field:term` validated against the CRL endpoint schema."""
    return search_crl(client, search=q(field, term, endpoint=ENDPOINT_CRL), **kw)


def count_crl_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a CRL field (returns buckets instead of documents)."""
    return search_crl(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar based on transparency_crl.yaml fields

def search_crl_by_file_name(client: OpenFDAClient, name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_crl_by_field(client, "file_name", name, **kw)


def search_crl_by_application_number(client: OpenFDAClient, app_no: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_crl_by_field(client, "application_number", app_no, **kw)


def search_crl_by_letter_type(client: OpenFDAClient, letter_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_crl_by_field(client, "letter_type", letter_type, **kw)


def search_crl_by_company_name(client: OpenFDAClient, company: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_crl_by_field(client, "company_name", company, **kw)


def search_crl_by_company_rep(client: OpenFDAClient, rep: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_crl_by_field(client, "company_rep", rep, **kw)


def search_crl_by_company_address(client: OpenFDAClient, address: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_crl_by_field(client, "company_address", address, **kw)


def search_crl_by_approval_name(client: OpenFDAClient, name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_crl_by_field(client, "approval_name", name, **kw)


def search_crl_by_approval_title(client: OpenFDAClient, title: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_crl_by_field(client, "approval_title", title, **kw)


def search_crl_by_approval_center(client: OpenFDAClient, center: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_crl_by_field(client, "approval_center", center, **kw)


def search_crl_full_text(client: OpenFDAClient, phrase: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_crl_by_field(client, "text", phrase, **kw)


# Date range helpers (YYYYMMDD)

def _range(field: str, start: str, end: str) -> str:
    return f"{field}:[{start} TO {end}]"


def search_crl_between_letter_date(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_crl(client, search=_range("letter_date", start, end), **kw)


# Facet helpers for common buckets

def count_crl_by_letter_type(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_crl_by_field(client, "letter_type", limit=limit, **kw)


def count_crl_by_company_name(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_crl_by_field(client, "company_name", limit=limit, **kw)


def count_crl_by_approval_center(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_crl_by_field(client, "approval_center", limit=limit, **kw)