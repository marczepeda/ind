

from __future__ import annotations
from typing import Any, Mapping, Optional
from .client import SeerClient, JSON
from .utils import get_category

CATEGORY = "mph"

def get_mph_group_by_id(
    client: SeerClient,
    id: str,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/mph/group/{id}
    Returns the group information for a given group ID.

    Parameters
    ----------
    id : str
        MPH group identifier.
    """
    endpoint = f"group/{id}"
    params: dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


def list_mph_groups(
    client: SeerClient,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/mph/groups
    Returns a list of all MPH groups.
    """
    endpoint = "groups"
    params: dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)