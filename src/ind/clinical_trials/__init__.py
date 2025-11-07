"""
src/ind/clinical_trials/
├── __init__.py                 Initializer
├── client.py                   HTTP client for ClinicalTrials.gov REST API 2.0.5
├── stats.py                    stats endpoint
├── studies.py                  studies endpoint
├── version.py                  version endpoint
└── cli.py                      command line interface
"""
from .client import ClinicalTrialsClient, ClinicalTrialsError
from .studies import (
    list_studies,
    iterate_studies,
    get_study,
    get_studies_metadata,
    get_search_areas,
    get_enums,
)
from .stats import (
    get_study_sizes,  # new canonical name
    get_field_values,
    get_field_sizes,
    get_size,         # back-compat alias
)
from .version import get_version

__all__ = [
    "ClinicalTrialsClient",
    "ClinicalTrialsError",
    # studies
    "list_studies",
    "iterate_studies",
    "get_study",
    "get_studies_metadata",
    "get_search_areas",
    "get_enums",
    # stats
    "get_study_sizes",
    "get_field_values",
    "get_field_sizes",
    "get_size",
    # version
    "get_version",
]