#!/usr/bin/env python3
"""
ClinicalTrials.gov API demo for the ind package.

Quick tours:
  1) List studies and preview a few rows (optionally filtered by query.* / filter.*).
  2) Fetch a single study by NCT ID (from --nct-id).
  3) Explore metadata / enums / search-areas.
  4) Hit stats endpoints: size, field-values, field-sizes.

Run:
  python examples/clinical_trials/clinical_trials.py studies --q-cond "diabetes" --filter-overall-status RECRUITING --limit 5 --paginate
  python examples/clinical_trials/clinical_trials.py studies --q-term "AREA[LastUpdatePostDate]RANGE[2024-01-01,MAX]" --limit 3
  python examples/clinical_trials/clinical_trials.py study --nct-id NCT03888612
  python examples/clinical_trials/clinical_trials.py metadata
  python examples/clinical_trials/clinical_trials.py enums
  python examples/clinical_trials/clinical_trials.py size
  python examples/clinical_trials/clinical_trials.py search-areas
  python examples/clinical_trials/clinical_trials.py field-values --fields OverallStatus Phase --types ENUM --limit 10
  python examples/clinical_trials/clinical_trials.py field-sizes --fields protocolSection.armsInterventionsModule.armGroups.interventionNames --limit 10
"""

from __future__ import annotations

import argparse
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from ind.clinical_trials import (
    ClinicalTrialsClient,
    ClinicalTrialsError,
    list_studies,
    iterate_studies,
    get_study,
    get_studies_metadata,
    get_search_areas,
    get_enums,
    get_study_sizes,
    get_field_values,
    get_field_sizes,
)

console = Console()

# ------------------------------- helpers ------------------------------------


def pretty_json(obj: Any) -> None:
    console.print_json(data=obj)


def pluck_nct_id(study: Dict[str, Any]) -> Optional[str]:
    try:
        return study["protocolSection"]["identificationModule"]["nctId"]
    except Exception:
        return None


def render_studies_table(studies: List[Dict[str, Any]], max_rows: int = 5) -> None:
    table = Table(title="Studies (preview)", box=box.SIMPLE_HEAVY)
    table.add_column("NCTId", no_wrap=True)
    table.add_column("BriefTitle")
    table.add_column("OverallStatus", no_wrap=True)

    count = 0
    for s in studies:
        nct = pluck_nct_id(s) or "-"
        # Titles/status fields are nested; try common locations.
        title = (
            s.get("protocolSection", {})
             .get("identificationModule", {})
             .get("briefTitle")
            or s.get("briefTitle")
            or "-"
        )
        status = (
            s.get("protocolSection", {})
             .get("statusModule", {})
             .get("overallStatus")
            or s.get("overallStatus")
            or "-"
        )
        table.add_row(nct, title, status)
        count += 1
        if count >= max_rows:
            break

    console.print(table)


# --------------------------------- CLI --------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ClinicalTrials.gov demo (ind package)")
    sub = p.add_subparsers(dest="cmd", required=True)

    # studies
    p_list = sub.add_parser("studies", help="List studies with query/filter and optional pagination")
    # query.* (Essie)
    p_list.add_argument("--q-cond", help="query.cond (ConditionSearch area)")
    p_list.add_argument("--q-term", help="query.term (BasicSearch area)")
    p_list.add_argument("--q-locn", help="query.locn (LocationSearch area)")
    p_list.add_argument("--q-titles", help="query.titles (TitleSearch area)")
    p_list.add_argument("--q-intr", help="query.intr (InterventionSearch area)")
    p_list.add_argument("--q-outc", help="query.outc (OutcomeSearch area)")
    p_list.add_argument("--q-spons", help="query.spons")
    p_list.add_argument("--q-lead", help="query.lead (LeadSponsorName)")
    p_list.add_argument("--q-id", help="query.id (NCT or alias, Essie)")
    p_list.add_argument("--q-patient", help="query.patient")
    # filter.* (commonly used)
    p_list.add_argument("--filter-overall-status", nargs="*", help="Filter by overallStatus values")
    p_list.add_argument("--filter-geo", help='Geo distance, e.g. distance(39.0036,-77.1013,50mi)')
    p_list.add_argument("--filter-ids", nargs="*", help="Filter by NCT IDs")
    p_list.add_argument("--filter-advanced", help="Essie expression for filter.advanced")
    # projection/sort/paging
    p_list.add_argument("--fields", nargs="*", default=["NCTId", "BriefTitle", "OverallStatus"], help="Projection fields")
    p_list.add_argument("--sort", nargs="*", help="Up to 2 sort items, e.g. @relevance LastUpdatePostDate:desc")
    p_list.add_argument("--count-total", action="store_true", help="Return totalCount on first page")
    p_list.add_argument("--limit", type=int, default=5, help="Preview N rows in the table")
    p_list.add_argument("--first-page-size", type=int, default=50)
    p_list.add_argument("--paginate", action="store_true", help="Follow nextPageToken")
    p_list.add_argument("--next-page-size", type=int, default=100, help="Page size for subsequent pages")
    p_list.add_argument("--max-pages", type=int, help="Max number of pages when paginating")

    # single study
    p_study = sub.add_parser("study", help="Fetch a single study by NCT ID")
    p_study.add_argument("--nct-id", required=True)
    p_study.add_argument("--format", default="json", choices=["json", "fhir.json"])
    p_study.add_argument("--fields", nargs="*")  # only for json
    p_study.add_argument("--markup-format", default="markdown", choices=["markdown", "legacy"])

    # metadata/enums/search-areas
    p_meta = sub.add_parser("metadata", help="Show studies metadata")
    p_meta.add_argument("--indexed-only", action="store_true")
    p_meta.add_argument("--historic-only", action="store_true")
    sub.add_parser("enums", help="Show enums")
    sub.add_parser("search-areas", help="Show search areas")

    # stats
    p_size = sub.add_parser("size", help="Show statistics of study JSON sizes")

    p_vals = sub.add_parser("field-values", help="Value statistics for leaf fields")
    p_vals.add_argument("--fields", nargs="*", help="Pieces or field paths")
    p_vals.add_argument("--types", nargs="*", choices=["ENUM", "STRING", "DATE", "INTEGER", "NUMBER", "BOOLEAN"])
    p_vals.add_argument("--limit", type=int, default=15)

    p_fs = sub.add_parser("field-sizes", help="Size statistics for list/array fields")
    p_fs.add_argument("--fields", nargs="*", help="Pieces or field paths")
    p_fs.add_argument("--limit", type=int, default=15)

    # connection options
    for sp in (p_list, p_study, p_size, p_vals, p_fs):
        sp.add_argument("--timeout", type=float, default=20.0)
        sp.add_argument("--rate", type=float, default=2.0, help="req/sec (float)")

    return p


# --------------------------------- main -------------------------------------


def main() -> None:
    args = build_parser().parse_args()
    client = ClinicalTrialsClient(
        timeout=args.__dict__.get("timeout", 20.0),
        rate_limit_per_sec=args.__dict__.get("rate", 2.0),
    )

    try:
        if args.cmd == "studies":
            # decide single page vs pagination
            if args.paginate:
                pages = iterate_studies(
                    client,
                    query_cond=args.q_cond,
                    query_term=args.q_term,
                    query_locn=args.q_locn,
                    query_titles=args.q_titles,
                    query_intr=args.q_intr,
                    query_outc=args.q_outc,
                    query_spons=args.q_spons,
                    query_lead=args.q_lead,
                    query_id=args.q_id,
                    query_patient=args.q_patient,
                    filter_overall_status=args.filter_overall_status,
                    filter_geo=args.filter_geo,
                    filter_ids=args.filter_ids,
                    filter_advanced=args.filter_advanced,
                    fields=args.fields,
                    sort=args.sort,
                    first_page_size=args.first_page_size,
                    next_page_size=args.next_page_size,
                    max_pages=args.max_pages,
                    include_total_on_first_page=args.count_total,
                )
                total = sum(len(p.get("studies", [])) for p in pages)
                header = f"Fetched {len(pages)} page(s), {total} studies total across pages."
                console.print(Panel.fit(header, style="bold cyan"))
                if pages and pages[0].get("studies"):
                    render_studies_table(pages[0]["studies"], max_rows=args.limit)
                else:
                    console.print("[yellow]No studies returned.[/yellow]")
            else:
                res = list_studies(
                    client,
                    query_cond=args.q_cond,
                    query_term=args.q_term,
                    query_locn=args.q_locn,
                    query_titles=args.q_titles,
                    query_intr=args.q_intr,
                    query_outc=args.q_outc,
                    query_spons=args.q_spons,
                    query_lead=args.q_lead,
                    query_id=args.q_id,
                    query_patient=args.q_patient,
                    filter_overall_status=args.filter_overall_status,
                    filter_geo=args.filter_geo,
                    filter_ids=args.filter_ids,
                    filter_advanced=args.filter_advanced,
                    fields=args.fields,
                    sort=args.sort,
                    count_total=args.count_total,
                    page_size=args.first_page_size,
                )
                studies = res.get("studies", [])
                total_count = res.get("totalCount", None)
                header = f"Found {total_count if total_count is not None else len(studies)} studies (showing up to {args.limit})"
                console.print(Panel.fit(header, style="bold cyan"))
                if studies:
                    render_studies_table(studies, max_rows=args.limit)
                else:
                    console.print("[yellow]No studies returned.[/yellow]")

        elif args.cmd == "study":
            res = get_study(
                client,
                args.nct_id,
                format=args.format,
                fields=args.fields if args.format == "json" else None,
                markup_format=args.markup_format if args.format == "json" else "markdown",
            )
            console.print(Panel.fit(f"Study: {args.nct_id} ({args.format})", style="bold green"))
            pretty_json(res)

        elif args.cmd == "metadata":
            res = get_studies_metadata(
                client,
                include_indexed_only=args.indexed_only,
                include_historic_only=args.historic_only,
            )
            console.print(Panel.fit("Studies Metadata (truncated)", style="bold magenta"))
            # Show top-level keys only to keep console readable
            if isinstance(res, dict):
                pretty_json({k: res.get(k) for k in list(res.keys())[:6]})
            else:
                pretty_json(res)

        elif args.cmd == "enums":
            res = get_enums(client)
            console.print(Panel.fit("Enums (truncated)", style="bold magenta"))
            if isinstance(res, dict):
                pretty_json({k: res.get(k) for k in list(res.keys())[:6]})
            else:
                # Many APIs return a list here
                pretty_json(res[:10] if isinstance(res, list) else res)

        elif args.cmd == "search-areas":
            res = get_search_areas(client)
            console.print(Panel.fit("Search Areas", style="bold magenta"))
            pretty_json(res)

        elif args.cmd == "size":
            res = get_study_sizes(client)
            console.print(Panel.fit("Study JSON Sizes", style="bold green"))
            pretty_json(res)

        elif args.cmd == "field-values":
            res = get_field_values(client, fields=args.fields, types=args.types)
            console.print(Panel.fit("Field Values", style="bold green"))
            if isinstance(res, list) and args.limit:
                pretty_json(res[: args.limit])
            else:
                pretty_json(res)

        elif args.cmd == "field-sizes":
            res = get_field_sizes(client, fields=args.fields)
            console.print(Panel.fit("Field Sizes", style="bold green"))
            if isinstance(res, list) and args.limit:
                pretty_json(res[: args.limit])
            else:
                pretty_json(res)

        else:
            console.print(f"[red]Unknown command: {args.cmd}[/red]")

    except ClinicalTrialsError as e:
        console.print(f"[bold red]ERROR[/bold red] {e}")


if __name__ == "__main__":
    main()