

from __future__ import annotations
"""
OpenFDA – Cosmetic endpoints

Base:
    https://api.fda.gov/cosmetic/

This module currently implements the adverse event dataset:
    https://api.fda.gov/cosmetic/event.json

It mirrors the structure used across the other ind.openfda modules:
- typed APIResponse wrapper
- endpoint wrapper (search)
- schema-validated convenience helpers using `q()`
- small set of focused count/range helpers
"""

from typing import Any, Dict, Mapping, Optional

from .client import OpenFDAClient
from .types import APIResponse, Meta, MetaResults
from .utils import build_params
from .query import q

BASE = "/cosmetic"
ENDPOINT_EVENT = "cosmetic/event"


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
# /cosmetic/event.json
# ----------------------------

def search_events(
    client: OpenFDAClient,
    *,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    sort: Optional[str] = None,
    count: Optional[str] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> APIResponse[Dict[str, Any]]:
    """Search cosmetic adverse events.

    Parameters mirror the OpenFDA API (Solr-style `search`, optional `count`,
    and paging with `limit`/`skip`). Limit is clamped server-side to 1000.
    """
    params = build_params(search=search, limit=limit, skip=skip, sort=sort, count=count, extra=extra)
    data = client.request_json("GET", f"{BASE}/event.json", params=params)
    return _wrap(data)


# ============================
# Convenience helpers (schema-validated via cosmetic_event.yaml)
# ============================

# Generic builder/aggregator

def search_cosmetic_events_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Build `search=field:term` validated against the endpoint schema."""
    return search_events(client, search=q(field, term, endpoint=ENDPOINT_EVENT), **kw)


def count_cosmetic_events_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a field (returns buckets instead of documents)."""
    return search_events(client, count=f"{field}.exact", limit=limit, **kw)


# IDs & meta

def search_cosmetic_events_by_report_number(client: OpenFDAClient, report_number: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_cosmetic_events_by_field(client, "report_number", report_number, **kw)


def search_cosmetic_events_by_report_type(client: OpenFDAClient, report_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_cosmetic_events_by_field(client, "report_type", report_type, **kw)


def search_cosmetic_events_by_legacy_report_id(client: OpenFDAClient, legacy_id: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_cosmetic_events_by_field(client, "legacy_report_id", legacy_id, **kw)


# Product block

def search_cosmetic_events_by_product_name(client: OpenFDAClient, product_name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_cosmetic_events_by_field(client, "products.product_name", product_name, **kw)


def search_cosmetic_events_by_product_role(client: OpenFDAClient, role: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    # role ∈ {Suspect, Concomitant}
    return search_cosmetic_events_by_field(client, "products.role", role, **kw)


# Patient demographics

def search_cosmetic_events_by_patient_gender(client: OpenFDAClient, gender: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_cosmetic_events_by_field(client, "patient.gender", gender, **kw)


def search_cosmetic_events_by_patient_age(client: OpenFDAClient, age: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_cosmetic_events_by_field(client, "patient.age", age, **kw)


def search_cosmetic_events_by_patient_age_unit(client: OpenFDAClient, unit: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    # unit ∈ {Day(s), Week(s), Month(s), Year(s), Decade(s), Not Available}
    return search_cosmetic_events_by_field(client, "patient.age_unit", unit, **kw)


# Clinical fields

def search_cosmetic_events_by_reaction(client: OpenFDAClient, meddra_term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    # Reactions are MedDRA terms (British English, e.g., DIARRHOEA)
    return search_cosmetic_events_by_field(client, "reactions", meddra_term, **kw)


def search_cosmetic_events_by_outcome(client: OpenFDAClient, outcome: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    # outcome includes values like HOSPITALIZATION, LIFE THREATENING, etc.
    return search_cosmetic_events_by_field(client, "outcomes", outcome, **kw)


# Date range helpers (YYYYMMDD)

def _range(field: str, start: str, end: str) -> str:
    return f"{field}:[{start} TO {end}]"


def search_cosmetic_events_between_event_date(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_events(client, search=_range("event_date", start, end), **kw)


def search_cosmetic_events_between_initial_received_date(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_events(client, search=_range("initial_received_date", start, end), **kw)


def search_cosmetic_events_between_latest_received_date(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_events(client, search=_range("latest_received_date", start, end), **kw)


# Facet helpers

def count_cosmetic_events_by_reaction(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_cosmetic_events_by_field(client, "reactions", limit=limit, **kw)


def count_cosmetic_events_by_outcome(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_cosmetic_events_by_field(client, "outcomes", limit=limit, **kw)


def count_cosmetic_events_by_product_role(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_cosmetic_events_by_field(client, "products.role", limit=limit, **kw)


def count_cosmetic_events_by_gender(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_cosmetic_events_by_field(client, "patient.gender", limit=limit, **kw)


def count_cosmetic_events_by_age_unit(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_cosmetic_events_by_field(client, "patient.age_unit", limit=limit, **kw)