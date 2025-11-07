from __future__ import annotations
from importlib.resources import files
from pathlib import Path
import yaml, difflib
from typing import Dict

_DATA_PKG = "ind.openfda.data"

class FieldInfo(dict):
    @property
    def name(self): return self.get("name")
    @property
    def description(self): return self.get("description")
    @property
    def type(self): return self.get("type")
    @property
    def is_exact(self): return bool(self.get("is_exact", False))

class FieldRegistry:
    def __init__(self, mapping: Dict[str, dict]):
        self._m = mapping
    def has(self, field: str) -> bool:
        return field in self._m
    def info(self, field: str) -> FieldInfo:
        return FieldInfo(self._m[field])
    def suggest(self, field: str, n: int = 5):
        return difflib.get_close_matches(field, list(self._m.keys()), n=n)

def _flatten(d, prefix=""):
    out = {}
    for k, v in (d or {}).items():
        name = f"{prefix}.{k}" if prefix else k
        out[name] = v
        if isinstance(v, dict) and "properties" in v:
            out.update(_flatten(v["properties"], name))
    return out

def load_registry_for(endpoint: str) -> FieldRegistry:
    """
    endpoint: e.g. 'drug/event', 'drug/label'
    Maps to data file '{category}_{name}.yaml'
    """
    category, name = endpoint.split("/", 1)
    filename = f"{category}_{name}.yaml"   # drug_event.yaml
    text = files(_DATA_PKG).joinpath(filename).read_text(encoding="utf-8")
    raw = yaml.safe_load(text) or {}
    props = raw.get("properties") or {}
    return FieldRegistry(_flatten(props))