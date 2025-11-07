from __future__ import annotations

import sys
import json
from pathlib import Path
from typing import List, Optional

from .client import USPTOClient
from .types import Pagination, SortOrder, Filter, RangeFilter, Sort
from .patent import (
    search_applications, download_search,
    get_application, get_meta_data, get_adjustment, get_assignment, get_attorney,
    get_continuity, get_foreign_priority, get_transactions, get_documents, get_associated_documents,
    get_status_codes,
)
from .bulk import search_products, get_product, download_product_file
from .petitions import search_decisions, download_search_decisions, get_decision


def _json_print(obj, pretty: bool = True):
    if pretty:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(obj, separators=(",", ":"), ensure_ascii=False))


def add_subparser(subparsers, formatter_class):
    """Register `uspto` command with subcommands under it."""
    p = subparsers.add_parser("uspto", help="USPTO Open Data Portal CLI", description="USPTO Open Data Portal CLI", formatter_class=formatter_class)
    p.set_defaults(_cmd="uspto")

    p.add_argument("--api-key", default=None, help="USPTO ODP x-api-key")
    p.add_argument("--method", default="auto", choices=["auto", "GET", "POST"], help="HTTP method strategy")
    p.add_argument("--compact", action="store_true", help="compact JSON output (no pretty indent)")
    p.add_argument("--troubleshoot", action="store_true", help="print request bodies/params")

    sp = p.add_subparsers(dest="domain", required=True)

    # ---------------- PATENT ----------------
    pat = sp.add_parser("patent", help="Patent application endpoints", description="Patent application endpoints", formatter_class=formatter_class)
    pat_sp = pat.add_subparsers(dest="action", required=True)

    # search
    pat_search = pat_sp.add_parser("search", help="Search patent applications", description="Search patent applications", formatter_class=formatter_class)
    pat_search.add_argument("-q", default=None, help="Lucene query string")
    pat_search.add_argument("--offset", type=int, default=0)
    pat_search.add_argument("--limit", type=int, default=25)
    pat_search.add_argument("--fields", nargs="*", default=[])
    pat_search.add_argument("--facet", dest="facets", nargs="*", default=[])
    pat_search.set_defaults(_pat_action="search")

    # download (search/download)
    pat_dl = pat_sp.add_parser("download", help="Download search results (bytes)", description="Download search results (bytes)", formatter_class=formatter_class)
    pat_dl.add_argument("-q", default=None)
    pat_dl.add_argument("--offset", type=int, default=0)
    pat_dl.add_argument("--limit", type=int, default=25)
    pat_dl.add_argument("--fields", nargs="*", default=[])
    pat_dl.add_argument("--facet", dest="facets", nargs="*", default=[])
    pat_dl.add_argument("--out", help="Destination file path; if omitted, prints byte length")
    pat_dl.set_defaults(_pat_action="download")

    # by-id
    pat_get = pat_sp.add_parser("get", help="Get application by number", description="Get application by number", formatter_class=formatter_class)
    pat_get.add_argument("application_number")
    pat_get.set_defaults(_pat_action="get")

    # simple subresources
    for name in [
        ("meta", "get_meta_data"),
        ("adjustment", "get_adjustment"),
        ("assignment", "get_assignment"),
        ("attorney", "get_attorney"),
        ("continuity", "get_continuity"),
        ("foreign-priority", "get_foreign_priority"),
        ("transactions", "get_transactions"),
        ("documents", "get_documents"),
        ("associated-documents", "get_associated_documents"),
    ]:
        sname, func = name
        sub = pat_sp.add_parser(sname, help=f"GET /api/v1/patent/applications/{{num}}/{sname.replace('_','-')}", description=f"GET /api/v1/patent/applications/{{num}}/{sname.replace('_','-')}", formatter_class=formatter_class)
        sub.add_argument("application_number")
        sub.set_defaults(_pat_action=func)

    # status-codes
    pat_codes = pat_sp.add_parser("status-codes", help="Patent application status codes", description="Patent application status codes", formatter_class=formatter_class)
    pat_codes.add_argument("-q", default=None)
    pat_codes.set_defaults(_pat_action="status_codes")

    # ---------------- BULK ----------------
    bulk = sp.add_parser("bulk", help="Bulk datasets", description="Bulk datasets")
    bulk_sp = bulk.add_subparsers(dest="action", required=True)

    bulk_search = bulk_sp.add_parser("search", help="Search bulk products", description="Search bulk products", formatter_class=formatter_class)
    bulk_search.add_argument("-q", default=None)
    bulk_search.add_argument("--limit", type=int, default=10)
    bulk_search.set_defaults(_bulk_action="search")

    bulk_get = bulk_sp.add_parser("get", help="Get product by identifier", description="Get product by identifier", formatter_class=formatter_class)
    bulk_get.add_argument("product_identifier")
    bulk_get.add_argument("--include-files", action="store_true")
    bulk_get.add_argument("--latest", action="store_true")
    bulk_get.add_argument("--limit", type=int, default=None)
    bulk_get.set_defaults(_bulk_action="get")

    bulk_dl = bulk_sp.add_parser("download-file", help="Download a file by fileDownloadURI", description="Download a file by fileDownloadURI", formatter_class=formatter_class)
    bulk_dl.add_argument("file_download_uri")
    bulk_dl.add_argument("--out", required=True, help="Destination path")
    bulk_dl.set_defaults(_bulk_action="download_file")

    # ---------------- PETITIONS ----------------
    pet = sp.add_parser("petitions", help="Petition decisions", description="Petition decisions", formatter_class=formatter_class)
    pet_sp = pet.add_subparsers(dest="action", required=True)

    pet_search = pet_sp.add_parser("search", help="Search petition decisions", description="Search petition decisions", formatter_class=formatter_class)
    pet_search.add_argument("-q", default=None)
    pet_search.add_argument("--offset", type=int, default=0)
    pet_search.add_argument("--limit", type=int, default=25)
    pet_search.add_argument("--fields", nargs="*", default=[])
    pet_search.set_defaults(_pet_action="search")

    pet_dl = pet_sp.add_parser("download", help="Download petition decisions search", description="Download petition decisions search", formatter_class=formatter_class)
    pet_dl.add_argument("-q", default=None)
    pet_dl.add_argument("--offset", type=int, default=0)
    pet_dl.add_argument("--limit", type=int, default=25)
    pet_dl.add_argument("--fields", nargs="*", default=[])
    pet_dl.add_argument("--format", default="json", choices=["json", "csv"])
    pet_dl.add_argument("--out", help="Destination file")
    pet_dl.set_defaults(_pet_action="download")

    pet_get = pet_sp.add_parser("get", help="Get petition decision by id", description="Get petition decision by id", formatter_class=formatter_class)
    pet_get.add_argument("decision_id")
    pet_get.add_argument("--include-documents", action="store_true")
    pet_get.set_defaults(_pet_action="get")


def _mk_client(args) -> USPTOClient:
    return USPTOClient(api_key=args.api_key)


def run(args) -> int:
    client = _mk_client(args)
    pretty = not args.compact

    if args.domain == "patent":
        act = args._pat_action
        if act == "search":
            res = search_applications(
                client,
                q=args.q,
                fields=args.fields or None,
                pagination=Pagination(args.offset, args.limit),
                facets=args.facets or None,
                method=args.method,
                troubleshoot=args.troubleshoot,
            )
            _json_print(res, pretty)
            return 0

        if act == "download":
            payload = dict(
                q=args.q,
                fields=args.fields or None,
                pagination=Pagination(args.offset, args.limit),
                facets=args.facets or None,
            )
            data = download_search(
                client,
                **payload,
                method=args.method,
                dest_path=args.out,
                troubleshoot=args.troubleshoot,
            )
            if isinstance(data, (bytes, bytearray)):
                print(f"[download] {len(data)} bytes")
            else:
                print(f"[saved] {data}")
            return 0

        if act == "get":
            _json_print(get_application(client, args.application_number), pretty)
            return 0

        # subresources
        fn_map = {
            "get_meta_data": get_meta_data,
            "get_adjustment": get_adjustment,
            "get_assignment": get_assignment,
            "get_attorney": get_attorney,
            "get_continuity": get_continuity,
            "get_foreign_priority": get_foreign_priority,
            "get_transactions": get_transactions,
            "get_documents": get_documents,
            "get_associated_documents": get_associated_documents,
        }
        if act in fn_map:
            _json_print(fn_map[act](client, args.application_number), pretty)
            return 0

        if act == "status_codes":
            _json_print(get_status_codes(client, q=args.q, method=args.method, troubleshoot=args.troubleshoot), pretty)
            return 0

    elif args.domain == "bulk":
        act = args._bulk_action
        if act == "search":
            res = search_products(client, q=args.q, limit=args.limit, troubleshoot=args.troubleshoot)
            _json_print(res, pretty)
            return 0
        if act == "get":
            res = get_product(
                client,
                args.product_identifier,
                include_files=args.include_files,
                latest=args.latest,
                limit=args.limit,
                troubleshoot=args.troubleshoot,
            )
            _json_print(res, pretty)
            return 0
        if act == "download_file":
            path = download_product_file(client, args.file_download_uri, dest_path=args.out)
            print(f"[saved] {path}")
            return 0

    elif args.domain == "petitions":
        act = args._pet_action
        if act == "search":
            res = search_decisions(
                client,
                q=args.q,
                fields=args.fields or None,
                pagination=Pagination(args.offset, args.limit),
                method=args.method,
                troubleshoot=args.troubleshoot,
            )
            _json_print(res, pretty)
            return 0
        if act == "download":
            body = dict(
                q=args.q,
                fields=args.fields or None,
                pagination=Pagination(args.offset, args.limit),
            )
            data = download_search_decisions(
                client,
                **body,
                format=args.format,
                method=args.method,
                dest_path=args.out,
                troubleshoot=args.troubleshoot,
            )
            if isinstance(data, (bytes, bytearray)):
                print(f"[download] {len(data)} bytes")
            else:
                print(f"[saved] {data}")
            return 0
        if act == "get":
            _json_print(get_decision(client, args.decision_id, include_documents=args.include_documents), pretty)
            return 0

    print("Unknown command. Use --help.", file=sys.stderr)
    return 2