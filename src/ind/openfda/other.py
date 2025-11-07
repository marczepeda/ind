from __future__ import annotations
"""
OpenFDA – Other endpoints

Base:
    https://api.fda.gov/other/

This module implements the Historical Documents dataset:
    https://api.fda.gov/other/historicaldocument.json

It mirrors the structure used across the other ind.openfda modules:
- typed APIResponse wrapper
- endpoint wrapper (search)
- schema-validated convenience helpers using `q()`
- focused count/range helpers
"""

from typing import Any, Dict, Mapping, Optional

from .client import OpenFDAClient
from .types import APIResponse, Meta, MetaResults
from .utils import build_params
from .query import q

BASE = "/other"
ENDPOINT_HISTORICALDOCUMENT = "other/historicaldocument"
ENDPOINT_NSDE = "other/nsde"
ENDPOINT_SUBSTANCE = "other/substance"
ENDPOINT_UNII = "other/unii"


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
# /other/nsde.json
# ----------------------------

def search_nsde(
    client: OpenFDAClient,
    *,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    sort: Optional[str] = None,
    count: Optional[str] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> APIResponse[Dict[str, Any]]:
    """Search across FDA NSDE (National Drug Code Directory) records."""
    params = build_params(search=search, limit=limit, skip=skip, sort=sort, count=count, extra=extra)
    data = client.request_json("GET", f"{BASE}/nsde.json", params=params)
    return _wrap(data)


# ----------------------------
# /other/substance.json
# ----------------------------

def search_substance(
    client: OpenFDAClient,
    *,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    sort: Optional[str] = None,
    count: Optional[str] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> APIResponse[Dict[str, Any]]:
    """Search across FDA Substance Registration System (GSRS) records."""
    params = build_params(search=search, limit=limit, skip=skip, sort=sort, count=count, extra=extra)
    data = client.request_json("GET", f"{BASE}/substance.json", params=params)
    return _wrap(data)


# ----------------------------
# /other/unii.json
# ----------------------------

def search_unii(
    client: OpenFDAClient,
    *,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    sort: Optional[str] = None,
    count: Optional[str] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> APIResponse[Dict[str, Any]]:
    """Search across FDA Unique Ingredient Identifier (UNII) records."""
    params = build_params(search=search, limit=limit, skip=skip, sort=sort, count=count, extra=extra)
    data = client.request_json("GET", f"{BASE}/unii.json", params=params)
    return _wrap(data)


# ----------------------------
# /other/historicaldocument.json
# ----------------------------

def search_historicaldocument(
    client: OpenFDAClient,
    *,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    sort: Optional[str] = None,
    count: Optional[str] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> APIResponse[Dict[str, Any]]:
    """Search across FDA historical documents (press releases, etc.)."""
    params = build_params(search=search, limit=limit, skip=skip, sort=sort, count=count, extra=extra)
    data = client.request_json("GET", f"{BASE}/historicaldocument.json", params=params)
    return _wrap(data)


# ============================
# Convenience helpers (schema-validated via other_historicaldocument.yaml)
# ============================

# Generic builder / facet

def search_historicaldocument_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Build `search=field:term` validated against the endpoint schema."""
    return search_historicaldocument(client, search=q(field, term, endpoint=ENDPOINT_HISTORICALDOCUMENT), **kw)


def count_historicaldocument_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a field (returns buckets instead of documents)."""
    return search_historicaldocument(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar based on other_historicaldocument.yaml

def search_historicaldocument_by_doc_type(client: OpenFDAClient, doc_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Filter by document type (e.g., 'pr' for Press Release)."""
    return search_historicaldocument_by_field(client, "doc_type", doc_type, **kw)


def search_historicaldocument_by_year(client: OpenFDAClient, year: int | str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_historicaldocument_by_field(client, "year", str(year), **kw)


def search_historicaldocument_by_num_pages(client: OpenFDAClient, pages: int | str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_historicaldocument_by_field(client, "num_of_pages", str(pages), **kw)


def search_historicaldocument_full_text(client: OpenFDAClient, phrase: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Full-text match against the OCRed document text."""
    return search_historicaldocument_by_field(client, "text", phrase, **kw)


def search_historicaldocument_by_download_url(client: OpenFDAClient, url_part: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    """Substring/term match on the original PDF URL (hosted by FDA)."""
    return search_historicaldocument_by_field(client, "download_url", url_part, **kw)


# Date/number range helpers

def _range(field: str, start: str, end: str) -> str:
    return f"{field}:[{start} TO {end}]"


def search_historicaldocument_between_years(client: OpenFDAClient, start_year: int | str, end_year: int | str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_historicaldocument(client, search=_range("year", str(start_year), str(end_year)), **kw)


def search_historicaldocument_between_pages(client: OpenFDAClient, min_pages: int | str, max_pages: int | str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_historicaldocument(client, search=_range("num_of_pages", str(min_pages), str(max_pages)), **kw)


# Facets

def count_historicaldocument_by_doc_type(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_historicaldocument_by_field(client, "doc_type", limit=limit, **kw)


def count_historicaldocument_by_year(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_historicaldocument_by_field(client, "year", limit=limit, **kw)


# ============================
# NSDE endpoint conveniences
# ============================

# Generic builders validated against other_nsde.yaml

def search_nsde_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_nsde(client, search=q(field, term, endpoint=ENDPOINT_NSDE), **kw)


def count_nsde_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_nsde(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar based on other_nsde.yaml fields

def search_nsde_by_package_ndc(client: OpenFDAClient, ndc: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_nsde_by_field(client, "package_ndc", ndc, **kw)


def search_nsde_by_package_ndc11(client: OpenFDAClient, ndc11: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_nsde_by_field(client, "package_ndc11", ndc11, **kw)


def search_nsde_by_proprietary_name(client: OpenFDAClient, name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_nsde_by_field(client, "proprietary_name", name, **kw)


def search_nsde_by_dosage_form(client: OpenFDAClient, dosage: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_nsde_by_field(client, "dosage_form", dosage, **kw)


def search_nsde_by_marketing_category(client: OpenFDAClient, category: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_nsde_by_field(client, "marketing_category", category, **kw)


def search_nsde_by_application_number_or_citation(client: OpenFDAClient, app_no: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_nsde_by_field(client, "application_number_or_citation", app_no, **kw)


def search_nsde_by_product_type(client: OpenFDAClient, prod_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_nsde_by_field(client, "product_type", prod_type, **kw)


def search_nsde_by_billing_unit(client: OpenFDAClient, unit: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_nsde_by_field(client, "billing_unit", unit, **kw)


# Date range helpers (YYYYMMDD)

def _range(field: str, start: str, end: str) -> str:
    return f"{field}:[{start} TO {end}]"


def search_nsde_between_marketing_start_date(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_nsde(client, search=_range("marketing_start_date", start, end), **kw)


def search_nsde_between_marketing_end_date(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_nsde(client, search=_range("marketing_end_date", start, end), **kw)


def search_nsde_between_inactivation_date(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_nsde(client, search=_range("inactivation_date", start, end), **kw)


def search_nsde_between_reactivation_date(client: OpenFDAClient, start: str, end: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_nsde(client, search=_range("reactivation_date", start, end), **kw)


# Facet helpers for common buckets

def count_nsde_by_marketing_category(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_nsde_by_field(client, "marketing_category", limit=limit, **kw)


def count_nsde_by_product_type(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_nsde_by_field(client, "product_type", limit=limit, **kw)


def count_nsde_by_dosage_form(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_nsde_by_field(client, "dosage_form", limit=limit, **kw)


# ============================
# Substance endpoint conveniences
# ============================

# Generic builders validated against other_substance.yaml

def search_substance_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_substance(client, search=q(field, term, endpoint=ENDPOINT_SUBSTANCE), **kw)


def count_substance_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_substance(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar based on other_substance.yaml fields

def search_substance_by_unii(client: OpenFDAClient, unii: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_substance_by_field(client, "unii", unii, **kw)


def search_substance_by_uuid(client: OpenFDAClient, uuid: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_substance_by_field(client, "uuid", uuid, **kw)


def search_substance_by_name(client: OpenFDAClient, name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_substance_by_field(client, "names.name", name, **kw)


def search_substance_by_name_type(client: OpenFDAClient, name_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_substance_by_field(client, "names.type", name_type, **kw)


def search_substance_by_name_domain(client: OpenFDAClient, domain: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_substance_by_field(client, "names.domains", domain, **kw)


def search_substance_by_name_language(client: OpenFDAClient, lang: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_substance_by_field(client, "names.languages", lang, **kw)


def search_substance_by_structural_class(client: OpenFDAClient, cls: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_substance_by_field(client, "substance_class", cls, **kw)


def search_substance_by_relationship_type(client: OpenFDAClient, rel_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_substance_by_field(client, "relationships.type", rel_type, **kw)


def search_substance_by_polymer_type(client: OpenFDAClient, poly_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_substance_by_field(client, "polymer.polymer_class", poly_type, **kw)


def search_substance_by_organism_genus(client: OpenFDAClient, genus: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_substance_by_field(client, "structurally_diverse.organism_genus", genus, **kw)


def search_substance_by_organism_species(client: OpenFDAClient, species: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_substance_by_field(client, "structurally_diverse.organism_species", species, **kw)


def search_substance_by_molecular_formula(client: OpenFDAClient, formula: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_substance_by_field(client, "structure.formula", formula, **kw)


def search_substance_by_stereochemistry(client: OpenFDAClient, stereo: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_substance_by_field(client, "structure.stereochemistry", stereo, **kw)


def search_substance_by_relationship_interaction(client: OpenFDAClient, interaction: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_substance_by_field(client, "relationships.interaction_type", interaction, **kw)


def search_substance_by_source_material_type(client: OpenFDAClient, src_type: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_substance_by_field(client, "structurally_diverse.source_material_type", src_type, **kw)


def search_substance_by_version(client: OpenFDAClient, version: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_substance_by_field(client, "version", version, **kw)


# Facet helpers for common buckets

def count_substance_by_structural_class(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_substance_by_field(client, "substance_class", limit=limit, **kw)


def count_substance_by_name_type(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_substance_by_field(client, "names.type", limit=limit, **kw)


def count_substance_by_polymer_class(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_substance_by_field(client, "polymer.polymer_class", limit=limit, **kw)


def count_substance_by_source_material_type(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_substance_by_field(client, "structurally_diverse.source_material_type", limit=limit, **kw)


# ============================
# UNII endpoint conveniences
# ============================

# Generic builders validated against other_unii.yaml

def search_unii_by_field(client: OpenFDAClient, field: str, term: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_unii(client, search=q(field, term, endpoint=ENDPOINT_UNII), **kw)


def count_unii_by_field(client: OpenFDAClient, field: str, /, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_unii(client, count=f"{field}.exact", limit=limit, **kw)


# Targeted sugar based on other_unii.yaml fields

def search_unii_by_substance_name(client: OpenFDAClient, name: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_unii_by_field(client, "substance_name", name, **kw)


def search_unii_by_unii(client: OpenFDAClient, unii: str, /, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return search_unii_by_field(client, "unii", unii, **kw)


# Facet helpers for common buckets

def count_unii_by_substance_name(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_unii_by_field(client, "substance_name", limit=limit, **kw)


def count_unii_by_unii(client: OpenFDAClient, limit: int = 1000, **kw: Any) -> APIResponse[Dict[str, Any]]:
    return count_unii_by_field(client, "unii", limit=limit, **kw)