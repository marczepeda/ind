from __future__ import annotations
"""
Helpers for the OpenFDA Animal & Veterinary endpoints.

Base endpoint for adverse events:
    https://api.fda.gov/animalandveterinary/event.json

Notes
-----
- `search` uses OpenFDA's Solr/Lucene syntax: field:term (quote multi-word terms).
- `limit` defaults to your global default and is clamped to 1000 per OpenFDA rules.
- Use `count` to request facet aggregations instead of full documents.
- For field validation and suggestions, pair with `ind.openfda.query.q(..., endpoint=ENDPOINT_EVENT)`
  if you are using per-endpoint YAML schemas.
"""

from typing import Any, Dict, Mapping, Optional, Sequence

from .client import OpenFDAClient
from .types import APIResponse, Meta, MetaResults
from .utils import build_params, paginate

# Endpoint identifiers
BASE = "/animalandveterinary"
ENDPOINT_EVENT = "animalandveterinary/event"


def _wrap(data: Dict[str, Any]) -> APIResponse[Dict[str, Any]]:
    """Normalize the OpenFDA JSON payload into our APIResponse."""
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
# Adverse event search
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
    """Query animal & veterinary adverse events.

    Parameters
    ----------
    client : OpenFDAClient
        Configured client instance.
    search : str, optional
        Solr-style query string (e.g., 'term:VALUE' or 'field:"multi word"').
    limit : int, optional
        Number of records to return (clamped to <= 1000).
    skip : int, optional
        Offset for pagination.
    sort : str, optional
        Sort expression, e.g. 'date_received:desc'.
    count : str, optional
        Facet field for aggregations (returns buckets rather than documents).
    extra : Mapping[str, Any], optional
        Any additional query parameters supported by the API.
    """
    params = build_params(
        search=search, limit=limit, skip=skip, sort=sort, count=count, extra=extra
    )
    data = client.request_json("GET", f"{BASE}/event.json", params=params)
    return _wrap(data)


def iter_events(
    client: OpenFDAClient,
    *,
    search: Optional[str] = None,
    limit: int = 100,
    max_records: Optional[int] = None,
    sort: Optional[str] = None,
):
    """Iterate over event results across pages.

    Use `max_records` to stop early after yielding N records.
    """
    yield from paginate(
        client,
        f"{BASE}/event.json",
        search=search,
        limit=limit,
        max_records=max_records,
        sort=sort,
    )


# ----------------------------
# Convenience helpers (no schema dependency)
# ----------------------------

def _quote_term(term: str) -> str:
    """Quote a term if it contains spaces or special chars and escape quotes."""
    needs_quotes = any(c.isspace() or c in ':/()' for c in term)
    safe = term.replace('"', r'\"')
    return f'"{safe}"' if needs_quotes else safe


def search_events_by_field(
    client: OpenFDAClient,
    field: str,
    term: str,
    /,
    **kwargs: Any,
) -> APIResponse[Dict[str, Any]]:
    """Build a simple `search=field:term` query and execute it.

    Examples
    --------
    # By VeDDRA term name (see animalandveterinary_event.yaml)
    # field="reaction.veddra_term_name", term="Vomiting"
    return: APIResponse
    """
    search = f"{field}:{_quote_term(term)}"
    return search_events(client, search=search, **kwargs)


def count_events_by_field(
    client: OpenFDAClient,
    field: str,
    /,
    limit: int = 1000,
    **kwargs: Any,
) -> APIResponse[Dict[str, Any]]:
    """Facet counts for a field using `count`.

    Returns buckets rather than full documents.
    """
    return search_events(client, count=f"{field}.exact", limit=limit, **kwargs)


# Targeted sugar for common fields from the YAML

def search_events_by_veddra_term(
    client: OpenFDAClient,
    term: str,
    /,
    **kwargs: Any,
) -> APIResponse[Dict[str, Any]]:
    """Search by reaction VeDDRA term name.

    Field path comes from the endpoint schema (reaction.veddra_term_name).
    """
    return search_events_by_field(client, "reaction.veddra_term_name", term, **kwargs)


def count_events_by_veddra_term(
    client: OpenFDAClient,
    limit: int = 1000,
    **kwargs: Any,
) -> APIResponse[Dict[str, Any]]:
    """Facet counts for reaction VeDDRA term names."""
    return count_events_by_field(client, "reaction.veddra_term_name", limit=limit, **kwargs)
