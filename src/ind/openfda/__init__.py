"""
src/ind/openfda/
├── __init__.py             initializer
├── cli.py                  command line interface
├── client.py               shared HTTP client, retries, key, query helpers
├── utils.py                pagination, query building, validation
├── types.py                pydantic/dataclasses for Meta, Response wrappers
├── data/                   .yaml files for schema, field mappings, etc.
├── schema.py               data models for OpenFDA schema objects
├── drug.py                 concrete endpoints (event, label, ndc, enforcement, drugsfda)
├── device.py               (stubs) event, recall, 510k, classification, enforcement
├── food.py                 (stubs) enforcement, event
├── cosmetic.py             (stubs) adverse events
├── tobacco.py              (stubs) compliance
├── animal_veterinary.py    (stubs) adverse events
├── transparency.py         (stubs) API status / datasets
└── other.py                (stubs) NDC directory legacy, etc.

OpenFDA API client and endpoint helpers for the ind package.

Example usage:
    from ind.openfda import OpenFDAClient, drug

    client = OpenFDAClient(api_key=os.getenv("OPENFDA_API_KEY"))
    res = drug.search_events(client, search='patient.reaction.reactionmeddrapt:"HEADACHE"', limit=5)
    print(res.meta.results.total, len(res.results))
"""

from .client import OpenFDAClient
from . import (
    drug,
    device,
    food,
    cosmetic,
    tobacco,
    animal_veterinary,
    transparency,
    other,
    utils,
    types,
    schema,
)

__all__ = [
    "OpenFDAClient",
    "drug",
    "device",
    "food",
    "cosmetic",
    "tobacco",
    "animal_veterinary",
    "transparency",
    "other",
    "utils",
    "types",
    "schema",
]