"""
SEER (Surveillance, Epidemiology, and End Results) API module

This package provides wrappers for the official NCI SEER API endpoints.
src/ind/seer/:
├── client.py             base HTTP client with API key and retry support
├── utils.py              shared helper functions
├── disease.py            Disease endpoints
├── glossary.py           Glossary endpoints
├── hcpcs.py              HCPCS endpoints
├── mph.py                Multiple Primary and Histology endpoints
├── naaccr.py             NAACCR record layout endpoints
├── ndc.py                NDC drug endpoints
├── recode.py             Site recode endpoints
├── rx.py                 SEER Rx endpoints
├── staging.py            Staging endpoints
└── surgery.py            Surgery endpoints

Usage:
    from ind.seer.client import SeerClient
    from ind.seer import disease, rx

    client = SeerClient(api_key="YOUR_SEER_API_KEY")
    versions = disease.list_disease_versions(client)
    print(versions)
"""

from .client import SeerClient, SeerError
from . import (
    utils,
    disease,
    glossary,
    hcpcs,
    mph,
    naaccr,
    ndc,
    recode,
    rx,
    staging,
    surgery,
)

__all__ = [
    "SeerClient",
    "SeerError",
    "utils",
    "disease",
    "glossary",
    "hcpcs",
    "mph",
    "naaccr",
    "ndc",
    "recode",
    "rx",
    "staging",
    "surgery",
]
