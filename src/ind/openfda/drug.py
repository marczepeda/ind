from __future__ import annotations
from typing import Any, Dict, Mapping, Optional, Sequence

from .client import OpenFDAClient
from .types import APIResponse, Meta, MetaResults
from .utils import build_params, paginate
from .query import q

BASE = "/drug"
ENDPOINT_EVENT = "drug/event"
ENDPOINT_LABEL = "drug/label"
ENDPOINT_NDC = "drug/ndc"
ENDPOINT_ENFORCEMENT = "drug/enforcement"
ENDPOINT_DRUGSFDA = "drug/drugsfda"
ENDPOINT_SHORTAGES = "drug/shortages"

# ---- Response helpers

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


# ---- Standard search endpoints

# /drug/event.json

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


# /drug/label.json

def search_labels(
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
    data = client.request_json("GET", f"{BASE}/label.json", params=params)
    return _wrap(data)


# /drug/enforcement.json

def search_enforcements(
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
    data = client.request_json("GET", f"{BASE}/enforcement.json", params=params)
    return _wrap(data)


# /drug/ndc.json

def search_ndc(
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
    data = client.request_json("GET", f"{BASE}/ndc.json", params=params)
    return _wrap(data)



# /drug/drugsfda.json

def search_drugsfda(
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
    data = client.request_json("GET", f"{BASE}/drugsfda.json", params=params)
    return _wrap(data)

# /drug/shortages.json

def search_shortages(
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
    data = client.request_json("GET", f"{BASE}/shortages.json", params=params)
    return _wrap(data)


# Convenience: iterate all results

def iter_events(
    client: OpenFDAClient,
    *,
    search: Optional[str] = None,
    limit: int = 100,
    max_records: Optional[int] = None,
    sort: Optional[str] = None,
):
    yield from paginate(client, f"{BASE}/event.json", search=search, limit=limit, max_records=max_records, sort=sort)

def search_events_by_reaction(client, reaction_pt: str, **kw):
    ENDPOINT_EVENT = "drug/event"
    return search_events(
        client,
        search=q("reaction.reactionmeddrapt", reaction_pt, endpoint=ENDPOINT_EVENT),
        **kw
    )

def count_events_by_reaction(client, limit=1000):
    # facets: returns buckets instead of documents
    return search_events(client, count="reaction.reactionmeddrapt.exact", limit=limit)


# ----------------------------
# Additional convenience helpers for common fields
# (field names sourced from drug_event.yaml)
# ----------------------------

# Generic builder stays validated via `q(..., endpoint=ENDPOINT_EVENT)`

def search_events_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Search with `search=field:term` using the event schema for validation."""
    return search_events(client, search=q(field, term, endpoint=ENDPOINT_EVENT), **kw)


def count_events_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a field (returns buckets instead of documents)."""
    return search_events(client, count=f"{field}.exact", limit=limit, **kw)


# --- Targeted sugar based on common queries (see drug_event.yaml) ---

def search_events_by_medicinal_product(client: OpenFDAClient, product: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """`medicinalproduct` — trade or generic product name (not strictly normalized)."""
    return search_events_by_field(client, "patient.drug.medicinalproduct", product, **kw)


def search_events_by_brand_name(client: OpenFDAClient, brand: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """`openfda.brand_name` — normalized brand names array in the openFDA block."""
    return search_events_by_field(client, "patient.drug.openfda.brand_name", brand, **kw)


def search_events_by_generic_name(client: OpenFDAClient, generic: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """`openfda.generic_name` — normalized generic names array in the openFDA block."""
    return search_events_by_field(client, "patient.drug.openfda.generic_name", generic, **kw)


def search_events_by_manufacturer(client: OpenFDAClient, manufacturer: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """`openfda.manufacturer_name` — labeler/manufacturer name."""
    return search_events_by_field(client, "patient.drug.openfda.manufacturer_name", manufacturer, **kw)


def search_events_by_product_ndc(client: OpenFDAClient, product_ndc: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """`openfda.product_ndc` — labeler+product code (e.g., 12345-678)."""
    return search_events_by_field(client, "patient.drug.openfda.product_ndc", product_ndc, **kw)


def search_events_by_package_ndc(client: OpenFDAClient, package_ndc: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """`openfda.package_ndc` — full NDC including package segment (e.g., 12345-6789-01)."""
    return search_events_by_field(client, "patient.drug.openfda.package_ndc", package_ndc, **kw)


def search_events_by_application_number(client: OpenFDAClient, app_no: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """`openfda.application_number` — NDA/ANDA/BLA or CFR citation."""
    return search_events_by_field(client, "patient.drug.openfda.application_number", app_no, **kw)


def search_events_by_unii(client: OpenFDAClient, unii: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """`openfda.unii` — 10-character Unique Ingredient Identifier."""
    return search_events_by_field(client, "patient.drug.openfda.unii", unii, **kw)


def search_events_by_rxcui(client: OpenFDAClient, rxcui: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """`openfda.rxcui` — 6-digit RxNorm concept identifier."""
    return search_events_by_field(client, "patient.drug.openfda.rxcui", rxcui, **kw)


def count_events_by_medicinal_product(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_events_by_field(client, "patient.drug.medicinalproduct", limit=limit, **kw)


def count_events_by_brand_name(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_events_by_field(client, "patient.drug.openfda.brand_name", limit=limit, **kw)


def count_events_by_generic_name(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_events_by_field(client, "patient.drug.openfda.generic_name", limit=limit, **kw)


def count_events_by_reaction(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_events_by_field(client, "reaction.reactionmeddrapt", limit=limit, **kw)


# --- Demographics & metadata filters ---

def search_events_by_patient_sex(client: OpenFDAClient, sex: str | int, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Filter by `patient.patientsex` (codes: 0 Unknown, 1 Male, 2 Female)."""
    code_map = {"unknown": "0", "male": "1", "female": "2"}
    val = str(sex).lower()
    term = code_map.get(val, str(sex))
    return search_events_by_field(client, "patient.patientsex", term, **kw)


def search_events_by_seriousness(client: OpenFDAClient, serious: str | int, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Filter by `serious` (1 serious, 2 not serious)."""
    code_map = {"serious": "1", "not_serious": "2", "not-serious": "2", "nonserious": "2"}
    val = str(serious).lower()
    term = code_map.get(val, str(serious))
    return search_events_by_field(client, "serious", term, **kw)


# --- Date range helpers ---

def _range(field: str, start: str, end: str) -> str:
    """Build an OpenFDA range expression [YYYYMMDD TO YYYYMMDD]."""
    return f"{field}:[{start} TO {end}]"


def search_events_between_receivedate(client: OpenFDAClient, start_yyyymmdd: str, end_yyyymmdd: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Filter by first received date `[start TO end]` using `receivedate`.

    Dates should be in `YYYYMMDD` per the API (e.g., '20240101').
    """
    return search_events(client, search=_range("receivedate", start_yyyymmdd, end_yyyymmdd), **kw)


def search_events_between_receiptdate(client: OpenFDAClient, start_yyyymmdd: str, end_yyyymmdd: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Filter by last-updated receipt date `[start TO end]` using `receiptdate`."""
    return search_events(client, search=_range("receiptdate", start_yyyymmdd, end_yyyymmdd), **kw)


# ============================
# Label endpoint conveniences
# ============================

# Generic builders validated against the label schema

def search_labels_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Search with `search=field:term` using the label schema for validation."""
    return search_labels(client, search=q(field, term, endpoint=ENDPOINT_LABEL), **kw)


def count_labels_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a label field (returns buckets instead of documents)."""
    return search_labels(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar for common openFDA fields in the label dataset
# (field names from drug_label.yaml)

def search_labels_by_brand_name(client: OpenFDAClient, brand: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_labels_by_field(client, "openfda.brand_name", brand, **kw)


def search_labels_by_generic_name(client: OpenFDAClient, generic: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_labels_by_field(client, "openfda.generic_name", generic, **kw)


def search_labels_by_manufacturer(client: OpenFDAClient, manufacturer: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_labels_by_field(client, "openfda.manufacturer_name", manufacturer, **kw)


def search_labels_by_product_ndc(client: OpenFDAClient, product_ndc: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_labels_by_field(client, "openfda.product_ndc", product_ndc, **kw)


def search_labels_by_package_ndc(client: OpenFDAClient, package_ndc: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_labels_by_field(client, "openfda.package_ndc", package_ndc, **kw)


def search_labels_by_application_number(client: OpenFDAClient, app_no: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_labels_by_field(client, "openfda.application_number", app_no, **kw)


def search_labels_by_route(client: OpenFDAClient, route: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_labels_by_field(client, "openfda.route", route, **kw)


def search_labels_by_product_type(client: OpenFDAClient, product_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_labels_by_field(client, "openfda.product_type", product_type, **kw)


def search_labels_by_rxcui(client: OpenFDAClient, rxcui: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_labels_by_field(client, "openfda.rxcui", rxcui, **kw)


def search_labels_by_spl_id(client: OpenFDAClient, spl_id: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_labels_by_field(client, "openfda.spl_id", spl_id, **kw)


def search_labels_by_spl_set_id(client: OpenFDAClient, spl_set_id: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_labels_by_field(client, "openfda.spl_set_id", spl_set_id, **kw)


def search_labels_by_substance_name(client: OpenFDAClient, substance: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_labels_by_field(client, "openfda.substance_name", substance, **kw)


def search_labels_by_unii(client: OpenFDAClient, unii: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_labels_by_field(client, "openfda.unii", unii, **kw)


# Facet helpers for common fields

def count_labels_by_brand_name(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_labels_by_field(client, "openfda.brand_name", limit=limit, **kw)


def count_labels_by_generic_name(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_labels_by_field(client, "openfda.generic_name", limit=limit, **kw)


def count_labels_by_manufacturer(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_labels_by_field(client, "openfda.manufacturer_name", limit=limit, **kw)


def count_labels_by_route(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_labels_by_field(client, "openfda.route", limit=limit, **kw)

# ============================
# NDC endpoint conveniences
# ============================

# Generic builders validated against the NDC schema

def search_ndc_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Search with `search=field:term` using the NDC schema for validation."""
    return search_ndc(client, search=q(field, term, endpoint=ENDPOINT_NDC), **kw)


def count_ndc_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Facet counts for an NDC field (returns buckets instead of documents)."""
    return search_ndc(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar for common NDC fields (see drug_ndc.yaml)

def search_ndc_by_product_ndc(client: OpenFDAClient, product_ndc: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_ndc_by_field(client, "product_ndc", product_ndc, **kw)


def search_ndc_by_package_ndc(client: OpenFDAClient, package_ndc: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_ndc_by_field(client, "packaging.package_ndc", package_ndc, **kw)


def search_ndc_by_brand_name(client: OpenFDAClient, brand: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_ndc_by_field(client, "brand_name", brand, **kw)


def search_ndc_by_brand_name_base(client: OpenFDAClient, brand_base: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_ndc_by_field(client, "brand_name_base", brand_base, **kw)


def search_ndc_by_generic_name(client: OpenFDAClient, generic: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_ndc_by_field(client, "generic_name", generic, **kw)


def search_ndc_by_dosage_form(client: OpenFDAClient, dosage_form: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_ndc_by_field(client, "dosage_form", dosage_form, **kw)


def search_ndc_by_route(client: OpenFDAClient, route: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_ndc_by_field(client, "route", route, **kw)


def search_ndc_by_product_type(client: OpenFDAClient, product_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_ndc_by_field(client, "product_type", product_type, **kw)


def search_ndc_by_application_number(client: OpenFDAClient, app_no: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_ndc_by_field(client, "application_number", app_no, **kw)


def search_ndc_by_manufacturer(client: OpenFDAClient, manufacturer: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_ndc_by_field(client, "openfda.manufacturer_name", manufacturer, **kw)


def search_ndc_by_unii(client: OpenFDAClient, unii: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_ndc_by_field(client, "openfda.unii", unii, **kw)


def search_ndc_by_rxcui(client: OpenFDAClient, rxcui: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_ndc_by_field(client, "openfda.rxcui", rxcui, **kw)


def search_ndc_by_spl_set_id(client: OpenFDAClient, spl_set_id: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_ndc_by_field(client, "openfda.spl_set_id", spl_set_id, **kw)


def search_ndc_by_spl_id(client: OpenFDAClient, spl_id: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_ndc_by_field(client, "spl_id", spl_id, **kw)


def search_ndc_by_dea_schedule(client: OpenFDAClient, schedule: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_ndc_by_field(client, "dea_schedule", schedule, **kw)


def search_ndc_by_active_ingredient(client: OpenFDAClient, name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_ndc_by_field(client, "active_ingredients.name", name, **kw)


def search_ndc_by_active_strength(client: OpenFDAClient, strength: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_ndc_by_field(client, "active_ingredients.strength", strength, **kw)


def search_ndc_by_upc(client: OpenFDAClient, upc: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_ndc_by_field(client, "openfda.upc", upc, **kw)


# Facet helpers for common NDC fields

def count_ndc_by_product_ndc(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_ndc_by_field(client, "product_ndc", limit=limit, **kw)


def count_ndc_by_brand_name(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_ndc_by_field(client, "brand_name", limit=limit, **kw)


def count_ndc_by_generic_name(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_ndc_by_field(client, "generic_name", limit=limit, **kw)


def count_ndc_by_route(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_ndc_by_field(client, "route", limit=limit, **kw)


def count_ndc_by_product_type(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_ndc_by_field(client, "product_type", limit=limit, **kw)


def count_ndc_by_manufacturer(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_ndc_by_field(client, "openfda.manufacturer_name", limit=limit, **kw)


# ============================
# Enforcement endpoint conveniences
# ============================

# NOTE: These helpers are schema-agnostic for now. Once you add
# `drug_enforcement.yaml`, swap to `q(field, term, endpoint=ENDPOINT_ENFORCEMENT)`
# for validation, mirroring the label/NDC helpers.


def _quote_term_enf(term: str) -> str:
    needs_quotes = any(c.isspace() or c in ':/()' for c in term)
    safe = term.replace('"', r'\"')
    return f'"{safe}"' if needs_quotes else safe


def search_enforcements_by_field(
    client: OpenFDAClient,
    field: str,
    term: str,
    /,
    **kw: Any,
) -> APIResponse[Dict[str, Any]]:
    """Builds `search=field:term` and queries the enforcement endpoint."""
    search = f"{field}:{_quote_term_enf(term)}"
    return search_enforcements(client, search=search, **kw)


def count_enforcements_by_field(
    client: OpenFDAClient,
    field: str,
    /,
    limit: int = 1000,
    **kw: Any,
) -> APIResponse[Dict[str, Any]]:
    """Facet counts for an enforcement field (returns buckets)."""
    return search_enforcements(client, count=f"{field}.exact", limit=limit, **kw)


# Common targeted sugar (based on openFDA enforcement fields)

def search_enforcements_by_classification(client: OpenFDAClient, classification: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Filter by recall class (I, II, III)."""
    return search_enforcements_by_field(client, "classification", classification, **kw)


def search_enforcements_by_recalling_firm(client: OpenFDAClient, firm: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_enforcements_by_field(client, "recalling_firm", firm, **kw)


def search_enforcements_by_status(client: OpenFDAClient, status: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_enforcements_by_field(client, "status", status, **kw)


def search_enforcements_by_state(client: OpenFDAClient, state: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_enforcements_by_field(client, "state", state, **kw)


# Date range helpers

def _date_range_enf(field: str, start: str, end: str) -> str:
    return f"{field}:[{start} TO {end}]"


def search_enforcements_between_report_date(
    client: OpenFDAClient,
    start_yyyymmdd: str,
    end_yyyymmdd: str,
    /,
    **kw: Any,
) -> APIResponse[Dict[str, Any]]:
    """Filter by report_date range `[YYYYMMDD TO YYYYMMDD]`."""
    return search_enforcements(client, search=_date_range_enf("report_date", start_yyyymmdd, end_yyyymmdd), **kw)


# ============================
# Drugs@FDA endpoint conveniences
# ============================

# Generic builders validated against the Drugs@FDA schema

def search_drugsfda_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Search with `search=field:term` using the drugsfda schema for validation.
    Common searchable fields include `application_number`, `openfda.*`, `products.*`, `sponsor_name`, and `submissions.*` (see drug_drugsfda.yaml)."""
    return search_drugsfda(client, search=q(field, term, endpoint=ENDPOINT_DRUGSFDA), **kw)


def count_drugsfda_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a drugsfda field (returns buckets instead of documents)."""
    return search_drugsfda(client, count=f"{field}.exact", limit=limit, **kw)


# --- Targeted sugar from drug_drugsfda.yaml ---

def search_drugsfda_by_application_number(client: OpenFDAClient, app_no: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Match by primary `application_number` (e.g., NDA/ANDA/BLA)."""
    return search_drugsfda_by_field(client, "application_number", app_no, **kw)


def search_drugsfda_by_openfda_application_number(client: OpenFDAClient, app_no: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "openfda.application_number", app_no, **kw)


def search_drugsfda_by_brand_name(client: OpenFDAClient, brand: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "openfda.brand_name", brand, **kw)


def search_drugsfda_by_generic_name(client: OpenFDAClient, generic: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "openfda.generic_name", generic, **kw)


def search_drugsfda_by_manufacturer(client: OpenFDAClient, manufacturer: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "openfda.manufacturer_name", manufacturer, **kw)


def search_drugsfda_by_unii(client: OpenFDAClient, unii: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "openfda.unii", unii, **kw)


def search_drugsfda_by_rxcui(client: OpenFDAClient, rxcui: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "openfda.rxcui", rxcui, **kw)


def search_drugsfda_by_product_ndc(client: OpenFDAClient, product_ndc: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "openfda.product_ndc", product_ndc, **kw)


def search_drugsfda_by_package_ndc(client: OpenFDAClient, package_ndc: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "openfda.package_ndc", package_ndc, **kw)


def search_drugsfda_by_route(client: OpenFDAClient, route: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "openfda.route", route, **kw)


def search_drugsfda_by_substance_name(client: OpenFDAClient, substance: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "openfda.substance_name", substance, **kw)


def search_drugsfda_by_nui(client: OpenFDAClient, nui: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "openfda.nui", nui, **kw)


def search_drugsfda_by_spl_id(client: OpenFDAClient, spl_id: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "openfda.spl_id", spl_id, **kw)


def search_drugsfda_by_spl_set_id(client: OpenFDAClient, spl_set_id: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "openfda.spl_set_id", spl_set_id, **kw)


def search_drugsfda_by_products_brand_name(client: OpenFDAClient, brand: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "products.brand_name", brand, **kw)


def search_drugsfda_by_products_route(client: OpenFDAClient, route: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "products.route", route, **kw)


def search_drugsfda_by_active_ingredient(client: OpenFDAClient, name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "products.active_ingredients.name", name, **kw)


def search_drugsfda_by_active_strength(client: OpenFDAClient, strength: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "products.active_ingredients.strength", strength, **kw)


def search_drugsfda_by_marketing_status(client: OpenFDAClient, status: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "products.marketing_status", status, **kw)


def search_drugsfda_by_product_number(client: OpenFDAClient, product_number: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "products.product_number", product_number, **kw)


def search_drugsfda_by_te_code(client: OpenFDAClient, te_code: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "products.te_code", te_code, **kw)


def search_drugsfda_by_sponsor_name(client: OpenFDAClient, sponsor: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "sponsor_name", sponsor, **kw)


def search_drugsfda_by_submission_type(client: OpenFDAClient, submission_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "submissions.submission_type", submission_type, **kw)


def search_drugsfda_by_submission_status(client: OpenFDAClient, submission_status: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "submissions.submission_status", submission_status, **kw)


def search_drugsfda_by_submission_number(client: OpenFDAClient, submission_number: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_drugsfda_by_field(client, "submissions.submission_number", submission_number, **kw)


# Facet helpers for common buckets

def count_drugsfda_by_brand_name(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_drugsfda_by_field(client, "openfda.brand_name", limit=limit, **kw)


def count_drugsfda_by_generic_name(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_drugsfda_by_field(client, "openfda.generic_name", limit=limit, **kw)


def count_drugsfda_by_manufacturer(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_drugsfda_by_field(client, "openfda.manufacturer_name", limit=limit, **kw)


def count_drugsfda_by_route(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_drugsfda_by_field(client, "openfda.route", limit=limit, **kw)
# ============================
# Drug Shortages endpoint conveniences
# ============================

# Generic builders validated against the shortages schema

def search_shortages_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Search with `search=field:term` using the shortages schema for validation."""
    return search_shortages(client, search=q(field, term, endpoint=ENDPOINT_SHORTAGES), **kw)


def count_shortages_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a shortages field (returns buckets instead of documents)."""
    return search_shortages(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar (field names from drug_shortage.yaml)

def search_shortages_by_package_ndc(client: OpenFDAClient, package_ndc: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_shortages_by_field(client, "package_ndc", package_ndc, **kw)


def search_shortages_by_product_ndc(client: OpenFDAClient, product_ndc: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    # openFDA nested product NDC
    return search_shortages_by_field(client, "openfda.product_ndc", product_ndc, **kw)


def search_shortages_by_brand_name(client: OpenFDAClient, brand: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    # supports both top-level proprietary_name and openFDA brand_name
    try:
        return search_shortages_by_field(client, "proprietary_name", brand, **kw)
    except Exception:
        return search_shortages_by_field(client, "openfda.brand_name", brand, **kw)


def search_shortages_by_generic_name(client: OpenFDAClient, generic: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    # supports both top-level generic_name and openFDA generic_name
    try:
        return search_shortages_by_field(client, "generic_name", generic, **kw)
    except Exception:
        return search_shortages_by_field(client, "openfda.generic_name", generic, **kw)


def search_shortages_by_company(client: OpenFDAClient, company: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_shortages_by_field(client, "company_name", company, **kw)


def search_shortages_by_dosage_form(client: OpenFDAClient, dosage_form: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    # top-level dosage_form and openFDA.dosage_form
    try:
        return search_shortages_by_field(client, "dosage_form", dosage_form, **kw)
    except Exception:
        return search_shortages_by_field(client, "openfda.dosage_form", dosage_form, **kw)


def search_shortages_by_route(client: OpenFDAClient, route: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_shortages_by_field(client, "openfda.route", route, **kw)


def search_shortages_by_unii(client: OpenFDAClient, unii: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_shortages_by_field(client, "openfda.unii", unii, **kw)


def search_shortages_by_rxcui(client: OpenFDAClient, rxcui: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_shortages_by_field(client, "openfda.rxcui", rxcui, **kw)


def search_shortages_by_upc(client: OpenFDAClient, upc: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_shortages_by_field(client, "openfda.upc", upc, **kw)


def search_shortages_by_status(client: OpenFDAClient, status: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_shortages_by_field(client, "status", status, **kw)


def search_shortages_by_reason(client: OpenFDAClient, reason: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_shortages_by_field(client, "shortage_reason", reason, **kw)


def search_shortages_by_therapeutic_category(client: OpenFDAClient, category: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_shortages_by_field(client, "therapeutic_category", category, **kw)


# Date range helpers for shortages

def _range_shortages(field: str, start: str, end: str) -> str:
    return f"{field}:[{start} TO {end}]"


def search_shortages_between_update_date(client: OpenFDAClient, start_yyyymmdd: str, end_yyyymmdd: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_shortages(client, search=_range_shortages("update_date", start_yyyymmdd, end_yyyymmdd), **kw)


def search_shortages_between_change_date(client: OpenFDAClient, start_yyyymmdd: str, end_yyyymmdd: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_shortages(client, search=_range_shortages("change_date", start_yyyymmdd, end_yyyymmdd), **kw)


def search_shortages_between_initial_posting_date(client: OpenFDAClient, start_yyyymmdd: str, end_yyyymmdd: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_shortages(client, search=_range_shortages("initial_posting_date", start_yyyymmdd, end_yyyymmdd), **kw)


# Facet helpers for common buckets

def count_shortages_by_brand_name(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_shortages_by_field(client, "openfda.brand_name", limit=limit, **kw)


def count_shortages_by_generic_name(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_shortages_by_field(client, "openfda.generic_name", limit=limit, **kw)


def count_shortages_by_company(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_shortages_by_field(client, "company_name", limit=limit, **kw)


def count_shortages_by_status(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_shortages_by_field(client, "status", limit=limit, **kw)