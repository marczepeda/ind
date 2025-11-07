from __future__ import annotations

import json
from typing import Any

from rich import print as rprint

from . import (
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

def _print_json(obj: Any) -> None:
    rprint(json.dumps(obj, indent=2))

def add_subparser(subparsers, Formatter):
    ct = subparsers.add_parser(
        "trials",
        help="ClinicalTrials.gov API",
        description="ClinicalTrials.gov API",
        formatter_class=Formatter,
    )
    ct_sub = ct.add_subparsers(dest="ct_cmd", required=True)

    # /studies
    p_list = ct_sub.add_parser("studies", help="List studies", description="List studies", formatter_class=Formatter)
    # query.* (Essie)
    p_list.add_argument("--q-cond", help="query.cond")
    p_list.add_argument("--q-term", help="query.term")
    p_list.add_argument("--q-locn", help="query.locn")
    p_list.add_argument("--q-titles", help="query.titles")
    p_list.add_argument("--q-intr", help="query.intr")
    p_list.add_argument("--q-outc", help="query.outc")
    p_list.add_argument("--q-spons", help="query.spons")
    p_list.add_argument("--q-lead", help="query.lead")
    p_list.add_argument("--q-id", help="query.id")
    p_list.add_argument("--q-patient", help="query.patient")
    # filter.* (common)
    p_list.add_argument("--filter-overall-status", nargs="*")
    p_list.add_argument("--filter-geo")
    p_list.add_argument("--filter-ids", nargs="*")
    p_list.add_argument("--filter-advanced")
    # projection / sort / paging
    p_list.add_argument("--fields", nargs="*", default=["NCTId", "BriefTitle", "OverallStatus"])
    p_list.add_argument("--sort", nargs="*")
    p_list.add_argument("--count-total", action="store_true")
    p_list.add_argument("--page-size", type=int, default=50)
    p_list.add_argument("--paginate", action="store_true")
    p_list.add_argument("--next-page-size", type=int, default=100)
    p_list.add_argument("--max-pages", type=int)
    p_list.add_argument("--timeout", type=float, default=20.0)
    p_list.add_argument("--rate", type=float, default=2.0)

    # /studies/{nctId}
    p_one = ct_sub.add_parser("study", help="Get single study by NCT ID", description="Get single study by NCT ID", formatter_class=Formatter)
    p_one.add_argument("nct_id")
    p_one.add_argument("--format", default="json", choices=["json", "fhir.json"])
    p_one.add_argument("--fields", nargs="*")
    p_one.add_argument("--markup-format", default="markdown", choices=["markdown", "legacy"])
    p_one.add_argument("--timeout", type=float, default=20.0)
    p_one.add_argument("--rate", type=float, default=2.0)

    # metadata, enums, search-areas
    p_meta = ct_sub.add_parser("metadata", help="Get studies metadata", description="Get studies metadata", formatter_class=Formatter)
    p_meta.add_argument("--indexed-only", action="store_true")
    p_meta.add_argument("--historic-only", action="store_true")
    p_meta.add_argument("--timeout", type=float, default=20.0)
    p_meta.add_argument("--rate", type=float, default=2.0)

    ct_sub.add_parser("enums", help="Get enums", description="Get enums", formatter_class=Formatter).add_argument("--timeout", type=float, default=20.0)
    ct_sub.add_parser("search-areas", help="Get search areas", description="Get search areas", formatter_class=Formatter).add_argument("--timeout", type=float, default=20.0)

    # stats
    ct_sub.add_parser("size", help="Study JSON size stats", description="Study JSON size stats", formatter_class=Formatter).add_argument("--timeout", type=float, default=20.0)

    p_vals = ct_sub.add_parser("field-values", help="Value stats for leaf fields", description="Value stats for leaf fields", formatter_class=Formatter)
    p_vals.add_argument("--fields", nargs="*")
    p_vals.add_argument("--types", nargs="*", choices=["ENUM", "STRING", "DATE", "INTEGER", "NUMBER", "BOOLEAN"])
    p_vals.add_argument("--limit", type=int, default=15)
    p_vals.add_argument("--timeout", type=float, default=20.0)

    p_fs = ct_sub.add_parser("field-sizes", help="Size stats for list/array fields", description="Size stats for list/array fields", formatter_class=Formatter)
    p_fs.add_argument("--fields", nargs="*")
    p_fs.add_argument("--limit", type=int, default=15)
    p_fs.add_argument("--timeout", type=float, default=20.0)

    ct.set_defaults(func=run)

def run(args) -> int:
    client = ClinicalTrialsClient(
        timeout=getattr(args, "timeout", 20.0),
        rate_limit_per_sec=getattr(args, "rate", 2.0),
    )
    try:
        if args.ct_cmd == "studies":
            if getattr(args, "paginate", False):
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
                    first_page_size=args.page_size,
                    next_page_size=args.next_page_size,
                    max_pages=args.max_pages,
                    include_total_on_first_page=args.count_total,
                )
                _print_json({"pages": pages})
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
                    page_size=args.page_size,
                )
                _print_json(res)

        elif args.ct_cmd == "study":
            res = get_study(
                client,
                args.nct_id,
                format=args.format,
                fields=args.fields if args.format == "json" else None,
                markup_format=args.markup_format if args.format == "json" else "markdown",
            )
            _print_json(res)

        elif args.ct_cmd == "metadata":
            res = get_studies_metadata(
                client,
                include_indexed_only=getattr(args, "indexed_only", False),
                include_historic_only=getattr(args, "historic_only", False),
            )
            _print_json(res)

        elif args.ct_cmd == "enums":
            _print_json(get_enums(client))

        elif args.ct_cmd == "search-areas":
            _print_json(get_search_areas(client))

        elif args.ct_cmd == "size":
            _print_json(get_study_sizes(client))

        elif args.ct_cmd == "field-values":
            _print_json(get_field_values(client, fields=args.fields, types=args.types))

        elif args.ct_cmd == "field-sizes":
            _print_json(get_field_sizes(client, fields=args.fields))

        else:
            raise ClinicalTrialsError(f"Unknown clinical_trials command: {args.ct_cmd}")

    except ClinicalTrialsError as e:
        rprint(f"[bold red]ERROR[/bold red] {e}")
        return 2
    return 0