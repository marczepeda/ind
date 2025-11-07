"""
tests/uspto_odp/endpoints.py — USPTO Open Data Portal Endpoints Smoke Test
Date: 2025-11-02

Usage:
  python tests/uspto_odp/endpoints.py <api_key> [--troubleshoot]

Notes:
  • This is a *smoke test* — it touches each endpoint with small, safe payloads.
  • We avoid large downloads. For "download" endpoints, we request tiny payloads
    and keep data in-memory (no files) or skip heavy bulk file downloads.
  • Output is human-readable; redirect to a file if you want an artifact.
"""

import sys
import argparse
from pprint import pprint

from ind.uspto_odp.client import USPTOClient
from ind.uspto_odp.types import Pagination, SortOrder, Filter, RangeFilter, Sort
from ind.uspto_odp.patent import (
    search_applications, download_search,
    get_application, get_meta_data, get_adjustment, get_assignment, get_attorney,
    get_continuity, get_foreign_priority, get_transactions, get_documents, get_associated_documents,
    get_status_codes,
)
from ind.uspto_odp.bulk import search_products, get_product
from ind.uspto_odp.petitions import (
    search_decisions, download_search_decisions, get_decision
)


# ------------------------------------------
# Helpers
# ------------------------------------------
def header(title: str):
    print("\n" + "=" * len(title))
    print(title)
    print("=" * len(title))

def sub(title: str):
    print(f"\n--- {title} ---")

def safe_call(label, func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        print(f"{label}: OK")
        return result
    except Exception as e:
        print(f"{label}: FAILED → {e}")
        return None

def first(lst, default=None):
    try:
        return lst[0]
    except Exception:
        return default


# ------------------------------------------
# Main
# ------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="USPTO ODP endpoints smoke test")
    ap.add_argument("api_key", help="USPTO ODP API key")
    ap.add_argument("--troubleshoot", action="store_true", help="print request bodies/params")
    args = ap.parse_args()

    client = USPTOClient(api_key=args.api_key)

    # -------------------------
    # PATENT: Applications search (GET/POST auto) + per-application endpoints
    # -------------------------
    header("PATENT: Applications")

    sub("POST/GET /api/v1/patent/applications/search (small query)")
    # Keep payload small; rely on auto (GET→POST fallback) and tiny limit
    search_res = safe_call(
        "Patent search",
        search_applications,
        client,
        q='applicationMetaData.applicationTypeLabelName:Utility',
        # very safe, small selection of fields
        fields=["applicationNumberText", "applicationMetaData.inventionTitle", "grantDate", "filingDate", "patentNumber"],
        pagination=Pagination(offset=0, limit=3),
        troubleshoot=args.troubleshoot,
    )
    if search_res:
        print("Search count:", search_res.get("count"))
        bag = search_res.get("patentFileWrapperDataBag", [])
        for rec in bag:
            num = rec.get("applicationNumberText")
            title = rec.get("applicationMetaData", {}).get("inventionTitle") or rec.get("inventionTitle")
            print(f"  • {num}: {title}")
    app_number = None
    if search_res:
        bag = search_res.get("patentFileWrapperDataBag") or []
        first_app = first(bag)
        if first_app:
            app_number = first_app.get("applicationNumberText")

    sub("POST/GET /api/v1/patent/applications/search/download (tiny)")
    # We’ll mirror the same small request; keep in memory (bytes)
    _dl_bytes = safe_call(
        "Patent search download",
        download_search,
        client,
        q='applicationMetaData.applicationTypeLabelName:Utility',
        fields=["applicationNumberText", "applicationMetaData.inventionTitle"],
        pagination=Pagination(offset=0, limit=1),
        troubleshoot=args.troubleshoot,
    )
    if isinstance(_dl_bytes, (bytes, bytearray)):
        print(f"Download bytes len: {len(_dl_bytes)}")

    # Per-application endpoints (best-effort; some may 404 depending on sample)
    if app_number:
        sub(f"GET /api/v1/patent/applications/{app_number}")
        _app = safe_call("Get application", get_application, client, app_number)

        sub("GET /meta-data")
        _meta = safe_call("Get meta-data", get_meta_data, client, app_number)

        sub("GET /adjustment")
        _adj = safe_call("Get adjustment", get_adjustment, client, app_number)

        sub("GET /assignment")
        _asg = safe_call("Get assignment", get_assignment, client, app_number)

        sub("GET /attorney")
        _att = safe_call("Get attorney", get_attorney, client, app_number)

        sub("GET /continuity")
        _con = safe_call("Get continuity", get_continuity, client, app_number)

        sub("GET /foreign-priority")
        _fp = safe_call("Get foreign-priority", get_foreign_priority, client, app_number)

        sub("GET /transactions")
        _trx = safe_call("Get transactions", get_transactions, client, app_number)

        sub("GET /documents")
        _docs = safe_call("Get documents", get_documents, client, app_number)

        sub("GET /associated-documents")
        _assoc = safe_call("Get associated-documents", get_associated_documents, client, app_number)
    else:
        print("No application number available from search to test per-application endpoints.")

    sub("GET/POST /api/v1/patent/status-codes")
    _codes = safe_call("Status codes (auto)", get_status_codes, client, troubleshoot=args.troubleshoot)
    if _codes:
        # Just show a couple of entries if available
        print("Status codes keys:", list(_codes.keys())[:5])

    # -------------------------
    # BULK: products search / get product (no big downloads)
    # -------------------------
    header("BULK: Datasets")

    sub("GET /api/v1/datasets/products/search (small)")
    prod_search = safe_call(
        "Bulk products search",
        search_products,
        client,
        limit=3,
        troubleshoot=args.troubleshoot,
    )
    product_identifier = None
    if prod_search:
        bag = prod_search.get("bulkDataProductBag") or []
        # API nests products as lists in lists sometimes; flatten carefully
        first_entry = None
        if bag and isinstance(bag[0], list) and bag[0]:
            first_entry = bag[0][0]
        elif bag:
            first_entry = bag[0]
        if isinstance(first_entry, dict):
            product_identifier = first_entry.get("productIdentifier")
            print("First product:", product_identifier)

    sub("GET /api/v1/datasets/products/{productIdentifier} (include_files latest)")
    if product_identifier:
        prod = safe_call(
            "Bulk get product",
            get_product,
            client,
            product_identifier,
            include_files=True,
            latest=True,
            limit=1,
            troubleshoot=args.troubleshoot,
        )
        if prod:
            # Try to show the first file URI if present (we DON'T download here)
            try:
                file_bag = prod["bulkDataProductBag"][0][0]["productFileBag"]["fileDataBag"][0]
                print("Sample fileDownloadURI:", file_bag.get("fileDownloadURI"))
            except Exception:
                pass
    else:
        print("No productIdentifier available from search; skipping get_product.")

    # -------------------------
    # PETITIONS: decision search / download / get decision
    # -------------------------
    header("PETITIONS: Decisions")

    sub("POST/GET /api/v1/petition/decisions/search (small)")
    dec_search = safe_call(
        "Petitions search",
        search_decisions,
        client,
        # Very permissive; let API pick top 25 but limit to 3 via pagination
        pagination=Pagination(offset=0, limit=3),
        fields=["petitionDecisionRecordIdentifier", "applicationNumberText", "decisionTypeCodeDescriptionText", "petitionMailDate"],
        troubleshoot=args.troubleshoot,
    )
    decision_id = None
    if dec_search:
        bag = dec_search.get("petitionDecisionDataBag") or []
        first_dec = first(bag)
        if first_dec and isinstance(first_dec, dict):
            decision_id = first_dec.get("petitionDecisionRecordIdentifier")
            print("First decision id:", decision_id)

    sub("POST/GET /api/v1/petition/decisions/search/download (tiny, json)")
    _pet_dl = safe_call(
        "Petitions search download",
        download_search_decisions,
        client,
        pagination=Pagination(offset=0, limit=1),
        fields=["petitionDecisionRecordIdentifier", "applicationNumberText"],
        format="json",
        troubleshoot=args.troubleshoot,
    )
    if isinstance(_pet_dl, (bytes, bytearray)):
        print(f"Download bytes len: {len(_pet_dl)}")

    sub("GET /api/v1/petition/decisions/{petitionDecisionRecordIdentifier}")
    if decision_id:
        _one = safe_call("Get decision (includeDocuments=True)", get_decision, client, decision_id, include_documents=True)
        if _one:
            # Show a tiny slice
            keys = list(_one.keys())
            print("Decision keys:", keys[:5])
    else:
        print("No decision id available from search; skipping get_decision.")

    print("\nDONE.")

if __name__ == "__main__":
    main()