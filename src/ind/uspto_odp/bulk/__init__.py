"""
USPTO Open Data Portal — Bulk datasets API.

Endpoints implemented:
  - GET /api/v1/datasets/products/search
  - GET /api/v1/datasets/products/{productIdentifier}
"""

from .products import search_products, get_product, download_product_file

__all__ = [
    "search_products",
    "get_product",
    "download_product_file",
]