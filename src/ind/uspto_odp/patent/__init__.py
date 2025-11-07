"""
USPTO Open Data Portal — Bulk datasets API.

Endpoints implemented:
  - GET /api/v1/datasets/products/search
  - GET /api/v1/datasets/products/{productIdentifier}
  - (helper) download_product_file() to stream fileDownloadURI to disk
"""

from .applications import (
    # Search endpoints
    search_applications, download_search,
    # Per-application endpoints
    get_application, get_meta_data, get_adjustment, get_assignment, get_attorney,
    get_continuity, get_foreign_priority, get_transactions, get_documents, get_associated_documents,
)

from .status_codes import get_status_codes

__all__ = [
    # Search + download
    "search_applications", "download_search",
    # Per-application
    "get_application", "get_meta_data", "get_adjustment", "get_assignment", "get_attorney",
    "get_continuity", "get_foreign_priority", "get_transactions", "get_documents", "get_associated_documents",
    # Metadata / status
    "get_status_codes",
]