"""
src/ind/ncbi/
├── __init__.py             Initializer
├── client.py               Entrez configuration + request wrapper + rate limiting
├── utils.py                helpers (ID chunking, XML→dict, retries, coercions)
├── endpoints.py            thin, typed wrappers around esearch/efetch/...
├── workflows.py            higher-level workflows (e.g., fetch all records for a query)
├── cli.py                  subparsers for E-utilities
└── types.py                light dataclasses / TypedDicts (optional but nice)
"""
from .client import EntrezClient, NCBIConfig