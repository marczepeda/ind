from __future__ import annotations
from typing import Any, Dict

from .client import ClinicalTrialsClient

__all__ = ["get_version"]

def get_version(client: ClinicalTrialsClient) -> Dict[str, Any]:
    """GET /version"""
    return client.request_json("GET", "/version")