from __future__ import annotations
from typing import Any, Dict, Mapping, Optional

from .client import OpenFDAClient
from .types import APIResponse, Meta, MetaResults
from .utils import build_params
from .query import q

BASE = "/food"
ENDPOINT_ENFORCEMENT = "food/enforcement"
ENDPOINT_EVENT = "food/event"


def _wrap(data: Dict[str, Any]) -> APIResponse[Dict[str, Any]]:
    meta_raw = data.get("meta", {})
    res_raw = meta_raw.get("results", {})
    meta = Meta(
        disclaimer=meta_raw.get("disclaimer"),
        terms=meta_raw.get("terms"),
        license=meta_raw.get("license"),
        last_updated=meta_raw.get("last_updated"),
        results=MetaResults(
            total=res_raw.get("total"), skip=res_raw.get("skip"), limit=res_raw.get("limit")
        ),
    )
    return APIResponse(meta=meta, results=data.get("results"))



def search_enforcements(client: OpenFDAClient, *, search: Optional[str] = None, limit: Optional[int] = None, skip: Optional[int] = None, sort: Optional[str] = None, count: Optional[str] = None, extra: Optional[Mapping[str, Any]] = None) -> APIResponse[Dict[str, Any]]:
    params = build_params(search=search, limit=limit, skip=skip, sort=sort, count=count, extra=extra)
    data = client.request_json("GET", f"{BASE}/enforcement.json", params=params)
    return _wrap(data)


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
    params = build_params(search=search, limit=limit, skip=skip, sort=sort, count=count, extra=extra)
    data = client.request_json("GET", f"{BASE}/event.json", params=params)
    return _wrap(data)


# ============================
# Food Enforcement endpoint conveniences
# ============================

# Generic builders validated against the food enforcement schema

def search_food_enforcements_by_field(
    client: OpenFDAClient,
    field: str,
    term: str,
    /,
    **kw: Any,
) -> APIResponse[Dict[str, Any]]:
    """Search with `search=field:term` using the food enforcement schema for validation."""
    return search_enforcements(client, search=q(field, term, endpoint=ENDPOINT_ENFORCEMENT), **kw)


def count_food_enforcements_by_field(
    client: OpenFDAClient,
    field: str,
    /,
    limit: int = 1000,
    **kw: Any,
) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a food enforcement field (returns buckets)."""
    return search_enforcements(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar based on food_enforcement.yaml fields

def search_food_enforcements_by_classification(client: OpenFDAClient, cls: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Recall class: "Class I", "Class II", or "Class III"."""
    return search_food_enforcements_by_field(client, "classification", cls, **kw)


def search_food_enforcements_by_recalling_firm(client: OpenFDAClient, firm: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_enforcements_by_field(client, "recalling_firm", firm, **kw)


def search_food_enforcements_by_status(client: OpenFDAClient, status: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    # One of: On-Going, Completed, Terminated, Pending
    return search_food_enforcements_by_field(client, "status", status, **kw)


def search_food_enforcements_by_state(client: OpenFDAClient, state: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_enforcements_by_field(client, "state", state, **kw)


def search_food_enforcements_by_city(client: OpenFDAClient, city: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_enforcements_by_field(client, "city", city, **kw)


def search_food_enforcements_by_country(client: OpenFDAClient, country: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_enforcements_by_field(client, "country", country, **kw)


def search_food_enforcements_by_product_type(client: OpenFDAClient, product_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    # Typically "Food"
    return search_food_enforcements_by_field(client, "product_type", product_type, **kw)


def search_food_enforcements_by_product_code(client: OpenFDAClient, code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_enforcements_by_field(client, "product_code", code, **kw)


def search_food_enforcements_by_product_description(client: OpenFDAClient, text: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_enforcements_by_field(client, "product_description", text, **kw)


def search_food_enforcements_by_product_quantity(client: OpenFDAClient, text: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_enforcements_by_field(client, "product_quantity", text, **kw)


def search_food_enforcements_by_reason_for_recall(client: OpenFDAClient, text: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_enforcements_by_field(client, "reason_for_recall", text, **kw)


def search_food_enforcements_by_event_id(client: OpenFDAClient, event_id: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_enforcements_by_field(client, "event_id", event_id, **kw)


def search_food_enforcements_by_recall_number(client: OpenFDAClient, recall_number: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_enforcements_by_field(client, "recall_number", recall_number, **kw)


def search_food_enforcements_by_voluntary_mandated(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_enforcements_by_field(client, "voluntary_mandated", value, **kw)


def search_food_enforcements_by_distribution_pattern(client: OpenFDAClient, text: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_enforcements_by_field(client, "distribution_pattern", text, **kw)


def search_food_enforcements_by_code_info(client: OpenFDAClient, text: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_enforcements_by_field(client, "code_info", text, **kw)


def search_food_enforcements_by_more_code_info(client: OpenFDAClient, text: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_enforcements_by_field(client, "more_code_info", text, **kw)


def search_food_enforcements_by_initial_firm_notification(client: OpenFDAClient, method: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_enforcements_by_field(client, "initial_firm_notification", method, **kw)


# Date range helpers (YYYYMMDD)

def _range_food_enf(field: str, start: str, end: str) -> str:
    return f"{field}:[{start} TO {end}]"


def search_food_enforcements_between_report_date(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_enforcements(client, search=_range_food_enf("report_date", start, end), **kw)


def search_food_enforcements_between_recall_initiation_date(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_enforcements(client, search=_range_food_enf("recall_initiation_date", start, end), **kw)


def search_food_enforcements_between_center_classification_date(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_enforcements(client, search=_range_food_enf("center_classification_date", start, end), **kw)


def search_food_enforcements_between_termination_date(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_enforcements(client, search=_range_food_enf("termination_date", start, end), **kw)


# Facet helpers for common buckets

def count_food_enforcements_by_classification(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_food_enforcements_by_field(client, "classification", limit=limit, **kw)


def count_food_enforcements_by_status(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_food_enforcements_by_field(client, "status", limit=limit, **kw)


def count_food_enforcements_by_state(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_food_enforcements_by_field(client, "state", limit=limit, **kw)


def count_food_enforcements_by_product_type(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_food_enforcements_by_field(client, "product_type", limit=limit, **kw)


# ============================
# Food Adverse Event endpoint conveniences
# ============================

# Generic builders validated against the food event schema

def search_food_events_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Search with `search=field:term` using the food event schema for validation."""
    return search_events(client, search=q(field, term, endpoint=ENDPOINT_EVENT), **kw)


def count_food_events_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a food event field (returns buckets)."""
    return search_events(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar based on food_event.yaml fields
# Consumer demographics

def search_food_events_by_consumer_age(client: OpenFDAClient, age: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_events_by_field(client, "consumer.age", age, **kw)


def search_food_events_by_consumer_age_unit(client: OpenFDAClient, unit: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_events_by_field(client, "consumer.age_unit", unit, **kw)


def search_food_events_by_consumer_gender(client: OpenFDAClient, gender: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_events_by_field(client, "consumer.gender", gender, **kw)


# Product details

def search_food_events_by_product_industry_code(client: OpenFDAClient, code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_events_by_field(client, "products.industry_code", code, **kw)


def search_food_events_by_product_industry_name(client: OpenFDAClient, name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_events_by_field(client, "products.industry_name", name, **kw)


def search_food_events_by_product_brand_name(client: OpenFDAClient, brand: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_events_by_field(client, "products.name_brand", brand, **kw)


def search_food_events_by_product_role(client: OpenFDAClient, role: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_events_by_field(client, "products.role", role, **kw)


# Reactions and outcomes

def search_food_events_by_reaction(client: OpenFDAClient, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_events_by_field(client, "reactions", term, **kw)


def search_food_events_by_outcome(client: OpenFDAClient, outcome: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_events_by_field(client, "outcomes", outcome, **kw)


# IDs and dates

def search_food_events_by_report_number(client: OpenFDAClient, report_number: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_food_events_by_field(client, "report_number", report_number, **kw)


def _range_food_event(field: str, start: str, end: str) -> str:
    return f"{field}:[{start} TO {end}]"


def search_food_events_between_date_created(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_events(client, search=_range_food_event("date_created", start, end), **kw)


def search_food_events_between_date_started(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_events(client, search=_range_food_event("date_started", start, end), **kw)


# Facet helpers for common buckets

def count_food_events_by_reaction(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_food_events_by_field(client, "reactions", limit=limit, **kw)


def count_food_events_by_outcome(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_food_events_by_field(client, "outcomes", limit=limit, **kw)


def count_food_events_by_industry_code(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_food_events_by_field(client, "products.industry_code", limit=limit, **kw)


def count_food_events_by_role(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_food_events_by_field(client, "products.role", limit=limit, **kw)


def count_food_events_by_gender(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_food_events_by_field(client, "consumer.gender", limit=limit, **kw)


def count_food_events_by_age_unit(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_food_events_by_field(client, "consumer.age_unit", limit=limit, **kw)