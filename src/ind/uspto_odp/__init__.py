'''
src/ind/uspto_odp/
├── __init__.py             re-export a simple facade
├── cli.py                  command line interface
├── client.py               shared HTTP client (session, retries, timeouts, base urls)
├── types.py                common dataclasses and helper functions
└── patent/                 patent search endpoints
│  ├── __init__.py         
│  ├── applications.py     
│  └── status_codes.py     
└── bulk/                   bulk datasets endpoints
│  ├── __init__.py         
│  ├── products.py
└── petitions/              petition decision search endpoints
│  ├── __init__.py         
│  ├── decisions.py
'''

from .client import USPTOClient
from . import patent as patent
from . import bulk as bulk
from . import petitions as petitions
from .types import Filter, RangeFilter, SortOrder, Sort, Pagination

__all__ = ["USPTOClient", "patent", "bulk", "petitions",
           "Filter", "RangeFilter", "SortOrder", "Sort", "Pagination"]