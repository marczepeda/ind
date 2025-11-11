from __future__ import annotations
from typing import Any, Mapping, Optional, Sequence, Dict, Union

from .client import SeerClient, JSON

# ----------------------- HTTP/path helpers -----------------------

def get_category(
    client: SeerClient,
    category: str,
    endpoint: str,
    *,
    params: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    Compose SEER REST paths consistently and dispatch via the client.

    Builds: /rest/{category}/{endpoint}
    (endpoint may be an empty string to target the category root).
    """
    cat = (category or "").strip("/")
    ep = (endpoint or "").lstrip("/")
    path = f"/rest/{cat}" + (f"/{ep}" if ep else "")
    return client.request_json("GET", path, params=params)

# ----------------------- param utilities ------------------------

def bool_str(value: Optional[bool]) -> Optional[str]:
    """Serialize a bool to the API's expected "true"/"false" strings."""
    if value is None:
        return None
    return "true" if value else "false"

def join_csv(values: Optional[Sequence[str] | str | bytes]) -> Optional[str]:
    """Normalize sequences/strings into a comma-separated string for query params."""
    if values is None:
        return None
    if isinstance(values, (str, bytes)):
        return values.decode() if isinstance(values, bytes) else values
    cleaned = [v for v in values if v is not None and str(v) != ""]
    return ",".join(str(v) for v in cleaned) if cleaned else None

def put(params: Dict[str, Any], key: str, value: Optional[Union[str, int, bool]]) -> None:
    """Safe put: ignores None; bools serialized to "true"/"false"."""
    if value is None:
        return
    if isinstance(value, bool):
        params[key] = bool_str(value)
    else:
        params[key] = value

def cap_count(value: Optional[int], *, max_value: int) -> Optional[int]:
    """Cap an integer parameter at a given maximum if provided."""
    if value is None:
        return None
    v = int(value)
    return min(v, max_value)
