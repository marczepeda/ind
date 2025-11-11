from __future__ import annotations
import argparse
import os
import json
import sys
from typing import Any
from rich import print as rprint
from .client import NCBIConfig, EntrezClient
from . import endpoints as ep
from . import workflows as wf

def add_subparser(subparsers: argparse._SubParsersAction, formatter_class: type[argparse.ArgumentDefaultsHelpFormatter]) -> None:
    # Parent config flags (shared)
    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--email", required=False, default=os.getenv("NCBI_EMAIL"),
                       help="Contact email for NCBI (required by policy; set NCBI_EMAIL env var or config).")
        p.add_argument("--api-key", required=False, default=os.getenv("NCBI_API_KEY"),
                       help="NCBI API key for higher rate limits; set NCBI API key (or set NCBI_API_KEY env var or config)")
        p.add_argument("--tool", default="ind-ncbi", help="Tool name sent to NCBI.")
        p.add_argument("--timeout", type=int, default=30, help="Request timeout (s).")

    # NCBI subparser
    ncbi_parser = subparsers.add_parser(
        "ncbi",
        help="Query the NCBI APIs",
        description="Query the NCBI APIs",
        formatter_class=formatter_class
    )
    ncbi_subparsers = ncbi_parser.add_subparsers()

    # esearch
    p_search = ncbi_subparsers.add_parser("esearch", help="E-utilities esearch: searches and retrieves primary IDs (for use in EFetch, ELink, and ESummary) and term translations and optionally retains results for future use in the user's environment.", description="E-utilities esearch: searches and retrieves primary IDs (for use in EFetch, ELink, and ESummary) and term translations and optionally retains results for future use in the user's environment.", formatter_class=formatter_class)
    add_common(p_search)
    p_search.add_argument("db", type=str, help="NCBI db (e.g., pubmed, nucleotide)")
    p_search.add_argument("term", type=str, help="Query term")
    p_search.add_argument("--retmax", type=int, default=20, help="Maximum number of IDs to return")
    p_search.add_argument("--retstart", type=int, default=0, help="Starting point for results")
    p_search.add_argument("--usehistory", dest="usehistory", action="store_true", default=True, help="Store results on NCBI History server (default: True)")
    p_search.add_argument("--no-usehistory", dest="usehistory", action="store_false", help="Disable storing results on History server")
    p_search.add_argument("--sort", default=None, help="Sort order (e.g., 'relevance', 'pub date'; varies by db)")
    p_search.add_argument("--field", default=None, help="Search field within the database (varies by db)")
    p_search.add_argument("--datetype", default=None, help="Type of date to limit by (e.g., 'pdat', 'mdat')")
    p_search.add_argument("--mindate", default=None, help="Minimum date for results (YYYY/MM/DD or YYYY)")
    p_search.add_argument("--maxdate", default=None, help="Maximum date for results (YYYY/MM/DD or YYYY)")
    p_search.add_argument("--webenv", default=None, help="WebEnv string from previous ESearch/EPost/ELink; requires --usehistory")
    p_search.add_argument("--query-key", dest="query_key", default=None, help="Query key integer from previous History use; requires --webenv and --usehistory")
    p_search.add_argument("--rettype", default=None, choices=["uilist", "count"], help="Return type: 'uilist' (default XML) or 'count'")
    p_search.add_argument("--retmode", default="xml", choices=["xml", "json"], help="Return mode: 'xml' (default) or 'json'")
    p_search.add_argument("--idtype", default=None, help="Identifier type for sequence DBs (e.g., 'acc')")
    p_search.add_argument("--reldate", type=int, default=None, help="Limit by relative date in days (requires --datetype)")
    p_search.set_defaults(func=_cmd_esearch)

    # esummary
    p_summary = ncbi_subparsers.add_parser("esummary", help="E-utilities esummary: retrieves document summaries from a list of primary IDs or from the user's environment.", description="E-utilities esummary: retrieves document summaries from a list of primary IDs or from the user's environment.", formatter_class=formatter_class)
    add_common(p_summary)
    p_summary.add_argument("db", type=str, help="Database to query")
    p_summary.add_argument("--ids", nargs="+", default=[], help="List of IDs to summarize")
    p_summary.add_argument("--webenv", default=None, help="NCBI History WebEnv token (from esearch/usehistory)")
    p_summary.add_argument("--query-key", dest="query_key", default=None, help="NCBI History query_key (from esearch/usehistory)")
    p_summary.add_argument("--retstart", type=int, default=0, help="Sequential index of first DocSum to retrieve")
    p_summary.add_argument("--retmax", type=int, default=None, help="Number of DocSums to retrieve (max 10000)")
    p_summary.add_argument("--retmode", default="xml", choices=["xml", "json"], help="Return mode for esummary")
    p_summary.add_argument("--version", default=None, help="ESummary XML version (e.g., '2.0')")
    p_summary.set_defaults(func=_cmd_esummary)

    # efetch
    p_fetch = ncbi_subparsers.add_parser("efetch", help="E-utilities efetch: retrieves records in the requested format from a list of one or more primary IDs or from the user's environment.", description="E-utilities efetch: retrieves records in the requested format from a list of one or more primary IDs or from the user's environment.", formatter_class=formatter_class)
    add_common(p_fetch)
    p_fetch.add_argument("db", type=str, help="Database to fetch from")
    p_fetch.add_argument("--ids", nargs="+", default=[], help="List of IDs to retrieve")
    p_fetch.add_argument("--rettype", default=None, help="Data type to return (e.g., gb, fasta)")
    p_fetch.add_argument("--retmode", default="xml", choices=["xml", "text", "html"], help="Format of the output (e.g., text, xml, html)")
    p_fetch.add_argument("--retstart", type=int, default=0, help="Sequential index of the first record to retrieve")
    p_fetch.add_argument("--retmax", type=int, default=None, help="Total number of records to retrieve (max 10000)")
    # Sequence database options
    p_fetch.add_argument("--strand", type=int, choices=[1, 2], default=None, help="DNA strand: 1 (plus) or 2 (minus)")
    p_fetch.add_argument("--seq-start", dest="seq_start", type=int, default=None, help="First sequence base to retrieve (1-based)")
    p_fetch.add_argument("--seq-stop", dest="seq_stop", type=int, default=None, help="Last sequence base to retrieve (1-based)")
    p_fetch.add_argument("--complexity", type=int, choices=[0,1,2,3,4], default=None, help="Sequence data content (0..4)")
    p_fetch.add_argument("--webenv", default=None, help="NCBI History WebEnv token (from esearch/usehistory)")
    p_fetch.add_argument("--query-key", dest="query_key", default=None, help="NCBI History query_key (from esearch/usehistory)")
    p_fetch.set_defaults(func=_cmd_efetch)

    # einfo
    p_info = ncbi_subparsers.add_parser("einfo", help="E-utilities einfo: provides field index term counts, last update, and available links for each database.", description="E-utilities einfo: provides field index term counts, last update, and available links for each database.", formatter_class=formatter_class)
    add_common(p_info)
    p_info.add_argument("--db", type=str, default=None, help="Database name to query")
    p_info.add_argument("--version", default=None, help="EInfo XML version (e.g., '2.0')")
    p_info.add_argument("--retmode", default="xml", choices=["xml", "json"], help="Return mode for einfo")
    p_info.set_defaults(func=_cmd_einfo)

    # elink
    p_link = ncbi_subparsers.add_parser("elink", help="E-utilities elink: checks for the existence of an external or Related Articles link from a list of one or more primary IDs.  Retrieves primary IDs and relevancy scores for links to Entrez databases or Related Articles;  creates a hyperlink to the primary LinkOut provider for a specific ID and database, or lists LinkOut URLs and Attributes for multiple IDs.", description="E-utilities elink: checks for the existence of an external or Related Articles link from a list of one or more primary IDs.  Retrieves primary IDs and relevancy scores for links to Entrez databases or Related Articles;  creates a hyperlink to the primary LinkOut provider for a specific ID and database, or lists LinkOut URLs and Attributes for multiple IDs.", formatter_class=formatter_class)
    add_common(p_link)
    p_link.add_argument("dbfrom", type=str, help="Source database")
    p_link.add_argument("--db", type=str, default=None, help="Target database")
    p_link.add_argument("--ids", nargs="+", default=[], help="List of IDs to link from")
    p_link.add_argument("--linkname", default=None, help="Specific link name for database relationships (e.g., pubmed_pubmed)")
    p_link.add_argument(
        "--cmd",
        default="neighbor",
        choices=["neighbor","neighbor_score","neighbor_history","acheck","ncheck","lcheck","llinks","llinkslib","prlinks"],
        help="ELink command mode"
    )
    p_link.add_argument("--term", default=None, help="Entrez query to filter linked UIDs (only when db==dbfrom)")
    p_link.add_argument("--holding", default=None, help="LinkOut provider abbreviation (llinks/llinkslib only)")
    p_link.add_argument("--datetype", default=None, help="Date type for limiting (PubMed only; neighbor/neighbor_history)")
    p_link.add_argument("--reldate", type=int, default=None, help="Relative date in days (PubMed only; neighbor/neighbor_history)")
    p_link.add_argument("--mindate", default=None, help="Minimum date (YYYY/MM/DD or YYYY/MM or YYYY)")
    p_link.add_argument("--maxdate", default=None, help="Maximum date (YYYY/MM/DD or YYYY/MM or YYYY)")
    p_link.add_argument("--idtype", default=None, help="Identifier type for sequence DBs (e.g., 'acc')")
    p_link.add_argument("--retmode", default="xml", choices=["xml","json","ref","text","html"], help="Return mode")
    p_link.set_defaults(func=_cmd_elink)

    # egquery
    p_gq = ncbi_subparsers.add_parser("egquery", help="E-utilities egquery (Global Query counts)", description="E-utilities egquery (Global Query counts)", formatter_class=formatter_class)
    add_common(p_gq)
    p_gq.add_argument("term", help="Search term for global query")
    p_gq.set_defaults(func=_cmd_egquery)

    # espell
    p_sp = ncbi_subparsers.add_parser("espell", help="E-utilities espell (spelling suggestions)", description="E-utilities espell (spelling suggestions)", formatter_class=formatter_class)
    add_common(p_sp)
    p_sp.add_argument("db", help="Database to query (e.g., pubmed)")
    p_sp.add_argument("term", help="Query term to check spelling")
    p_sp.set_defaults(func=_cmd_espell)

    # ecitmatch
    p_cm = ncbi_subparsers.add_parser("ecitmatch", help="E-utilities ecitmatch (match citations → PMIDs)", description="E-utilities ecitmatch (match citations → PMIDs)", formatter_class=formatter_class)
    add_common(p_cm)
    p_cm.add_argument("--bdata", help="Pipe-delimited citation lines per NCBI spec")
    p_cm.add_argument("--bdata-file", help="Path to file containing bdata lines")
    p_cm.add_argument("--retmode", default="xml", choices=["xml", "text"], help="Return mode for ecitmatch")
    p_cm.set_defaults(func=_cmd_ecitmatch)

    # search+fetch-abstracts
    p_sf = ncbi_subparsers.add_parser("search-abstracts", help="Search PubMed and fetch abstracts", description="Search PubMed and fetch abstracts", formatter_class=formatter_class)
    add_common(p_sf)
    p_sf.add_argument("term", help="Query term")
    p_sf.add_argument("--limit", type=int, default=50, help="Max records to fetch")
    p_sf.set_defaults(func=_cmd_search_abstracts)

    # gene->nuccore fasta
    p_gf = ncbi_subparsers.add_parser("gene-fasta", help="Download FASTA for Gene IDs via elink→efetch", description="Download FASTA for Gene IDs via elink→efetch", formatter_class=formatter_class)
    add_common(p_gf)
    p_gf.add_argument("--gene-ids", nargs="+", required=True, help="List of Gene IDs to retrieve FASTA for")
    p_gf.set_defaults(func=_cmd_gene_fasta)

    # Help message for ind ncbi query/count -h block text by Myformatter(RichHelpformatter_class):
    if any(["ind" in argv for argv in sys.argv]) and "ncbi" in sys.argv and any(["esearch" in sys.argv or "esummary" in sys.argv or "efetch" in sys.argv or "einfo" in sys.argv or "elink" in sys.argv or "espell" in sys.argv]) and ("--help" in sys.argv or "-h" in sys.argv):
        if "esearch" in sys.argv:
            p_search.print_help()
        if "esummary" in sys.argv:
            p_summary.print_help()
        if "efetch" in sys.argv:
            p_fetch.print_help()
        if "einfo" in sys.argv:
            p_info.print_help()
        if "elink" in sys.argv:
            p_link.print_help()
        if "espell" in sys.argv:
            p_sp.print_help()
        
        rprint(
'''
[red]Details:[/red]
  [cyan]db[/cyan]                   [blue]NCBI Databases: 'pubmed', 'protein', 'nuccore', 'ipg', 'nucleotide', 'structure', 
                      'genome', 'annotinfo', 'assembly', 'bioproject', 'biosample','blastdbinfo', 'books', 
                      'cdd', 'clinvar', 'gap', 'gapplus', 'grasp', 'dbvar', 'gene', 'gds', 'geoprofiles', 
                      'medgen', 'mesh', 'nlmcatalog', 'omim', 'orgtrack', 'pmc', 'popset', 'proteinclusters', 
                      'pcassay', 'protfam', 'pccompound', 'pcsubstance', 'seqannot', 'snp', 'sra', 'taxonomy', 
                      'biocollections', and 'gtr'[/blue]
''')
        sys.exit()



def _build_client(args) -> EntrezClient:
    if not args.email:
        raise SystemExit("NCBI requires a contact email. Provide --email or set NCBI_EMAIL.")
    cfg = NCBIConfig(email=args.email, api_key=args.api_key, tool=args.tool, timeout=args.timeout)
    return EntrezClient(cfg)

def _print(obj: Any) -> None:
    if isinstance(obj, str):
        print(obj)
    else:
        print(json.dumps(obj, indent=2, sort_keys=False))

def _cmd_esearch(args) -> None:
    client = _build_client(args)
    res = ep.esearch(
        client,
        db=args.db,
        term=args.term,
        retmax=args.retmax,
        retstart=args.retstart,
        usehistory=args.usehistory,
        sort=args.sort,
        field=args.field,
        datetype=args.datetype,
        mindate=args.mindate,
        maxdate=args.maxdate,
        webenv=args.webenv,
        query_key=args.query_key,
        rettype=args.rettype,
        retmode=args.retmode,
        idtype=args.idtype,
        reldate=args.reldate,
    )
    _print(res)

def _cmd_esummary(args) -> None:
    client = _build_client(args)
    res = ep.esummary(
        client,
        db=args.db,
        ids=args.ids,
        webenv=args.webenv,
        query_key=args.query_key,
        retstart=args.retstart,
        retmax=args.retmax,
        retmode=args.retmode,
        version=args.version,
    )
    _print(res)

def _cmd_efetch(args) -> None:
    client = _build_client(args)
    res = ep.efetch(
        client,
        db=args.db,
        ids=args.ids,
        rettype=args.rettype,
        retmode=args.retmode,
        webenv=args.webenv,
        query_key=args.query_key,
        retstart=args.retstart,
        retmax=args.retmax,
        strand=args.strand,
        seq_start=args.seq_start,
        seq_stop=args.seq_stop,
        complexity=args.complexity,
    )
    _print(res)

def _cmd_einfo(args) -> None:
    client = _build_client(args)
    res = ep.einfo(client, db=args.db, version=args.version, retmode=args.retmode)
    _print(res)

def _cmd_elink(args) -> None:
    client = _build_client(args)
    res = ep.elink(
        client,
        dbfrom=args.dbfrom,
        db=args.db,
        ids=args.ids,
        linkname=args.linkname,
        cmd=args.cmd,
        webenv=args.webenv if hasattr(args, "webenv") else None,
        query_key=args.query_key if hasattr(args, "query_key") else None,
        term=args.term,
        holding=args.holding,
        datetype=args.datetype,
        reldate=args.reldate,
        mindate=args.mindate,
        maxdate=args.maxdate,
        idtype=args.idtype,
        retmode=args.retmode,
    )
    _print(res)

def _cmd_egquery(args) -> None:
    client = _build_client(args)
    res = ep.egquery(client, term=args.term)
    _print(res)

def _cmd_espell(args) -> None:
    client = _build_client(args)
    res = ep.espell(client, db=args.db, term=args.term)
    _print(res)

def _cmd_ecitmatch(args) -> None:
    client = _build_client(args)
    if not args.bdata and not args.bdata_file:
        raise SystemExit("Provide --bdata or --bdata-file for ecitmatch")
    bdata = args.bdata
    if args.bdata_file:
        with open(args.bdata_file, "r", encoding="utf-8") as fh:
            bdata = fh.read()
    res = ep.ecitmatch(client, bdata=bdata, retmode=args.retmode)
    _print(res)

def _cmd_search_abstracts(args):
    client = _build_client(args)
    pairs = wf.search_then_fetch_abstracts(client, term=args.term, limit=args.limit)
    # Print as a simple JSON list of {pmid, abstract}
    print(json.dumps([{"pmid": p, "abstract": a} for p, a in pairs], indent=2))

def _cmd_gene_fasta(args):
    client = _build_client(args)
    res = wf.download_fasta_for_gene_ids(client, args.gene_ids)
    # Print a mapping {gene_id: fasta_text}
    print(json.dumps(res, indent=2))