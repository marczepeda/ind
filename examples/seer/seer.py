#!/usr/bin/env python3
"""
SEER API Examples CLI

Quick demonstrations of the helpers in ind.seer.*

Usage examples:
  python seer.py versions
  python seer.py disease-search latest --q lymphoma --type HEMATO --count 10
  python seer.py glossary-list latest --q lymph --category GENERAL STAGING --count 25
  python seer.py ndc-search --q bevacizumab --category IMMUNOTHERAPY --has-seer-info
  python seer.py rx-search latest --q bevacizumab --type DRUG --category CHEMOTHERAPY
  python seer.py staging-schema ajcc8 latest lung
  python seer.py surgery-table latest --title "Oral Cavity"
  python seer.py naaccr-items 22 --q "primary site" --count 25
  python seer.py hcpcs-search --q bevacizumab --order date_modified

Notes
-----
* These examples make live HTTP requests to https://api.seer.cancer.gov.
* An API key is required. Set the environment variable SEER_API_KEY or pass --api-key.
* Keep counts modest to be polite to the public service.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, Optional, Sequence
from pprint import pprint

from ind.seer.client import SeerClient
from ind.seer import (
    glossary as seer_glossary,
    disease as seer_disease,
    hcpcs as seer_hcpcs,
    mph as seer_mph,
    naaccr as seer_naaccr,
    ndc as seer_ndc,
    recode as seer_recode,
    rx as seer_rx,
    staging as seer_staging,
    surgery as seer_surgery,
)

# ------------------------- version helpers -------------------------
def _extract_version(value: Any) -> Optional[str]:
    """Best-effort extraction of a version string from an API response entry."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        # common keys we might see
        for k in ("version", "dbVersion", "name", "id"):
            v = value.get(k)
            if isinstance(v, str):
                return v
    return None

def _first_version_from_response(resp: Any) -> Optional[str]:
    # try list at top-level
    if isinstance(resp, list) and resp:
        v = _extract_version(resp[0])
        if v:
            return v
    # try dict with common list containers
    if isinstance(resp, dict):
        for key in ("versions", "items", "data", "results"):
            seq = resp.get(key)
            if isinstance(seq, list) and seq:
                v = _extract_version(seq[0])
                if v:
                    return v
    return None

def _resolve_latest(version: str, fetch_versions_fn) -> str:
    if str(version).lower() != "latest":
        return version
    try:
        resp = fetch_versions_fn()
        v = _first_version_from_response(resp)
        if not v:
            raise RuntimeError("Could not determine latest version from API response")
        return v
    except Exception:
        # fallback: keep the original token so the server errors explicitly
        return version

# ------------------------- util printing -------------------------

def _print_heading(title: str) -> None:
    print("\n" + title)
    print("-" * len(title))


def _pp(obj: Any, *, indent: int = 2, maxlen: int = 2000) -> None:
    """Pretty-print JSON safely with truncation."""
    try:
        s = json.dumps(obj, indent=indent, ensure_ascii=False)
    except Exception:
        pprint(obj)
        return
    if len(s) > maxlen:
        print(s[:maxlen] + "\n... [truncated] ...")
    else:
        print(s)


# ------------------------- command handlers -------------------------

def cmd_versions(client: SeerClient, args: argparse.Namespace) -> None:
    _print_heading("Glossary Versions")
    _pp(seer_glossary.list_glossary_versions(client))

    _print_heading("Disease Versions")
    _pp(seer_disease.list_disease_versions(client))

    _print_heading("Rx Versions")
    _pp(seer_rx.list_rx_versions(client))

    _print_heading("Staging Algorithms")
    _pp(seer_staging.list_staging_algorithms(client))


def cmd_disease_search(client: SeerClient, args: argparse.Namespace) -> None:
    version = _resolve_latest(args.version, lambda: seer_disease.list_disease_versions(client))
    res = seer_disease.list_diseases(
        client,
        version,
        q=args.q,
        type=args.type,
        site_category=args.site_category,
        count=args.count,
        offset=args.offset,
        order=args.order,
    )
    _print_heading(f"Disease Search v{version}")
    _pp(res)


def cmd_disease_same(client: SeerClient, args: argparse.Namespace) -> None:
    version = _resolve_latest(args.version, lambda: seer_disease.list_disease_versions(client))
    res = seer_disease.is_same_disease(
        client,
        version,
        d1=args.d1,
        year1=args.year1,
        d2=args.d2,
        year2=args.year2,
    )
    _print_heading(f"Disease Compare v{version}")
    _pp(res)


def cmd_glossary_list(client: SeerClient, args: argparse.Namespace) -> None:
    version = _resolve_latest(args.version, lambda: seer_glossary.list_glossary_versions(client))
    res = seer_glossary.list_glossary(
        client,
        version,
        q=args.q,
        category=args.category,
        count=args.count,
        order=args.order,
    )
    _print_heading(f"Glossary v{version}")
    _pp(res)


def cmd_ndc_search(client: SeerClient, args: argparse.Namespace) -> None:
    res = seer_ndc.list_ndc(
        client,
        q=args.q,
        category=args.category,
        has_seer_info=args.has_seer_info,
        page=args.page,
        per_page=args.per_page,
        order=args.order,
    )
    _print_heading("NDC Search")
    _pp(res)


def cmd_rx_search(client: SeerClient, args: argparse.Namespace) -> None:
    version = _resolve_latest(args.version, lambda: seer_rx.list_rx_versions(client))
    res = seer_rx.list_rx(
        client,
        version,
        q=args.q,
        type=args.type,
        category=args.category,
        do_not_code=args.do_not_code,
        count=args.count,
        offset=args.offset,
        order=args.order,
    )
    _print_heading(f"Rx Search v{version}")
    _pp(res)


def cmd_staging_schema(client: SeerClient, args: argparse.Namespace) -> None:
    _print_heading(f"Staging {args.algorithm} {args.version} – schema {args.schema_id}")
    res = seer_staging.get_staging_schema_by_id(client, args.algorithm, args.version, args.schema_id)
    _pp(res)


def cmd_surgery_table(client: SeerClient, args: argparse.Namespace) -> None:
    res = seer_surgery.get_surgery_table(
        client,
        args.year,
        title=args.title,
        site=args.site,
        hist=args.hist,
    )
    _print_heading(f"Surgery {args.year} table")
    _pp(res)


def cmd_naaccr_items(client: SeerClient, args: argparse.Namespace) -> None:
    res = seer_naaccr.list_naaccr_items(client, args.version, q=args.q, count=args.count)
    _print_heading(f"NAACCR {args.version} items")
    _pp(res)


def cmd_hcpcs_search(client: SeerClient, args: argparse.Namespace) -> None:
    res = seer_hcpcs.list_hcpcs(
        client,
        q=args.q,
        category=args.category,
        page=args.page,
        per_page=args.per_page,
        order=args.order,
    )
    _print_heading("HCPCS Search")
    _pp(res)


# ------------------------- argparse wiring -------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="SEER API examples (ind.seer)")
    p.add_argument("--base-url", default="https://api.seer.cancer.gov", help="Override SEER base URL")
    p.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout (s)")
    p.add_argument("--api-key", help="NCI SEER API key (or set SEER_API_KEY env var)")

    sp = p.add_subparsers(dest="cmd", required=True)

    # versions
    sp.add_parser("versions", help="Show versions/algorithms across categories")

    # disease search
    d = sp.add_parser("disease-search", help="Search diseases")
    d.add_argument("version", help="Disease version (e.g., latest)")
    d.add_argument("--q", help="Search query")
    d.add_argument("--type", choices=["SOLID_TUMOR", "HEMATO", "NON_NEOPLASTIC"], help="Disease classification")
    d.add_argument("--site-category", nargs="+", help="Limit to site categories (solid tumor only)")
    d.add_argument("--count", type=int, default=25)
    d.add_argument("--offset", type=int, default=0)
    d.add_argument("--order", help="Sort order (e.g., name, -name)")

    # disease compare
    c = sp.add_parser("disease-same", help="Determine if two morphologies represent the same disease")
    c.add_argument("version", help="Disease version (e.g., latest)")
    c.add_argument("--d1", required=True, help="Morphology code 1 (e.g., 8000/3)")
    c.add_argument("--year1", required=True, help="Diagnosis year 1 (YYYY)")
    c.add_argument("--d2", required=True, help="Morphology code 2 (e.g., 8140/3)")
    c.add_argument("--year2", required=True, help="Diagnosis year 2 (YYYY)")

    # glossary list
    g = sp.add_parser("glossary-list", help="List glossary entries")
    g.add_argument("version", help="Glossary version (e.g., latest)")
    g.add_argument("--q")
    g.add_argument("--category", nargs="+")
    g.add_argument("--count", type=int, default=25)
    g.add_argument("--order")

    # ndc search
    n = sp.add_parser("ndc-search", help="Search NDC products")
    n.add_argument("--q")
    n.add_argument("--category", nargs="+")
    n.add_argument("--has-seer-info", action="store_true")
    n.add_argument("--page", type=int, default=1)
    n.add_argument("--per-page", type=int, default=25)
    n.add_argument("--order")

    # rx search
    r = sp.add_parser("rx-search", help="Search SEER Rx entries")
    r.add_argument("version", help="Rx version (e.g., latest)")
    r.add_argument("--q")
    r.add_argument("--type", choices=["DRUG", "REGIMEN"])
    r.add_argument("--category", nargs="+")
    r.add_argument("--do-not-code", choices=["YES", "NO", "SEE_REMARKS"])
    r.add_argument("--count", type=int, default=25)
    r.add_argument("--offset", type=int, default=0)
    r.add_argument("--order")

    # staging schema
    s = sp.add_parser("staging-schema", help="Fetch a staging schema")
    s.add_argument("algorithm", help="Algorithm (e.g., ajcc8)")
    s.add_argument("version", help="Algorithm version (e.g., 1.1)")
    s.add_argument("schema_id", help="Schema identifier (e.g., lung)")

    # surgery table
    su = sp.add_parser("surgery-table", help="Fetch a surgery table")
    su.add_argument("year", help='Year (e.g., "latest")')
    group = su.add_mutually_exclusive_group(required=True)
    group.add_argument("--title", help="Table title")
    group.add_argument("--site", help="Primary site (ICDO2/ICDO3)")
    su.add_argument("--hist", help="Histology (ICDO code)")

    # naaccr items
    na = sp.add_parser("naaccr-items", help="List NAACCR items for a version")
    na.add_argument("version", help="Record layout version (e.g., 22)")
    na.add_argument("--q")
    na.add_argument("--count", type=int, default=25)

    # hcpcs search
    h = sp.add_parser("hcpcs-search", help="Search HCPCS procedures")
    h.add_argument("--q")
    h.add_argument("--category", nargs="+")
    h.add_argument("--page", type=int, default=1)
    h.add_argument("--per-page", type=int, default=25)
    h.add_argument("--order")

    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    client = SeerClient(base_url=args.base_url, timeout=args.timeout, api_key=args.api_key)

    try:
        if args.cmd == "versions":
            cmd_versions(client, args)
        elif args.cmd == "disease-search":
            cmd_disease_search(client, args)
        elif args.cmd == "disease-same":
            cmd_disease_same(client, args)
        elif args.cmd == "glossary-list":
            cmd_glossary_list(client, args)
        elif args.cmd == "ndc-search":
            cmd_ndc_search(client, args)
        elif args.cmd == "rx-search":
            cmd_rx_search(client, args)
        elif args.cmd == "staging-schema":
            cmd_staging_schema(client, args)
        elif args.cmd == "surgery-table":
            cmd_surgery_table(client, args)
        elif args.cmd == "naaccr-items":
            cmd_naaccr_items(client, args)
        elif args.cmd == "hcpcs-search":
            cmd_hcpcs_search(client, args)
        else:
            parser.error(f"Unknown command: {args.cmd}")
            return 2
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())