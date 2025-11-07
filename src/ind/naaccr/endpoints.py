from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

import time

from .client import NAACCRClient

JSON = Union[Dict[str, Any], List[Any]]

# The allowed attributes for /data_item/{number_or_xml_id}/history/
_ALLOWED_ATTRS = {
    "ItemName",
    "ItemLength",
    "YearImplemented",
    "VersionImplemented",
    "YearRetired",
    "VersionRetired",
    "Section",
    "SourceOfStandard",
    "DateCreated",
    "DateModified",
    "Description",
    "Rationale",
    "Clarification",
    "GeneralNotes",
    "NpcrCollect",
    "CocCollect",
    "SeerCollect",
    "CccrCollect",
    "Format",
    "CodeDescription",
    "CodeNote",
    "ItemDataType",
    "AllowableValues",
}


def list_versions(client: NAACCRClient) -> JSON:
    """
    GET /naaccr_versions/

    Returns info about all NAACCR versions.
    """
    return client.request_json("GET", "/naaccr_versions/", params={"format": "json"})


def get_data_item(
    client: NAACCRClient,
    naaccr_version: str,
    number_or_xml_id: str,
    minimize_results: bool = False,
) -> JSON:
    """
    GET /data_item/{naaccr_version}/{number_or_xml_id}/

    Retrieve the full record for a single data item by either NAACCR item number or XML id.
    If minimize_results is True, only a subset of fields will be returned.
    """
    path = f"/data_item/{naaccr_version}/{number_or_xml_id}/"
    params: Dict[str, Any] = {"format": "json"}
    if minimize_results:
        params["minimize_results"] = "true"
    return client.request_json("GET", path, params=params)


def search_data_items(
    client: NAACCRClient,
    naaccr_version: str,
    *,
    q: Optional[str] = None,
    minimize_results: bool = False,
    pages: int = 1,
    delay: float = 0.25,
) -> JSON:
    """
    GET /data_item/{naaccr_version}/?q=...

    Returns a list of items. The NAACCR API paginates responses and returns a
    JSON envelope with keys {count, next, previous, results}. This helper will:
      - fetch the first page, normalize to a list, and
      - if `pages > 1`, follow `next` up to the specified number of pages.

    A short sleep is used between page requests to avoid overloading the server.
    The delay (in seconds) between page requests can be adjusted via the
    `delay` argument.
    """
    if pages < 1:
        pages = 1

    params: Dict[str, Any] = {"format": "json"}
    if q is not None and str(q).strip():
        params["q"] = q
    if minimize_results:
        # Client handles quoting as minimize_results="true"
        params["minimize_results"] = "true"

    path = f"/data_item/{naaccr_version}/"
    resp = client.request_json("GET", path, params=params)

    items: List[Any] = []
    next_url: Optional[str] = None

    if isinstance(resp, dict) and "results" in resp:
        items.extend(list(resp.get("results") or []))
        next_url = resp.get("next")
    elif isinstance(resp, list):
        items.extend(resp)
        next_url = None
    else:
        return [resp]

    remaining = max(0, pages - 1)
    while remaining > 0 and next_url:
        time.sleep(delay)  # be polite to the public API
        r = client.session.get(next_url, timeout=client.timeout)
        r.raise_for_status()
        page = r.json()
        if isinstance(page, dict) and "results" in page:
            items.extend(list(page.get("results") or []))
            next_url = page.get("next")
        elif isinstance(page, list):
            items.extend(page)
            next_url = None
        else:
            break
        remaining -= 1

    return items


def get_attribute_history(
    client: NAACCRClient,
    number_or_xml_id: str,
    *,
    attribute: str,
) -> JSON:
    """
    GET /data_item/{number_or_xml_id}/history/?attribute=...

    Return the history for a single attribute across all supported versions.
    """
    if attribute not in _ALLOWED_ATTRS:
        allowed = ", ".join(sorted(_ALLOWED_ATTRS))
        raise ValueError(
            f"Invalid attribute '{attribute}'. Must be one of: {allowed}"
        )

    params = {"attribute": attribute, "format": "json"}
    path = f"/data_item/{number_or_xml_id}/history/"
    return client.request_json("GET", path, params=params)


def get_operation_history(
    client: NAACCRClient,
    naaccr_version: str,
    number_or_xml_id: str,
) -> JSON:
    """
    GET /data_item/operation_history/{naaccr_version}/{number_or_xml_id}/

    Returns the operation history (Operation, ModifiedAttribute, OldValue, NewValue) for a data item
    within a specific NAACCR version.
    """
    path = f"/data_item/operation_history/{naaccr_version}/{number_or_xml_id}/"
    return client.request_json("GET", path, params={"format": "json"})