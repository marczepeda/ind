from __future__ import annotations
from typing import Any, Dict, Mapping, Optional

from .client import OpenFDAClient
from .types import APIResponse, Meta, MetaResults
from .utils import build_params
from .query import q

# Constants for endpoints
BASE = "/device"
ENDPOINT_510K = "device/510k"
ENDPOINT_CLASSIFICATION = "device/classification"
ENDPOINT_ENFORCEMENT = "device/enforcement"
ENDPOINT_EVENT = "device/event"
ENDPOINT_PMA = "device/pma"
ENDPOINT_RECALL = "device/recall"
ENDPOINT_REGISTRATIONLISTING = "device/registrationlisting"
# /device/registrationlisting.json
ENDPOINT_COVID19SEROLOGY = "device/covid19serology"
ENDPOINT_UDI = "device/udi"
# /device/registrationlisting.json

# /device/registrationlisting.json

def search_registrationlisting(
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
    data = client.request_json("GET", f"{BASE}/registrationlisting.json", params=params)
    return _wrap(data)

# /device/covid19serology.json

def search_covid19serology(
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
    data = client.request_json("GET", f"{BASE}/covid19serology.json", params=params)
    return _wrap(data)

# /device/udi.json

def search_udi(
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
    data = client.request_json("GET", f"{BASE}/udi.json", params=params)
    return _wrap(data)


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


def search_events(client: OpenFDAClient, *, search: Optional[str] = None, limit: Optional[int] = None, skip: Optional[int] = None, sort: Optional[str] = None, count: Optional[str] = None, extra: Optional[Mapping[str, Any]] = None) -> APIResponse[Dict[str, Any]]:
    params = build_params(search=search, limit=limit, skip=skip, sort=sort, count=count, extra=extra)
    data = client.request_json("GET", f"{BASE}/event.json", params=params)
    return _wrap(data)


def search_enforcements(client: OpenFDAClient, *, search: Optional[str] = None, limit: Optional[int] = None, skip: Optional[int] = None, sort: Optional[str] = None, count: Optional[str] = None, extra: Optional[Mapping[str, Any]] = None) -> APIResponse[Dict[str, Any]]:
    params = build_params(search=search, limit=limit, skip=skip, sort=sort, count=count, extra=extra)
    data = client.request_json("GET", f"{BASE}/enforcement.json", params=params)
    return _wrap(data)


# /device/recall.json

def search_recalls(
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
    data = client.request_json("GET", f"{BASE}/recall.json", params=params)
    return _wrap(data)


# /device/510k.json


def search_510k(
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
    data = client.request_json("GET", f"{BASE}/510k.json", params=params)
    return _wrap(data)


# /device/classification.json

def search_pma(
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
    data = client.request_json("GET", f"{BASE}/pma.json", params=params)
    return _wrap(data)

def search_classification(
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
    data = client.request_json("GET", f"{BASE}/classification.json", params=params)
    return _wrap(data)


# ============================
# Device 510(k) endpoint conveniences
# ============================

# Generic builders validated against the 510k schema

def search_510k_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Search with `search=field:term` using the 510k schema for validation."""
    return search_510k(client, search=q(field, term, endpoint=ENDPOINT_510K), **kw)


def count_510k_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a 510k field (returns buckets instead of documents)."""
    return search_510k(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar based on device_510k.yaml fields

def search_510k_by_k_number(client: OpenFDAClient, k_number: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_510k_by_field(client, "k_number", k_number, **kw)


def search_510k_by_applicant(client: OpenFDAClient, applicant: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_510k_by_field(client, "applicant", applicant, **kw)


def search_510k_by_device_name(client: OpenFDAClient, name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_510k_by_field(client, "device_name", name, **kw)


def search_510k_by_product_code(client: OpenFDAClient, code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_510k_by_field(client, "product_code", code, **kw)


def search_510k_by_advisory_committee(client: OpenFDAClient, advisory: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_510k_by_field(client, "advisory_committee", advisory, **kw)


def search_510k_by_decision_code(client: OpenFDAClient, decision: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_510k_by_field(client, "decision_code", decision, **kw)


def search_510k_by_clearance_type(client: OpenFDAClient, clearance: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_510k_by_field(client, "clearance_type", clearance, **kw)


def search_510k_by_city(client: OpenFDAClient, city: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_510k_by_field(client, "city", city, **kw)


def search_510k_by_state(client: OpenFDAClient, state: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_510k_by_field(client, "state", state, **kw)


def search_510k_by_country(client: OpenFDAClient, country_code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_510k_by_field(client, "country_code", country_code, **kw)


def search_510k_by_decision_date_between(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Filter 510(k) clearances by decision date range `[YYYYMMDD TO YYYYMMDD]`."""
    search = f"decision_date:[{start} TO {end}]"
    return search_510k(client, search=search, **kw)


def search_510k_by_product_class(client: OpenFDAClient, device_class: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_510k_by_field(client, "openfda.device_class", device_class, **kw)


def search_510k_by_regulation_number(client: OpenFDAClient, reg_num: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_510k_by_field(client, "openfda.regulation_number", reg_num, **kw)


def search_510k_by_medical_specialty(client: OpenFDAClient, specialty: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_510k_by_field(client, "openfda.medical_specialty_description", specialty, **kw)


def count_510k_by_advisory_committee(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_510k_by_field(client, "advisory_committee", limit=limit, **kw)


def count_510k_by_decision_code(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_510k_by_field(client, "decision_code", limit=limit, **kw)


def count_510k_by_clearance_type(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_510k_by_field(client, "clearance_type", limit=limit, **kw)


# ============================
# Device Classification endpoint conveniences
# ============================

# Generic builders validated against the classification schema

def search_classification_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Search with `search=field:term` using the classification schema for validation."""
    return search_classification(client, search=q(field, term, endpoint=ENDPOINT_CLASSIFICATION), **kw)


def count_classification_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a classification field (returns buckets instead of documents)."""
    return search_classification(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar based on device_classification.yaml fields

def search_classification_by_product_code(client: OpenFDAClient, code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_classification_by_field(client, "product_code", code, **kw)


def search_classification_by_regulation_number(client: OpenFDAClient, reg: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_classification_by_field(client, "regulation_number", reg, **kw)


def search_classification_by_device_class(client: OpenFDAClient, device_class: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_classification_by_field(client, "device_class", device_class, **kw)


def search_classification_by_medical_specialty(client: OpenFDAClient, code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_classification_by_field(client, "medical_specialty", code, **kw)


def search_classification_by_medical_specialty_description(client: OpenFDAClient, text: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_classification_by_field(client, "medical_specialty_description", text, **kw)


def search_classification_by_implant_flag(client: OpenFDAClient, flag: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_classification_by_field(client, "implant_flag", flag, **kw)


def search_classification_by_life_sustain_flag(client: OpenFDAClient, flag: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_classification_by_field(client, "life_sustain_support_flag", flag, **kw)


def search_classification_by_gmp_exempt_flag(client: OpenFDAClient, flag: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_classification_by_field(client, "gmp_exempt_flag", flag, **kw)


def search_classification_by_submission_type_id(client: OpenFDAClient, sub_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_classification_by_field(client, "submission_type_id", sub_type, **kw)


def search_classification_by_summary_malfunction_reporting(client: OpenFDAClient, status: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_classification_by_field(client, "summary_malfunction_reporting", status, **kw)


def search_classification_by_third_party_flag(client: OpenFDAClient, flag: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_classification_by_field(client, "third_party_flag", flag, **kw)


def search_classification_by_unclassified_reason(client: OpenFDAClient, reason: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_classification_by_field(client, "unclassified_reason", reason, **kw)


def count_classification_by_device_class(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_classification_by_field(client, "device_class", limit=limit, **kw)


def count_classification_by_medical_specialty(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_classification_by_field(client, "medical_specialty", limit=limit, **kw)


def count_classification_by_submission_type_id(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_classification_by_field(client, "submission_type_id", limit=limit, **kw)


# ============================
# Device Enforcement endpoint conveniences
# ============================

# Generic builders validated against the device enforcement schema

def search_device_enforcements_by_field(
    client: OpenFDAClient,
    field: str,
    term: str,
    /,
    **kw: Any,
) -> APIResponse[Dict[str, Any]]:
    """Search with `search=field:term` using the device enforcement schema for validation."""
    return search_enforcements(client, search=q(field, term, endpoint=ENDPOINT_ENFORCEMENT), **kw)


def count_device_enforcements_by_field(
    client: OpenFDAClient,
    field: str,
    /,
    limit: int = 1000,
    **kw: Any,
) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a device enforcement field (returns buckets)."""
    return search_enforcements(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar based on device_enforcement.yaml fields

def search_device_enforcements_by_classification(client: OpenFDAClient, cls: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Recall class: "Class I", "Class II", or "Class III"."""
    return search_device_enforcements_by_field(client, "classification", cls, **kw)


def search_device_enforcements_by_recalling_firm(client: OpenFDAClient, firm: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_enforcements_by_field(client, "recalling_firm", firm, **kw)


def search_device_enforcements_by_status(client: OpenFDAClient, status: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    # Status is typically one of: On-Going, Completed, Terminated, Pending
    return search_device_enforcements_by_field(client, "status", status, **kw)


def search_device_enforcements_by_state(client: OpenFDAClient, state: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_enforcements_by_field(client, "state", state, **kw)


def search_device_enforcements_by_city(client: OpenFDAClient, city: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_enforcements_by_field(client, "city", city, **kw)


def search_device_enforcements_by_country(client: OpenFDAClient, country: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_enforcements_by_field(client, "country", country, **kw)


def search_device_enforcements_by_product_code(client: OpenFDAClient, code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_enforcements_by_field(client, "product_code", code, **kw)


def search_device_enforcements_by_product_type(client: OpenFDAClient, product_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_enforcements_by_field(client, "product_type", product_type, **kw)


def search_device_enforcements_by_reason(client: OpenFDAClient, reason: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_enforcements_by_field(client, "reason_for_recall", reason, **kw)


def search_device_enforcements_by_product_description(client: OpenFDAClient, text: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_enforcements_by_field(client, "product_description", text, **kw)


def search_device_enforcements_by_event_id(client: OpenFDAClient, event_id: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_enforcements_by_field(client, "event_id", event_id, **kw)


def search_device_enforcements_by_recall_number(client: OpenFDAClient, recall_number: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_enforcements_by_field(client, "recall_number", recall_number, **kw)


def search_device_enforcements_by_voluntary_mandated(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    # e.g., "Voluntary: Firm Initiated" vs. mandated variants per FDA
    return search_device_enforcements_by_field(client, "voluntary_mandated", value, **kw)


# Date range helpers (YYYYMMDD)

def _range_device_enf(field: str, start: str, end: str) -> str:
    return f"{field}:[{start} TO {end}]"


def search_device_enforcements_between_report_date(client: OpenFDAClient, start_yyyymmdd: str, end_yyyymmdd: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_enforcements(client, search=_range_device_enf("report_date", start_yyyymmdd, end_yyyymmdd), **kw)


def search_device_enforcements_between_recall_initiation_date(client: OpenFDAClient, start_yyyymmdd: str, end_yyyymmdd: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_enforcements(client, search=_range_device_enf("recall_initiation_date", start_yyyymmdd, end_yyyymmdd), **kw)


def search_device_enforcements_between_center_classification_date(client: OpenFDAClient, start_yyyymmdd: str, end_yyyymmdd: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_enforcements(client, search=_range_device_enf("center_classification_date", start_yyyymmdd, end_yyyymmdd), **kw)


# Facet helpers for common buckets

def count_device_enforcements_by_classification(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_device_enforcements_by_field(client, "classification", limit=limit, **kw)


def count_device_enforcements_by_status(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_device_enforcements_by_field(client, "status", limit=limit, **kw)


def count_device_enforcements_by_state(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_device_enforcements_by_field(client, "state", limit=limit, **kw)


def count_device_enforcements_by_product_code(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_device_enforcements_by_field(client, "product_code", limit=limit, **kw)


# ============================
# Device Event (MDR) endpoint conveniences
# ============================

# Generic builders validated against the device event schema

def search_device_events_by_field(
    client: OpenFDAClient,
    field: str,
    term: str,
    /,
    **kw: Any,
) -> APIResponse[Dict[str, Any]]:
    """Search with `search=field:term` using the device event schema for validation."""
    return search_events(client, search=q(field, term, endpoint=ENDPOINT_EVENT), **kw)


def count_device_events_by_field(
    client: OpenFDAClient,
    field: str,
    /,
    limit: int = 1000,
    **kw: Any,
) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a device event field (returns buckets)."""
    return search_events(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar based on device_event.yaml fields
# Schema includes adverse_event_flag, event_type, product_problem_flag, device[].*, openfda.*, dates, etc. (see YAML)

def search_device_events_by_event_type(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_events_by_field(client, "event_type", value, **kw)


def search_device_events_by_product_problem_flag(client: OpenFDAClient, flag: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_events_by_field(client, "product_problem_flag", flag, **kw)


def search_device_events_by_adverse_event_flag(client: OpenFDAClient, flag: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_events_by_field(client, "adverse_event_flag", flag, **kw)


def search_device_events_by_product_code(client: OpenFDAClient, code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_events_by_field(client, "device.device_report_product_code", code, **kw)


def search_device_events_by_device_name(client: OpenFDAClient, name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_events_by_field(client, "device.brand_name", name, **kw)


def search_device_events_by_device_generic_name(client: OpenFDAClient, name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_events_by_field(client, "device.generic_name", name, **kw)


def search_device_events_by_manufacturer_name(client: OpenFDAClient, mfr: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_events_by_field(client, "manufacturer_name", mfr, **kw)


def search_device_events_by_openfda_device_class(client: OpenFDAClient, cls: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_events_by_field(client, "device.openfda.device_class", cls, **kw)


def search_device_events_by_openfda_regulation_number(client: OpenFDAClient, reg: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_events_by_field(client, "device.openfda.regulation_number", reg, **kw)


def search_device_events_by_udi_di(client: OpenFDAClient, udi_di: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_events_by_field(client, "device.udi_di", udi_di, **kw)


# Date range helpers (YYYYMMDD as strings)

def _range_device_event(field: str, start: str, end: str) -> str:
    return f"{field}:[{start} TO {end}]"


def search_device_events_between_date_received(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_events(client, search=_range_device_event("date_received", start, end), **kw)


def search_device_events_between_date_of_event(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_events(client, search=_range_device_event("date_of_event", start, end), **kw)


def search_device_events_between_report_date(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_events(client, search=_range_device_event("report_date", start, end), **kw)


# Facet helpers for common buckets

def count_device_events_by_event_type(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_device_events_by_field(client, "event_type", limit=limit, **kw)


def count_device_events_by_product_code(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_device_events_by_field(client, "device.device_report_product_code", limit=limit, **kw)


def count_device_events_by_openfda_device_class(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_device_events_by_field(client, "device.openfda.device_class", limit=limit, **kw)
# ============================
# Device PMA endpoint conveniences
# ============================

# Generic builders validated against the PMA schema

def search_pma_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Search with `search=field:term` using the PMA schema for validation."""
    return search_pma(client, search=q(field, term, endpoint=ENDPOINT_PMA), **kw)


def count_pma_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a PMA field (returns buckets)."""
    return search_pma(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar based on device_pma.yaml fields

def search_pma_by_pma_number(client: OpenFDAClient, pma_number: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "pma_number", pma_number, **kw)


def search_pma_by_applicant(client: OpenFDAClient, applicant: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "applicant", applicant, **kw)


def search_pma_by_trade_name(client: OpenFDAClient, trade_name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "trade_name", trade_name, **kw)


def search_pma_by_generic_name(client: OpenFDAClient, generic_name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "generic_name", generic_name, **kw)


def search_pma_by_product_code(client: OpenFDAClient, product_code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "product_code", product_code, **kw)


def search_pma_by_advisory_committee(client: OpenFDAClient, advisory: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "advisory_committee", advisory, **kw)


def search_pma_by_advisory_committee_description(client: OpenFDAClient, text: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "advisory_committee_description", text, **kw)


def search_pma_by_decision_code(client: OpenFDAClient, decision_code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "decision_code", decision_code, **kw)


def search_pma_by_expedited_review_flag(client: OpenFDAClient, flag: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "expedited_review_flag", flag, **kw)


def search_pma_by_city(client: OpenFDAClient, city: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "city", city, **kw)


def search_pma_by_state(client: OpenFDAClient, state: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "state", state, **kw)


def search_pma_by_zip(client: OpenFDAClient, zip_code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "zip", zip_code, **kw)


def search_pma_by_zip_ext(client: OpenFDAClient, zip_ext: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "zip_ext", zip_ext, **kw)


def search_pma_by_openfda_device_class(client: OpenFDAClient, device_class: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "openfda.device_class", device_class, **kw)


def search_pma_by_openfda_device_name(client: OpenFDAClient, device_name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "openfda.device_name", device_name, **kw)


def search_pma_by_openfda_medical_specialty(client: OpenFDAClient, specialty: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "openfda.medical_specialty_description", specialty, **kw)


def search_pma_by_openfda_regulation_number(client: OpenFDAClient, reg: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "openfda.regulation_number", reg, **kw)


def search_pma_by_openfda_fei_number(client: OpenFDAClient, fei: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "openfda.fei_number", fei, **kw)


def search_pma_by_openfda_registration_number(client: OpenFDAClient, reg_no: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "openfda.registration_number", reg_no, **kw)


def search_pma_by_supplement_type(client: OpenFDAClient, supplement_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "supplement_type", supplement_type, **kw)


def search_pma_by_supplement_reason(client: OpenFDAClient, reason: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "supplement_reason", reason, **kw)


def search_pma_by_supplement_number(client: OpenFDAClient, supplement_number: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma_by_field(client, "supplement_number", supplement_number, **kw)


# Date range helpers (YYYYMMDD)

def _range_pma(field: str, start: str, end: str) -> str:
    return f"{field}:[{start} TO {end}]"


def search_pma_between_decision_date(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma(client, search=_range_pma("decision_date", start, end), **kw)


def search_pma_between_date_received(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma(client, search=_range_pma("date_received", start, end), **kw)


def search_pma_between_fed_reg_notice_date(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_pma(client, search=_range_pma("fed_reg_notice_date", start, end), **kw)


# Facet helpers

def count_pma_by_advisory_committee(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_pma_by_field(client, "advisory_committee", limit=limit, **kw)


def count_pma_by_decision_code(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_pma_by_field(client, "decision_code", limit=limit, **kw)


def count_pma_by_device_class(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_pma_by_field(client, "openfda.device_class", limit=limit, **kw)


# ============================
# Device Recall endpoint conveniences
# ============================

# Generic builders validated against the device recall schema

def search_device_recalls_by_field(
    client: OpenFDAClient,
    field: str,
    term: str,
    /,
    **kw: Any,
) -> APIResponse[Dict[str, Any]]:
    """Search with `search=field:term` using the device recall schema for validation."""
    return search_recalls(client, search=q(field, term, endpoint=ENDPOINT_RECALL), **kw)


def count_device_recalls_by_field(
    client: OpenFDAClient,
    field: str,
    /,
    limit: int = 1000,
    **kw: Any,
) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a device recall field (returns buckets)."""
    return search_recalls(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar based on device_recall.yaml fields

def search_device_recalls_by_status(client: OpenFDAClient, status: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "recall_status", status, **kw)


def search_device_recalls_by_recalling_firm(client: OpenFDAClient, firm: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "recalling_firm", firm, **kw)


def search_device_recalls_by_firm_fei(client: OpenFDAClient, fei: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "firm_fei_number", fei, **kw)


def search_device_recalls_by_city(client: OpenFDAClient, city: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "city", city, **kw)


def search_device_recalls_by_state(client: OpenFDAClient, state: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "state", state, **kw)


def search_device_recalls_by_country(client: OpenFDAClient, country: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "country", country, **kw)


def search_device_recalls_by_product_code(client: OpenFDAClient, code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "product_code", code, **kw)


def search_device_recalls_by_reason(client: OpenFDAClient, reason: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "reason_for_recall", reason, **kw)


def search_device_recalls_by_product_description(client: OpenFDAClient, text: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "product_description", text, **kw)


def search_device_recalls_by_product_res_number(client: OpenFDAClient, res_no: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "product_res_number", res_no, **kw)


def search_device_recalls_by_res_event_number(client: OpenFDAClient, res_event_no: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "res_event_number", res_event_no, **kw)


def search_device_recalls_by_root_cause(client: OpenFDAClient, cause: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "root_cause_description", cause, **kw)


def search_device_recalls_by_k_number(client: OpenFDAClient, k_number: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    # openFDA block also carries k_number[]; this targets top-level array
    return search_device_recalls_by_field(client, "k_numbers", k_number, **kw)


def search_device_recalls_by_pma_number(client: OpenFDAClient, pma_no: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "pma_numbers", pma_no, **kw)


def search_device_recalls_by_openfda_device_class(client: OpenFDAClient, cls: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "openfda.device_class", cls, **kw)


def search_device_recalls_by_openfda_device_name(client: OpenFDAClient, name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "openfda.device_name", name, **kw)


def search_device_recalls_by_openfda_regulation_number(client: OpenFDAClient, reg: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "openfda.regulation_number", reg, **kw)


def search_device_recalls_by_openfda_medical_specialty(client: OpenFDAClient, specialty: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "openfda.medical_specialty_description", specialty, **kw)


def search_device_recalls_by_openfda_fei_number(client: OpenFDAClient, fei: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "openfda.fei_number", fei, **kw)


def search_device_recalls_by_openfda_registration_number(client: OpenFDAClient, reg_no: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "openfda.registration_number", reg_no, **kw)


def search_device_recalls_by_distribution_pattern(client: OpenFDAClient, text: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "distribution_pattern", text, **kw)


def search_device_recalls_by_product_quantity(client: OpenFDAClient, text: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "product_quantity", text, **kw)


def search_device_recalls_by_code_info(client: OpenFDAClient, text: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "code_info", text, **kw)


def search_device_recalls_by_additional_info_contact(client: OpenFDAClient, text: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "additional_info_contact", text, **kw)


def search_device_recalls_by_other_submission_description(client: OpenFDAClient, text: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_device_recalls_by_field(client, "other_submission_description", text, **kw)


# Date range helpers (YYYYMMDD)

def _range_device_recall(field: str, start: str, end: str) -> str:
    return f"{field}:[{start} TO {end}]"


def search_device_recalls_between_event_date_initiated(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_recalls(client, search=_range_device_recall("event_date_initiated", start, end), **kw)


def search_device_recalls_between_event_date_posted(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_recalls(client, search=_range_device_recall("event_date_posted", start, end), **kw)


def search_device_recalls_between_event_date_terminated(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_recalls(client, search=_range_device_recall("event_date_terminated", start, end), **kw)


def search_device_recalls_between_event_date_created(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_recalls(client, search=_range_device_recall("event_date_created", start, end), **kw)


# Facet helpers for common buckets

def count_device_recalls_by_status(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_device_recalls_by_field(client, "recall_status", limit=limit, **kw)


def count_device_recalls_by_state(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_device_recalls_by_field(client, "state", limit=limit, **kw)


def count_device_recalls_by_product_code(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_device_recalls_by_field(client, "product_code", limit=limit, **kw)


def count_device_recalls_by_root_cause(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_device_recalls_by_field(client, "root_cause_description", limit=limit, **kw)
# ============================
# Device Registration & Listing endpoint conveniences
# ============================

# Generic builders validated against the registrationlisting schema

def search_registrationlisting_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Search with `search=field:term` using the registrationlisting schema for validation."""
    return search_registrationlisting(client, search=q(field, term, endpoint=ENDPOINT_REGISTRATIONLISTING), **kw)


def count_registrationlisting_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a registrationlisting field (returns buckets)."""
    return search_registrationlisting(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar based on device_registrationlisting.yaml fields

def search_registrationlisting_by_registration_number(client: OpenFDAClient, reg_no: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_registrationlisting_by_field(client, "registration.registration_number", reg_no, **kw)


def search_registrationlisting_by_fei_number(client: OpenFDAClient, fei: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_registrationlisting_by_field(client, "registration.fei_number", fei, **kw)


def search_registrationlisting_by_facility_name(client: OpenFDAClient, name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_registrationlisting_by_field(client, "registration.name", name, **kw)


def search_registrationlisting_by_city(client: OpenFDAClient, city: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_registrationlisting_by_field(client, "registration.city", city, **kw)


def search_registrationlisting_by_state_code(client: OpenFDAClient, state: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_registrationlisting_by_field(client, "registration.state_code", state, **kw)


def search_registrationlisting_by_country_code(client: OpenFDAClient, iso_country: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_registrationlisting_by_field(client, "registration.iso_country_code", iso_country, **kw)


def search_registrationlisting_by_owner_operator(client: OpenFDAClient, firm_name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_registrationlisting_by_field(client, "registration.owner_operator.firm_name", firm_name, **kw)


def search_registrationlisting_by_establishment_type(client: OpenFDAClient, est_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_registrationlisting_by_field(client, "establishment_type", est_type, **kw)


def search_registrationlisting_by_proprietary_name(client: OpenFDAClient, brand: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_registrationlisting_by_field(client, "proprietary_name", brand, **kw)


def search_registrationlisting_by_product_code(client: OpenFDAClient, product_code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_registrationlisting_by_field(client, "products.product_code", product_code, **kw)


def search_registrationlisting_by_openfda_device_class(client: OpenFDAClient, device_class: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_registrationlisting_by_field(client, "products.openfda.device_class", device_class, **kw)


def search_registrationlisting_by_openfda_regulation_number(client: OpenFDAClient, reg: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_registrationlisting_by_field(client, "products.openfda.regulation_number", reg, **kw)


def search_registrationlisting_by_openfda_medical_specialty(client: OpenFDAClient, specialty: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_registrationlisting_by_field(client, "products.openfda.medical_specialty_description", specialty, **kw)


def search_registrationlisting_by_k_number(client: OpenFDAClient, k_number: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_registrationlisting_by_field(client, "k_number", k_number, **kw)


def search_registrationlisting_by_pma_number(client: OpenFDAClient, pma_number: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_registrationlisting_by_field(client, "pma_number", pma_number, **kw)


def search_registrationlisting_by_products_created_date_between(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    search = f"products.created_date:[{start} TO {end}]"
    return search_registrationlisting(client, search=search, **kw)


# Facet helpers for common buckets

def count_registrationlisting_by_state_code(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_registrationlisting_by_field(client, "registration.state_code", limit=limit, **kw)


def count_registrationlisting_by_establishment_type(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_registrationlisting_by_field(client, "establishment_type", limit=limit, **kw)


def count_registrationlisting_by_product_code(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_registrationlisting_by_field(client, "products.product_code", limit=limit, **kw)


def count_registrationlisting_by_device_class(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_registrationlisting_by_field(client, "products.openfda.device_class", limit=limit, **kw)
#
# ============================
# Device COVID-19 Serology endpoint conveniences
# ============================

# Generic builders validated against the covid19serology schema

def search_covid19serology_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Search with `search=field:term` using the covid19serology schema for validation."""
    return search_covid19serology(client, search=q(field, term, endpoint=ENDPOINT_COVID19SEROLOGY), **kw)


def count_covid19serology_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a covid19serology field (returns buckets)."""
    return search_covid19serology(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar based on device_covid19serology.yaml fields

def search_covid19serology_by_manufacturer(client: OpenFDAClient, manufacturer: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "manufacturer", manufacturer, **kw)


def search_covid19serology_by_device_name(client: OpenFDAClient, device: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "device", device, **kw)


def search_covid19serology_by_panel(client: OpenFDAClient, panel: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "panel", panel, **kw)


def search_covid19serology_by_sample_id(client: OpenFDAClient, sample_id: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "sample_id", sample_id, **kw)


def search_covid19serology_by_group(client: OpenFDAClient, group: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "group", group, **kw)


def search_covid19serology_by_result_igm(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "igm_result", value, **kw)


def search_covid19serology_by_result_igg(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "igg_result", value, **kw)


def search_covid19serology_by_result_iga(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "iga_result", value, **kw)


def search_covid19serology_by_result_pan(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "pan_result", value, **kw)


def search_covid19serology_by_result_igm_igg(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "igm_igg_result", value, **kw)


def search_covid19serology_by_result_igm_iga(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "igm_iga_result", value, **kw)


def search_covid19serology_by_control(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "control", value, **kw)


def search_covid19serology_by_igm_truth(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "igm_truth", value, **kw)


def search_covid19serology_by_igg_truth(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "igg_truth", value, **kw)


def search_covid19serology_by_antibody_truth(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "antibody_truth", value, **kw)


def search_covid19serology_by_igm_agree(client: OpenFDAClient, code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "igm_agree", code, **kw)


def search_covid19serology_by_igg_agree(client: OpenFDAClient, code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "igg_agree", code, **kw)


def search_covid19serology_by_iga_agree(client: OpenFDAClient, code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "iga_agree", code, **kw)


def search_covid19serology_by_pan_agree(client: OpenFDAClient, code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "pan_agree", code, **kw)


def search_covid19serology_by_igm_igg_agree(client: OpenFDAClient, code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "igm_igg_agree", code, **kw)


def search_covid19serology_by_igm_iga_agree(client: OpenFDAClient, code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "igm_iga_agree", code, **kw)


def search_covid19serology_by_antibody_agree(client: OpenFDAClient, code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "antibody_agree", code, **kw)


def search_covid19serology_by_days_from_symptom(client: OpenFDAClient, text: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "days_from_symptom", text, **kw)


def search_covid19serology_by_type(client: OpenFDAClient, sample_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "type", sample_type, **kw)


def search_covid19serology_by_lot_number(client: OpenFDAClient, lot: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "lot_number", lot, **kw)


def search_covid19serology_by_evaluation_id(client: OpenFDAClient, eval_id: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "evaluation_id", eval_id, **kw)


def search_covid19serology_by_sample_no(client: OpenFDAClient, n: int | str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "sample_no", str(n), **kw)


def search_covid19serology_by_titer_igm(client: OpenFDAClient, value: int | str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "igm_titer", str(value), **kw)


def search_covid19serology_by_titer_igg(client: OpenFDAClient, value: int | str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "igg_titer", str(value), **kw)


def search_covid19serology_by_titer_pan(client: OpenFDAClient, value: int | str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology_by_field(client, "pan_titer", str(value), **kw)


# Date range helpers (YYYYMMDD)

def _range_covid_serology(field: str, start: str, end: str) -> str:
    return f"{field}:[{start} TO {end}]"


def search_covid19serology_between_date_performed(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_covid19serology(client, search=_range_covid_serology("date_performed", start, end), **kw)


# Facet helpers for common buckets

def count_covid19serology_by_manufacturer(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_covid19serology_by_field(client, "manufacturer", limit=limit, **kw)


def count_covid19serology_by_device_name(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_covid19serology_by_field(client, "device", limit=limit, **kw)


def count_covid19serology_by_group(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_covid19serology_by_field(client, "group", limit=limit, **kw)


def count_covid19serology_by_igm_agree(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_covid19serology_by_field(client, "igm_agree", limit=limit, **kw)


def count_covid19serology_by_igg_agree(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_covid19serology_by_field(client, "igg_agree", limit=limit, **kw)


def count_covid19serology_by_antibody_agree(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_covid19serology_by_field(client, "antibody_agree", limit=limit, **kw)
# ============================
# Device UDI (GUDID) endpoint conveniences
# ============================

# Generic builders validated against the UDI schema

def search_udi_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Search with `search=field:term` using the UDI schema for validation."""
    return search_udi(client, search=q(field, term, endpoint=ENDPOINT_UDI), **kw)


def count_udi_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a UDI field (returns buckets)."""
    return search_udi(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar based on device_udi.yaml fields

def search_udi_by_brand_name(client: OpenFDAClient, brand: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "brand_name", brand, **kw)


def search_udi_by_catalog_number(client: OpenFDAClient, catalog: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "catalog_number", catalog, **kw)


def search_udi_by_company_name(client: OpenFDAClient, company: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "company_name", company, **kw)


def search_udi_by_labeler_duns_number(client: OpenFDAClient, duns: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "labeler_duns_number", duns, **kw)


def search_udi_by_version_or_model_number(client: OpenFDAClient, model: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "version_or_model_number", model, **kw)


def search_udi_by_identifier_id(client: OpenFDAClient, identifier: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "identifiers.id", identifier, **kw)


def search_udi_by_identifier_issuing_agency(client: OpenFDAClient, agency: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "identifiers.issuing_agency", agency, **kw)


def search_udi_by_product_code(client: OpenFDAClient, code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "product_codes.code", code, **kw)


def search_udi_by_openfda_device_class(client: OpenFDAClient, device_class: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "product_codes.openfda.device_class", device_class, **kw)


def search_udi_by_openfda_regulation_number(client: OpenFDAClient, reg: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "product_codes.openfda.regulation_number", reg, **kw)


def search_udi_by_openfda_medical_specialty(client: OpenFDAClient, specialty: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "product_codes.openfda.medical_specialty_description", specialty, **kw)


def search_udi_by_openfda_device_name(client: OpenFDAClient, name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "product_codes.openfda.device_name", name, **kw)


def search_udi_by_premarket_submission_number(client: OpenFDAClient, sub_no: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "premarket_submissions.submission_number", sub_no, **kw)


def search_udi_by_premarket_submission_type(client: OpenFDAClient, sub_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "premarket_submissions.submission_type", sub_type, **kw)


def search_udi_by_mri_safety(client: OpenFDAClient, mri: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "mri_safety", mri, **kw)


def search_udi_by_sterilization_method(client: OpenFDAClient, method: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "sterilization.sterilization_methods", method, **kw)


def search_udi_by_storage_type(client: OpenFDAClient, storage_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "storage.type", storage_type, **kw)


def search_udi_by_flags_rx(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "is_rx", value, **kw)


def search_udi_by_flags_otc(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "is_otc", value, **kw)


def search_udi_by_flags_single_use(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "is_single_use", value, **kw)


def search_udi_by_flags_pm_exempt(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "is_pm_exempt", value, **kw)


def search_udi_by_flags_kit(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "is_kit", value, **kw)


def search_udi_by_flags_combination_product(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "is_combination_product", value, **kw)


def search_udi_by_has_serial_number(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "has_serial_number", value, **kw)


def search_udi_by_has_lot_or_batch_number(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "has_lot_or_batch_number", value, **kw)


def search_udi_by_has_expiration_date(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "has_expiration_date", value, **kw)


def search_udi_by_has_manufacturing_date(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "has_manufacturing_date", value, **kw)


def search_udi_by_has_donation_id_number(client: OpenFDAClient, value: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "has_donation_id_number", value, **kw)


def search_udi_by_commercial_distribution_status(client: OpenFDAClient, status: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi_by_field(client, "commercial_distribution_status", status, **kw)


# Date range helpers (YYYYMMDD)

def _range_udi(field: str, start: str, end: str) -> str:
    return f"{field}:[{start} TO {end}]"


def search_udi_between_publish_date(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi(client, search=_range_udi("publish_date", start, end), **kw)


def search_udi_between_public_version_date(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi(client, search=_range_udi("public_version_date", start, end), **kw)


def search_udi_between_commercial_distribution_end_date(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_udi(client, search=_range_udi("commercial_distribution_end_date", start, end), **kw)


# Facet helpers for common buckets

def count_udi_by_device_class(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_udi_by_field(client, "product_codes.openfda.device_class", limit=limit, **kw)


def count_udi_by_product_code(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_udi_by_field(client, "product_codes.code", limit=limit, **kw)


def count_udi_by_issuing_agency(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_udi_by_field(client, "identifiers.issuing_agency", limit=limit, **kw)


def count_udi_by_mri_safety(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_udi_by_field(client, "mri_safety", limit=limit, **kw)


def count_udi_by_commercial_status(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_udi_by_field(client, "commercial_distribution_status", limit=limit, **kw)