"""Bulk datasets — products endpoints.

Implements:
  - GET /api/v1/datasets/products/search
  - GET /api/v1/datasets/products/{productIdentifier}
Plus helper: download_product_file() for fileDownloadURI streaming.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Sequence, Union

from ..client import USPTOClient
from ..types import (
    comma_param, string_or_json, maybe_pprint
)

# =======================
# Internal helpers
# =======================

StrOrSeq = Union[str, Sequence[str]]

# =======================
# Products endpoints
# =======================
def search_products(
    client: USPTOClient,
    *,
    q: Optional[str] = None,
    sort: Optional[str] = None,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    facets: Optional[StrOrSeq] = None,
    fields: Optional[StrOrSeq] = None,
    filters: Optional[Union[str, Mapping[str, Any], Sequence[Any]]] = None,
    range_filters: Optional[Union[str, Mapping[str, Any], Sequence[Any]]] = None,
    troubleshoot: bool = False,
) -> Dict[str, Any]:
    """
    GET /api/v1/datasets/products/search

    Search bulk dataset products. All query parameters are optional. When none are supplied,
    the API returns the top 25 products.

    Parameters
    ----------
    q : str, optional
        Lucene-style query string supporting AND/OR/NOT, wildcards (*), and quoted phrases.
    sort : str, optional
        "<field> <order>", e.g. "lastModifiedDateTime desc".
    offset : int, optional
        Position in the dataset (start index).
    limit : int, optional
        Max number of results to return.
    facets : str | Sequence[str], optional
        One or more field names to facet by. Joined with commas for the API.
    fields : str | Sequence[str], optional
        Limits response to specific fields. Joined with commas for the API.
    filters : str | dict | list, optional
        Server expects a *string*. You may pass a preformatted string or a dict/list; dict/list
        will be JSON-encoded for convenience.
    range_filters : str | dict | list, optional
        Same treatment as `filters`, for numeric/date range filters.
    troubleshoot : bool, optional
        If True, pretty-print the built query parameters before sending.

    Returns
    -------
    dict
        Parsed JSON (includes "count", "bulkDataProductBag", and optional "facets").

    Raises
    ------
    BadRequestError, ForbiddenError, NotFoundError, ServerError
        Mapped by USPTOClient._raise_for_status
    """
    path = "/api/v1/datasets/products/search"

    params: Dict[str, Any] = {}
    if q:
        params["q"] = q
    if sort:
        params["sort"] = sort
    if offset is not None:
        params["offset"] = int(offset)
    if limit is not None:
        params["limit"] = int(limit)

    facets_param = comma_param(facets)
    if facets_param:
        params["facets"] = facets_param

    fields_param = comma_param(fields)
    if fields_param:
        params["fields"] = fields_param

    filters_param = string_or_json(filters)
    if filters_param:
        params["filters"] = filters_param

    range_param = string_or_json(range_filters)
    if range_param:
        params["rangeFilters"] = range_param

    maybe_pprint(params, troubleshoot, "Bulk Dataset Search Params")
    return client.request_json("GET", path, params=params if params else None)


def get_product(
    client: USPTOClient,
    product_identifier: str,
    *,
    file_data_from_date: Optional[str] = None,  # yyyy-MM-dd
    file_data_to_date: Optional[str] = None,    # yyyy-MM-dd
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    include_files: Optional[bool] = None,
    latest: Optional[bool] = None,
    troubleshoot: bool = False,
) -> Dict[str, Any]:
    """
    GET /api/v1/datasets/products/{productIdentifier}

    Fetch a bulk data product by its shortName (productIdentifier). Supports optional
    filtering of the embedded file list and pagination over product files.

    Parameters
    ----------
    product_identifier : str
        The product short name (e.g., "PTFWPRE").
    file_data_from_date : str, optional
        Lower bound for file data date (yyyy-MM-dd).
    file_data_to_date : str, optional
        Upper bound for file data date (yyyy-MM-dd).
    offset : int, optional
        Number of product file records to skip.
    limit : int, optional
        Number of product file records to return.
    include_files : bool, optional
        If True, include productFileBag in the response; if False, omit it.
        If None, do not send the parameter (server default).
    latest : bool, optional
        If True, return only the latest product file for this product.
    troubleshoot : bool, optional
        If True, pretty-print the built query parameters before sending.

    Returns
    -------
    dict
        Parsed JSON (includes "bulkDataProductBag" and optional "productFileBag").

    Raises
    ------
    BadRequestError, ForbiddenError, NotFoundError, ServerError
        Mapped by USPTOClient._raise_for_status
    """
    path = f"/api/v1/datasets/products/{product_identifier}"

    params: Dict[str, Any] = {}

    if file_data_from_date:
        params["fileDataFromDate"] = file_data_from_date
    if file_data_to_date:
        params["fileDataToDate"] = file_data_to_date
    if offset is not None:
        params["offset"] = int(offset)
    if limit is not None:
        params["limit"] = int(limit)

    # API expects "true"/"false" strings
    if include_files is True:
        params["includeFiles"] = "true"
    elif include_files is False:
        params["includeFiles"] = "false"

    if latest is True:
        params["latest"] = "true"
    elif latest is False:
        params["latest"] = "false"
    
    maybe_pprint(params, troubleshoot, "Bulk Get Product Params")

    return client.request_json("GET", path, params=params if params else None)

def download_product_file(
    client: USPTOClient,
    file_download_uri: str,
    *,
    dest_path: Optional[str] = None,
    chunk_bytes: int = 1024 * 1024,
) -> bytes | str:
    """
    Download a bulk dataset file given its `fileDownloadURI` from the API response.

    Typical flow:
      1) Search or get a product (include_files=True / latest=True)
      2) Extract `fileDownloadURI` from a fileDataBag entry
      3) Call this helper to stream the file to disk (or return bytes)

    Examples
    --------
    >>> prod = get_product(client, "PTFWPRE", include_files=True, latest=True)
    >>> file_uri = prod["bulkDataProductBag"][0][0]["productFileBag"]["fileDataBag"][0]["fileDownloadURI"]
    >>> download_product_file(client, file_uri, dest_path="downloads/PTFWPRE_latest.zip")
    'downloads/PTFWPRE_latest.zip'
    """
    return client.download_url(file_download_uri, dest_path=dest_path, chunk_bytes=chunk_bytes)