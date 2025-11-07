from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Mapping, Optional, Sequence, TypeVar

T = TypeVar("T")

@dataclass
class MetaResults:
    total: Optional[int] = None
    skip: Optional[int] = None
    limit: Optional[int] = None

@dataclass
class Meta:
    disclaimer: Optional[str] = None
    terms: Optional[str] = None
    license: Optional[str] = None
    last_updated: Optional[str] = None
    results: Optional[MetaResults] = None

@dataclass
class APIResponse(Generic[T]):
    meta: Meta
    results: Sequence[T] | None = None