from __future__ import annotations
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Optional
from urllib.parse import urlencode

MAX_LIMIT = 1000
DEFAULT_LIMIT = 100

def build_params(
    *,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    sort: Optional[str] = None,
    count: Optional[str] = None,
    extra: Optional[Mapping[str, Any]] = None,
    params = {},
) -> Dict[str, Any]:
    """Build an OpenFDA query parameter dict.

    - `search`: Solr/Lucene query string
    - `limit`: number of records (max varies by endpoint; default 100)
    - `skip`: offset for pagination
    - `sort`: e.g., "receivedate:desc"
    - `count`: facet term, e.g., "patient.reaction.reactionmeddrapt.exact"
    """
    if search: 
        params["search"] = search
    if limit is not None:
        params["limit"] = max(1, min(int(limit), MAX_LIMIT))
    if skip is not None: 
        params["skip"] = int(skip)
    if sort: 
        params["sort"] = sort
    if count: 
        params["count"] = count
    if extra: 
        params.update(extra)
    return params

def paginate(
    client: "OpenFDAClient",
    path: str,
    *,
    search: Optional[str] = None,
    limit: int = DEFAULT_LIMIT,
    max_records: Optional[int] = None,
    sort: Optional[str] = None,
) -> Iterable[Dict[str, Any]]:
    """Yield results across pages.

    Stops at `max_records` if provided.
    """
    fetched = 0
    skip = 0
    while True:
        remaining = None if max_records is None else max(0, max_records - fetched)
        page_limit = limit if remaining is None else min(limit, remaining)
        params = build_params(search=search, limit=page_limit, skip=skip, sort=sort)
        data = client.request_json("GET", path, params=params)
        results = data.get("results") or []
        for item in results:
            yield item
        batch = len(results)
        fetched += batch
        if batch < page_limit or (max_records is not None and fetched >= max_records):
            break
        skip += batch