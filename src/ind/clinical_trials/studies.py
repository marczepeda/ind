from __future__ import annotations
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .client import ClinicalTrialsClient

__all__ = [
    "list_studies",
    "iterate_studies",
    "get_study",
    "get_studies_metadata",
    "get_search_areas",
    "get_enums",
]

# ------------------------- helpers ------------------------------------------

def _join(values: Optional[Iterable[str]]) -> Optional[str]:
    if not values:
        return None
    # Accept comma/pipe strings or iterables; normalize to comma list
    if isinstance(values, (str, bytes)):
        s = values.decode() if isinstance(values, bytes) else values
        return s
    return ",".join(v for v in values if v is not None and v != "")

def _put(params: Dict[str, Any], key: str, value: Optional[str | int | bool]) -> None:
    if value is None:
        return
    if isinstance(value, bool):
        params[key] = "true" if value else "false"
    else:
        params[key] = value

# ------------------------- Studies Endpoints --------------------------------

def list_studies(
    client: ClinicalTrialsClient,
    *,
    # --- format controls (JSON only supported by this client)
    markup_format: str = "markdown",  # "markdown" | "legacy" (json only)
    # --- query.* (Essie syntax)
    query_cond: Optional[str] = None,
    query_term: Optional[str] = None,
    query_locn: Optional[str] = None,
    query_titles: Optional[str] = None,
    query_intr: Optional[str] = None,
    query_outc: Optional[str] = None,
    query_spons: Optional[str] = None,
    query_lead: Optional[str] = None,
    query_id: Optional[str] = None,
    query_patient: Optional[str] = None,
    # --- filter.* (arrays / strings)
    filter_overall_status: Optional[Sequence[str]] = None,
    filter_geo: Optional[str] = None,                 # e.g. distance(lat,lon,50mi)
    filter_ids: Optional[Sequence[str]] = None,       # NCT IDs
    filter_advanced: Optional[str] = None,           # Essie query
    filter_synonyms: Optional[Sequence[str]] = None, # area:synonym_id
    # --- postFilter.* (same semantics)
    postfilter_overall_status: Optional[Sequence[str]] = None,
    postfilter_geo: Optional[str] = None,
    postfilter_ids: Optional[Sequence[str]] = None,
    postfilter_advanced: Optional[str] = None,
    postfilter_synonyms: Optional[Sequence[str]] = None,
    # --- misc ranking/aggregation
    agg_filters: Optional[str] = None,               # e.g. "results:with,status:com"
    geo_decay: Optional[str] = None,                 # e.g. "func:exp,scale:300mi,offset:0mi,decay:0.5"
    # --- projection / sorting
    fields: Optional[Sequence[str]] = None,          # if provided, must be non-empty
    sort: Optional[Sequence[str]] = None,            # up to 2 items; e.g., ["@relevance", "LastUpdatePostDate:desc"]
    count_total: bool = False,                       # include totalCount on first page
    # --- paging
    page_size: int = 10,
    page_token: Optional[str] = None,
    # --- escape hatch (rare)
    passthrough: Optional[Mapping[str, Any]] = None, # copied as-is into query params
) -> Dict[str, Any]:
    """
    GET /studies — Returns one page of studies that match the provided parameters.

    Notes
    -----
    * This client **only** uses JSON format (CSV is incompatible with request_json()).
    * If `fields` is set, it must be a non-empty list per API rules.
    * Keep the same parameters for subsequent pages (except count_total, page_size, page_token).
    """
    # Guard against CSV (client expects JSON)
    params: Dict[str, Any] = {"format": "json", "markupFormat": markup_format}

    # query.*
    _put(params, "query.cond", query_cond)
    _put(params, "query.term", query_term)
    _put(params, "query.locn", query_locn)
    _put(params, "query.titles", query_titles)
    _put(params, "query.intr", query_intr)
    _put(params, "query.outc", query_outc)
    _put(params, "query.spons", query_spons)
    _put(params, "query.lead", query_lead)
    _put(params, "query.id", query_id)
    _put(params, "query.patient", query_patient)

    # filter.*
    _put(params, "filter.overallStatus", _join(filter_overall_status))
    _put(params, "filter.geo", filter_geo)
    _put(params, "filter.ids", _join(filter_ids))
    _put(params, "filter.advanced", filter_advanced)
    _put(params, "filter.synonyms", _join(filter_synonyms))

    # postFilter.*
    _put(params, "postFilter.overallStatus", _join(postfilter_overall_status))
    _put(params, "postFilter.geo", postfilter_geo)
    _put(params, "postFilter.ids", _join(postfilter_ids))
    _put(params, "postFilter.advanced", postfilter_advanced)
    _put(params, "postFilter.synonyms", _join(postfilter_synonyms))

    # ranking/aggregation helpers
    _put(params, "aggFilters", agg_filters)
    _put(params, "geoDecay", geo_decay)

    # projection / sort
    if fields is not None:
        joined_fields = _join(fields)
        if not joined_fields:
            raise ValueError("`fields` must be a non-empty list or non-empty string when provided.")
        _put(params, "fields", joined_fields)

    if sort is not None:
        sort_list = list(sort)
        if len(sort_list) > 2:
            raise ValueError("`sort` accepts at most 2 items (e.g., ['@relevance', 'LastUpdatePostDate:desc']).")
        _put(params, "sort", _join(sort_list))

    # totals + paging
    _put(params, "countTotal", bool(count_total))
    _put(params, "pageSize", int(page_size))
    if page_token:
        _put(params, "pageToken", page_token)

    # passthrough (last-wins)
    if passthrough:
        params.update(passthrough)

    return client.request_json("GET", "/studies", params=params)


def iterate_studies(
    client: ClinicalTrialsClient,
    *,
    # mirror the list_studies signature (except page_token/page_size can change)
    markup_format: str = "markdown",
    query_cond: Optional[str] = None,
    query_term: Optional[str] = None,
    query_locn: Optional[str] = None,
    query_titles: Optional[str] = None,
    query_intr: Optional[str] = None,
    query_outc: Optional[str] = None,
    query_spons: Optional[str] = None,
    query_lead: Optional[str] = None,
    query_id: Optional[str] = None,
    query_patient: Optional[str] = None,
    filter_overall_status: Optional[Sequence[str]] = None,
    filter_geo: Optional[str] = None,
    filter_ids: Optional[Sequence[str]] = None,
    filter_advanced: Optional[str] = None,
    filter_synonyms: Optional[Sequence[str]] = None,
    postfilter_overall_status: Optional[Sequence[str]] = None,
    postfilter_geo: Optional[str] = None,
    postfilter_ids: Optional[Sequence[str]] = None,
    postfilter_advanced: Optional[str] = None,
    postfilter_synonyms: Optional[Sequence[str]] = None,
    agg_filters: Optional[str] = None,
    geo_decay: Optional[str] = None,
    fields: Optional[Sequence[str]] = None,
    sort: Optional[Sequence[str]] = None,
    # paging controls
    first_page_size: int = 100,
    next_page_size: Optional[int] = None,   # if None, reuse first_page_size
    max_pages: Optional[int] = None,        # None = all pages until token stops
    passthrough: Optional[Mapping[str, Any]] = None,
    include_total_on_first_page: bool = True,
) -> Tuple[Dict[str, Any], ...]:
    """
    Paginate over /studies and return a tuple of page JSON dicts.

    API rule compliance:
    - First page may include `countTotal` and your chosen `pageSize`.
    - Subsequent pages keep the same parameters, changing only `pageSize` (optional) and `pageToken`.
    """
    pages: List[Dict[str, Any]] = []
    token: Optional[str] = None
    pages_seen = 0
    nxt_size = next_page_size if next_page_size is not None else first_page_size

    # Prepare a fixed kwargs dict to ensure consistency across pages
    fixed_kwargs = dict(
        markup_format=markup_format,
        query_cond=query_cond,
        query_term=query_term,
        query_locn=query_locn,
        query_titles=query_titles,
        query_intr=query_intr,
        query_outc=query_outc,
        query_spons=query_spons,
        query_lead=query_lead,
        query_id=query_id,
        query_patient=query_patient,
        filter_overall_status=filter_overall_status,
        filter_geo=filter_geo,
        filter_ids=filter_ids,
        filter_advanced=filter_advanced,
        filter_synonyms=filter_synonyms,
        postfilter_overall_status=postfilter_overall_status,
        postfilter_geo=postfilter_geo,
        postfilter_ids=postfilter_ids,
        postfilter_advanced=postfilter_advanced,
        postfilter_synonyms=postfilter_synonyms,
        agg_filters=agg_filters,
        geo_decay=geo_decay,
        fields=fields,
        sort=sort,
        passthrough=passthrough,
    )

    while True:
        is_first = (pages_seen == 0)
        page = list_studies(
            client,
            page_token=token,
            page_size=first_page_size if is_first else nxt_size,
            count_total=(include_total_on_first_page if is_first else False),
            **fixed_kwargs,
        )
        pages.append(page)
        pages_seen += 1
        token = page.get("nextPageToken")

        if not token:
            break
        if max_pages is not None and pages_seen >= max_pages:
            break

    return tuple(pages)



def get_study(
    client: ClinicalTrialsClient,
    nct_id: str,
    *,
    format: str = "json",                 # "json" | "fhir.json"
    markup_format: str = "markdown",      # only for json
    fields: Optional[Sequence[str]] = None,  # only for json
) -> Dict[str, Any]:
    """
    GET /studies/{nctId}

    Notes
    -----
    * Supported formats: "json" (default) and "fhir.json".
    * For "json": you may pass `fields` (non-empty) and `markup_format` ("markdown"|"legacy").
    * For "fhir.json": `fields` must be omitted (API returns a fixed FHIR structure).
    """
    if format not in ("json", "fhir.json"):
        raise ValueError("Only 'json' and 'fhir.json' are supported by this client.")

    params: Dict[str, Any] = {"format": format}

    if format == "json":
        params["markupFormat"] = markup_format
        if fields is not None:
            joined = ",".join(fields) if fields else ""
            if not joined:
                raise ValueError("`fields` must be a non-empty list when provided.")
            params["fields"] = joined
    else:
        # fhir.json — fields must be unspecified
        if fields is not None:
            raise ValueError("`fields` must be omitted when format='fhir.json'.")

    return client.request_json("GET", f"/studies/{nct_id}", params=params)


def get_studies_metadata(
    client: ClinicalTrialsClient,
    *,
    include_indexed_only: bool = False,
    include_historic_only: bool = False,
) -> Dict[str, Any]:
    """GET /studies/metadata — returns data model field definitions."""
    params: Dict[str, Any] = {}
    _put(params, "includeIndexedOnly", bool(include_indexed_only))
    _put(params, "includeHistoricOnly", bool(include_historic_only))
    return client.request_json("GET", "/studies/metadata", params=params)


def get_search_areas(client: ClinicalTrialsClient) -> Dict[str, Any]:
    """GET /studies/search-areas — returns available search areas."""
    return client.request_json("GET", "/studies/search-areas")


def get_enums(client: ClinicalTrialsClient) -> Dict[str, Any]:
    """GET /studies/enums — returns enumerations for certain fields."""
    return client.request_json("GET", "/studies/enums")