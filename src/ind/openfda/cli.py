from __future__ import annotations
"""
Command-line interface for the ind.openfda module.

This mirrors the structure of other ind.* CLIs: it exposes a top-level
`openfda` command under `ind` with a couple of focused subcommands that
cover most real-world use:

  ind openfda query drug/event --search 'patient.reaction.reactionmeddrapt:"Headache"' --limit 5
  ind openfda count drug/label openfda.brand_name --limit 10 --exact

It also supports an API key via:
  * --api-key
  * positional API key (after the subcommand)
  * environment variable OPENFDA_API_KEY

The order of precedence is: --api-key > positional > env.
"""

import argparse
import json
import os
from typing import Any, Dict, Optional
import sys
from rich import print as rprint

from .client import OpenFDAClient
from .utils import build_params


# -------------------------
# Helpers
# -------------------------

def _make_client(args: argparse.Namespace) -> OpenFDAClient:
    api_key_cli: Optional[str] = getattr(args, "api_key", None)
    api_key_env: Optional[str] = os.getenv("OPENFDA_API_KEY")

    api_key = api_key_cli or api_key_env

    return OpenFDAClient(
        base_url=getattr(args, "base_url", "https://api.fda.gov"),
        api_key=api_key,
        timeout=getattr(args, "timeout", 30.0),
        max_retries=getattr(args, "retries", 3),
        backoff_factor=getattr(args, "backoff", 1.5),
    )


def _print_json(d: Dict[str, Any]) -> None:
    print(json.dumps(d, indent=2))


# -------------------------
# Subcommand impls
# -------------------------

def _cmd_query(args: argparse.Namespace) -> int:
    client = _make_client(args)
    params: Dict[str, Any] = {}
    if args.search:
        params["search"] = args.search
    if args.limit is not None:
        params["limit"] = args.limit
    if args.skip is not None:
        params["skip"] = args.skip
    if args.sort:
        params["sort"] = args.sort
    if args.order:
        params["order"] = args.order

    # Raw escape hatch for future-proofing (e.g., dataset-specific params)
    if args.param:
        for kv in args.param:
            if "=" not in kv:
                raise SystemExit(f"Invalid --param '{kv}'. Expected key=value")
            k, v = kv.split("=", 1)
            params[k] = v

    resp = client.request_json("GET", f"/{args.endpoint}.json", params=params)
    _print_json(resp)
    return 0


def _cmd_count(args: argparse.Namespace) -> int:
    client = _make_client(args)

    count_field = args.field
    if args.exact and not count_field.endswith(".exact"):
        count_field = f"{count_field}.exact"

    params: Dict[str, Any] = {"count": count_field}
    if args.limit is not None:
        params["limit"] = args.limit
    if args.skip is not None:
        params["skip"] = args.skip

    # Raw escape hatch for dataset-specific params
    if args.param:
        for kv in args.param:
            if "=" not in kv:
                raise SystemExit(f"Invalid --param '{kv}'. Expected key=value")
            k, v = kv.split("=", 1)
            params[k] = v

    resp = client.request_json("GET", f"/{args.endpoint}.json", params=params)
    _print_json(resp)
    return 0


# -------------------------
# Public API consumed by ind.main
# -------------------------

def add_subparser(subparsers: argparse._SubParsersAction, Formatter: Any) -> None:
    """Register the `openfda` command and its subcommands on the main parser."""
    parser = subparsers.add_parser(
        "openfda",
        help="Query the OpenFDA APIs",
        description="Query or facet-count across OpenFDA endpoints (drug, device, food, etc.)",
        formatter_class=Formatter
    )
    sub = parser.add_subparsers(dest="openfda_cmd")

    # `query` subcommand (all options appear after `query`)
    p_q = sub.add_parser(
        "query",
        help="Run a document-level search against an OpenFDA endpoint.",
        description="Run a document-level search against an OpenFDA endpoint.",
        formatter_class=Formatter,
    )
    p_q.add_argument("endpoint", help="Endpoint path; see details below.")
    p_q.add_argument("--search", help="Lucene-like search expression, e.g. reactionmeddrapt:Headache")
    p_q.add_argument("--limit", type=int, default=None, help="Number of records to return (max 1000).")
    p_q.add_argument("--skip", type=int, default=None, help="Records to skip for pagination.")
    p_q.add_argument("--sort", help="Field to sort on (dataset dependent).")
    p_q.add_argument("--order", choices=["asc", "desc"], help="Sort order.")
    p_q.add_argument("--param", action="append", metavar="key=value",
                     help="Extra raw param(s) to pass through (may repeat).")

    # Per-subcommand runtime/API options (kept here so they only show after `query`)
    p_q.add_argument("--api-key", dest="api_key",
                     help="OpenFDA API key. If omitted, falls back to OPENFDA_API_KEY env var.")
    p_q.add_argument("--base-url", default="https://api.fda.gov", help="API base URL (default: https://api.fda.gov)")
    p_q.add_argument("--timeout", type=float, default=30.0, help="Request timeout (s).")
    p_q.add_argument("--retries", type=int, default=3, help="Max HTTP retries (default: 3).")
    p_q.add_argument("--backoff", type=float, default=1.5, help="Retry backoff factor (default: 1.5).")
    p_q.set_defaults(func=_cmd_query)

    # `count` subcommand (all options appear after `count`)
    p_c = sub.add_parser(
        "count",
        help="Facet on a field using the 'count' parameter.",
        description="Facet on a field using the 'count' parameter.",
        formatter_class=Formatter,
    )
    p_c.add_argument("endpoint", help="Endpoint path; see details below.")
    p_c.add_argument("field", help="Field to facet on. Optionally use dot paths; add --exact to suffix '.exact'.")
    p_c.add_argument("--limit", type=int, default=None, help="Max facet buckets to return.")
    p_c.add_argument("--skip", type=int, default=None, help="Facet buckets to skip (pagination).")
    p_c.add_argument("--exact", action="store_true", help="Use the '.exact' analyzer for exact term counts.")
    p_c.add_argument("--param", action="append", metavar="key=value",
                     help="Extra raw param(s) to pass through (may repeat).")

    # Per-subcommand runtime/API options (kept here so they only show after `count`)
    p_c.add_argument("--api-key", dest="api_key",
                     help="OpenFDA API key. If omitted, falls back to OPENFDA_API_KEY env var.")
    p_c.add_argument("--base-url", default="https://api.fda.gov", help="API base URL (default: https://api.fda.gov)")
    p_c.add_argument("--timeout", type=float, default=30.0, help="Request timeout (s).")
    p_c.add_argument("--retries", type=int, default=3, help="Max HTTP retries (default: 3).")
    p_c.add_argument("--backoff", type=float, default=1.5, help="Retry backoff factor (default: 1.5).")
    p_c.set_defaults(func=_cmd_count)

    # Help message for ind pe prime_designer because input file format can't be captured as block text by Myformatter(RichHelpFormatter):
    if any(["ind" in argv for argv in sys.argv]) and "openfda" in sys.argv and ("--help" in sys.argv or "-h" in sys.argv):
        if "query" in sys.argv:
            p_q.print_help()
        if "count" in sys.argv:
            p_c.print_help()
        rprint("""[red]
Details:[/red]
  [cyan]endpoint[/cyan]                      [blue]Format: category/endpoint (e.g., drug/event)
  drug/                                 
      event                     drug adverse event; FDA Adverse Event Reporting System (FAERS)
      label                     drug labeling; Structured Product Labeling (SPL) format
      ndc                       drug listing; National Drug Code Directory
      enforcement               drug enforcement reports; FDA Recall Enterprise System (RES)
      drugsfda                  Drugs@FDA; FDA-approved drug products
      shortages                 drug shortages; FDA Drug Shortages database   
  device/
      event                     medical device adverse events (MAUDE / MDR)
      recall                    medical device recalls (RES)
      enforcement               device enforcement reports (RES)
      classification            product classification: class, regulation, product code
      510k                      510(k) premarket notifications
      pma                       premarket approval (PMA) submissions
      registrationlisting       establishment registration & device listing
      udi                       GUDID — Unique Device Identification device records
      covid19serology           FDA independent evaluations of SARS‑CoV‑2 serology tests
  cosmetic/
      event                     cosmetic adverse event reports (CFSAN)
  food/
      enforcement               food recalls (RES)
      event                     CAERS adverse event reports for foods & dietary supplements
  animalandveterinary/
      event                     adverse events for animal drugs & devices (CVM)
  tobacco/
      problem                   tobacco product problem reports (CTP)
  other/
      nsde                      legacy drug listing/NDL data (superseded by drug/ndc; backward compatibility)
      substance                 FDA Substance Registration System (SRS) substances
      unii                      Unique Ingredient Identifier (UNII) dictionary
      historicaldocument        FDA historical documents (e.g., press releases)
  transparency/
      crl                       Complete Response Letter (CRL) metadata index
""")
        sys.exit()


def run(args: argparse.Namespace) -> int:
    """Entry-point called by ind.main when `openfda` is selected."""
    if not getattr(args, "openfda_cmd", None):
        # If no subcommand provided, show help and exit non-zero for clarity.
        # We rebuild the parser to print help text.
        parser = argparse.ArgumentParser(prog="ind openfda")
        parser.print_help()
        return 2

    func = getattr(args, "func", None)
    if func is None:
        raise SystemExit("No action bound for openfda command.")

    return int(func(args))
