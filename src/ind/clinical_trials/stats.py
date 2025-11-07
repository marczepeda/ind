from __future__ import annotations
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

from .client import ClinicalTrialsClient

__all__ = [
    "get_study_sizes",
    "get_field_values",
    "get_field_sizes",
    # Back-compat alias:
    "get_size",
]

# ------------------------- Stats Endpoints ---------------------------------

def get_study_sizes(client: ClinicalTrialsClient) -> Dict[str, Any]:
    """
    GET /stats/size  — Statistics of study JSON sizes.
    Returns a dict like:
      {
        "averageSizeBytes": int,
        "largestStudies": [{"id": str, "sizeBytes": int}, ...],
        "percentiles": {...},
        "ranges": [{"sizeRange": str, "studiesCount": int}, ...],
        "totalStudies": int
      }
    """
    return client.request_json("GET", "/stats/size")


# Back-compat: old name `get_size` -> `get_study_sizes`
def get_size(client: ClinicalTrialsClient) -> Dict[str, Any]:  # pragma: no cover
    return get_study_sizes(client)


def get_field_values(
    client: ClinicalTrialsClient,
    *,
    fields: Optional[Sequence[str]] = None,
    types: Optional[Sequence[str]] = None,  # ENUM | STRING | DATE | INTEGER | NUMBER | BOOLEAN
) -> List[Dict[str, Any]]:
    """
    GET /stats/field/values  — Value statistics of leaf fields.

    Params
    ------
    fields : Optional[list[str]]
        Filter by piece names or field paths (comma-joined). If omitted, API returns all available stats.
    types : Optional[list[str]]
        Filter by field types (ENUM, STRING, DATE, INTEGER, NUMBER, BOOLEAN).

    Returns
    -------
    list[dict]
      e.g. [{
        "field": "Phase",
        "piece": "ConditionsModule",
        "type": "ENUM",
        "missingStudiesCount": 0,
        "uniqueValuesCount": 3,
        "topValues": [{"value": "Phase 2", "studiesCount": 123}, ...]
      }]
    """
    params: Dict[str, Any] = {}
    if fields is not None:
        joined = ",".join(fields) if fields else ""
        if not joined:
            raise ValueError("`fields` must be a non-empty list when provided.")
        params["fields"] = joined
    if types is not None:
        joined = ",".join(types) if types else ""
        if not joined:
            raise ValueError("`types` must be a non-empty list when provided.")
        params["types"] = joined

    # API returns a JSON array
    res = client.request_json("GET", "/stats/field/values", params=params)
    # Some HTTP clients coerce arrays at top-level; normalize to list
    return res if isinstance(res, list) else list(res or [])


def get_field_sizes(
    client: ClinicalTrialsClient,
    *,
    fields: Optional[Sequence[str]] = None,
) -> List[Dict[str, Any]]:
    """
    GET /stats/field/sizes  — Sizes of list/array fields.

    Params
    ------
    fields : Optional[list[str]]
        Filter by piece names or field paths (comma-joined). If omitted, API returns all available stats.

    Returns
    -------
    list[dict]
      e.g. [{
        "field": "protocolSection.armsInterventionsModule.armGroups.interventionNames",
        "piece": "ArmsInterventionsModule",
        "minSize": 0,
        "maxSize": 4,
        "uniqueSizesCount": 3,
        "topSizes": [{"size": 1, "studiesCount": 1000}, ...]
      }]
    """
    params: Dict[str, Any] = {}
    if fields is not None:
        joined = ",".join(fields) if fields else ""
        if not joined:
            raise ValueError("`fields` must be a non-empty list when provided.")
        params["fields"] = joined

    res = client.request_json("GET", "/stats/field/sizes", params=params)
    return res if isinstance(res, list) else list(res or [])