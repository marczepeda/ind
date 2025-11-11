from __future__ import annotations

import argparse
import json
from typing import Any, Optional, Sequence

from .client import SeerClient
from . import (
    glossary as seer_glossary,
    disease as seer_disease,
    hcpcs as seer_hcpcs,
    naaccr as seer_naaccr,
    ndc as seer_ndc,
    rx as seer_rx,
    staging as seer_staging,
    surgery as seer_surgery,
)

DEFAULT_BASE_URL = "https://api.seer.cancer.gov"

# ------------------------- helpers -------------------------

def _pp(obj: Any, *, indent: int = 2) -> None:
    print(json.dumps(obj, indent=indent, ensure_ascii=False))


def _extract_version(value: Any) -> Optional[str]:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for k in ("version", "dbVersion", "name", "id"):
            v = value.get(k)
            if isinstance(v, str):
                return v
    return None


def _first_version_from_response(resp: Any) -> Optional[str]:
    if isinstance(resp, list) and resp:
        v = _extract_version(resp[0])
        if v:
            return v
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
        return v or version
    except Exception:
        return version


# ------------------------- command handlers -------------------------

def _make_client(args: argparse.Namespace) -> SeerClient:
    return SeerClient(
        base_url=getattr(args, "base_url", DEFAULT_BASE_URL),
        timeout=getattr(args, "timeout", 30.0),
        api_key=getattr(args, "api_key", None),
    )


def _run_versions(args: argparse.Namespace) -> int:
    client = _make_client(args)
    out = {
        "glossary_versions": seer_glossary.list_glossary_versions(client),
        "disease_versions": seer_disease.list_disease_versions(client),
        "rx_versions": seer_rx.list_rx_versions(client),
        "staging_algorithms": seer_staging.list_staging_algorithms(client),
    }
    _pp(out)
    return 0


def _run_disease_search(args: argparse.Namespace) -> int:
    client = _make_client(args)
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
    _pp({"version": version, "result": res})
    return 0


def _run_disease_same(args: argparse.Namespace) -> int:
    client = _make_client(args)
    version = _resolve_latest(args.version, lambda: seer_disease.list_disease_versions(client))
    res = seer_disease.is_same_disease(
        client,
        version,
        d1=args.d1,
        year1=args.year1,
        d2=args.d2,
        year2=args.year2,
    )
    _pp({"version": version, "result": res})
    return 0


def _run_glossary_list(args: argparse.Namespace) -> int:
    client = _make_client(args)
    version = _resolve_latest(args.version, lambda: seer_glossary.list_glossary_versions(client))
    res = seer_glossary.list_glossary(
        client,
        version,
        q=args.q,
        category=args.category,
        count=args.count,
        order=args.order,
    )
    _pp({"version": version, "result": res})
    return 0


def _run_ndc_search(args: argparse.Namespace) -> int:
    client = _make_client(args)
    res = seer_ndc.list_ndc(
        client,
        q=args.q,
        category=args.category,
        has_seer_info=args.has_seer_info,
        page=args.page,
        per_page=args.per_page,
        order=args.order,
    )
    _pp(res)
    return 0


def _run_rx_search(args: argparse.Namespace) -> int:
    client = _make_client(args)
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
    _pp({"version": version, "result": res})
    return 0


def _run_staging_schema(args: argparse.Namespace) -> int:
    client = _make_client(args)
    res = seer_staging.get_staging_schema_by_id(client, args.algorithm, args.version, args.schema_id)
    _pp(res)
    return 0


def _run_surgery_table(args: argparse.Namespace) -> int:
    client = _make_client(args)
    res = seer_surgery.get_surgery_table(
        client,
        args.year,
        title=args.title,
        site=args.site,
        hist=args.hist,
    )
    _pp(res)
    return 0


def _run_naaccr_items(args: argparse.Namespace) -> int:
    client = _make_client(args)
    res = seer_naaccr.list_naaccr_items(client, args.version, q=args.q, count=args.count)
    _pp(res)
    return 0


def _run_hcpcs_search(args: argparse.Namespace) -> int:
    client = _make_client(args)
    res = seer_hcpcs.list_hcpcs(
        client,
        q=args.q,
        category=args.category,
        page=args.page,
        per_page=args.per_page,
        order=args.order,
    )
    _pp(res)
    return 0


# ------------------------- public: register into main -------------------------

def register_subparser(seer_subparsers: argparse._SubParsersAction, formatter_class) -> None:
    """Register the `seer` command and its subcommands into an existing argparse tree.

    Expected usage from ind.main:
        seer_parser = subparsers.add_parser("seer", help="SEER API utilities")
        ind.seer.cli.register_subparser(seer_parser.add_subparsers(...))
    """
    # Top-level options shared by subcommands
    # We create the `seer` parent parser so options are inherited.
    parent = argparse.ArgumentParser(add_help=False, formatter_class=formatter_class)
    parent.add_argument("--base-url", default=DEFAULT_BASE_URL, help="SEER base URL")
    parent.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout (s)")
    parent.add_argument("--api-key", help="SEER API key (or set SEER_API_KEY env var or config)")

    # versions
    p = seer_subparsers.add_parser("versions", parents=[parent], help="Show versions/algorithms across categories", description="Show versions/algorithms across categories", formatter_class=formatter_class)
    p.set_defaults(func=_run_versions)

    # disease-search
    d = seer_subparsers.add_parser("disease-search", parents=[parent], help="Search diseases", description="Search diseases", formatter_class=formatter_class)
    d.add_argument("version", help="Disease version (e.g., latest)")
    d.add_argument("--q")
    d.add_argument("--type", choices=["SOLID_TUMOR", "HEMATO", "NON_NEOPLASTIC"])
    d.add_argument("--site-category", nargs="+")
    d.add_argument("--count", type=int, default=25)
    d.add_argument("--offset", type=int, default=0)
    d.add_argument("--order")
    d.set_defaults(func=_run_disease_search)

    # disease-same
    c = seer_subparsers.add_parser("disease-same", parents=[parent], help="Compare morphologies for same disease", description="Compare morphologies for same disease", formatter_class=formatter_class)
    c.add_argument("version", help="Disease version (e.g., latest)")
    c.add_argument("--d1", required=True)
    c.add_argument("--year1", required=True)
    c.add_argument("--d2", required=True)
    c.add_argument("--year2", required=True)
    c.set_defaults(func=_run_disease_same)

    # glossary-list
    g = seer_subparsers.add_parser("glossary-list", parents=[parent], help="List glossary entries", description="List glossary entries", formatter_class=formatter_class)
    g.add_argument("version", help="Glossary version (e.g., latest)")
    g.add_argument("--q")
    g.add_argument("--category", nargs="+")
    g.add_argument("--count", type=int, default=25)
    g.add_argument("--order")
    g.set_defaults(func=_run_glossary_list)

    # ndc-search
    n = seer_subparsers.add_parser("ndc-search", parents=[parent], help="Search NDC products", description="Search NDC products", formatter_class=formatter_class)
    n.add_argument("--q")
    n.add_argument("--category", nargs="+")
    n.add_argument("--has-seer-info", action="store_true")
    n.add_argument("--page", type=int, default=1)
    n.add_argument("--per-page", type=int, default=25)
    n.add_argument("--order")
    n.set_defaults(func=_run_ndc_search)

    # rx-search
    r = seer_subparsers.add_parser("rx-search", parents=[parent], help="Search SEER Rx entries", description="Search SEER Rx entries", formatter_class=formatter_class)
    r.add_argument("version", help="Rx version (e.g., latest)")
    r.add_argument("--q")
    r.add_argument("--type", choices=["DRUG", "REGIMEN"])
    r.add_argument("--category", nargs="+")
    r.add_argument("--do-not-code", choices=["YES", "NO", "SEE_REMARKS"])
    r.add_argument("--count", type=int, default=25)
    r.add_argument("--offset", type=int, default=0)
    r.add_argument("--order")
    r.set_defaults(func=_run_rx_search)

    # staging-schema
    s = seer_subparsers.add_parser("staging-schema", parents=[parent], help="Fetch a staging schema", description="Fetch a staging schema", formatter_class=formatter_class)
    s.add_argument("algorithm")
    s.add_argument("version")
    s.add_argument("schema_id")
    s.set_defaults(func=_run_staging_schema)

    # surgery-table
    su = seer_subparsers.add_parser("surgery-table", parents=[parent], help="Fetch a surgery table", description="Fetch a surgery table", formatter_class=formatter_class)
    su.add_argument("year")
    group = su.add_mutually_exclusive_group(required=True)
    group.add_argument("--title")
    group.add_argument("--site")
    su.add_argument("--hist")
    su.set_defaults(func=_run_surgery_table)

    # naaccr-items
    na = seer_subparsers.add_parser("naaccr-items", parents=[parent], help="List NAACCR items for a version", description="List NAACCR items for a version", formatter_class=formatter_class)
    na.add_argument("version")
    na.add_argument("--q")
    na.add_argument("--count", type=int, default=25)
    na.set_defaults(func=_run_naaccr_items)

    # hcpcs-search
    h = seer_subparsers.add_parser("hcpcs-search", parents=[parent], help="Search HCPCS procedures", description="Search HCPCS procedures", formatter_class=formatter_class)
    h.add_argument("--q")
    h.add_argument("--category", nargs="+")
    h.add_argument("--page", type=int, default=1)
    h.add_argument("--per-page", type=int, default=25)
    h.add_argument("--order")
    h.set_defaults(func=_run_hcpcs_search)


def add_subparser(main_subparsers: argparse._SubParsersAction, formatter_class) -> None:
    """Convenience for ind.main: create `seer` group and register subcommands."""
    seer_parser = main_subparsers.add_parser("seer", help="SEER API", description="SEER API", formatter_class=formatter_class)
    seer_subparsers = seer_parser.add_subparsers(dest="seer_cmd", required=True)
    register_subparser(seer_subparsers,formatter_class)
