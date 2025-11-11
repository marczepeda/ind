#!/usr/bin/env python3
"""
NCBI Entrez API Examples CLI

Quick demonstrations of the helpers in ind.ncbi.*

Usage examples:
  python ncbi.py esearch
  python ncbi.py esummary
  python ncbi.py fetch-abstracts
  python ncbi.py gene-fasta
  python ncbi.py linked-uids

Notes
-----
These examples require Biopython (`Bio.Entrez`) and an internet connection.

You **must** provide a contact email either through the environment variable
`NCBI_EMAIL` or via command line using `--email`.
"""

import os
import json
import argparse
from ind.ncbi.client import NCBIConfig, EntrezClient
from ind.ncbi import endpoints as ep
from ind.ncbi import workflows as wf
from ind.config import get_info


def get_client(args) -> EntrezClient:
    """Build a client instance using either CLI or environment config."""
    email = args.email or os.getenv("NCBI_EMAIL") or get_info("NCBI_EMAIL")
    api_key = args.api_key or os.getenv("NCBI_API_KEY") or get_info("NCBI_API_KEY")
    if not email:
        raise SystemExit("NCBI requires an email (use --email or set NCBI_EMAIL)")
    cfg = NCBIConfig(email=email, api_key=api_key)
    return EntrezClient(cfg)


def example_esearch(client: EntrezClient) -> None:
    print("=== Example 1: PubMed esearch ===")
    res = ep.esearch(client, db="pubmed", term="cancer immunotherapy", retmax=5)
    print(json.dumps(res, indent=2))


def example_esummary(client: EntrezClient) -> None:
    print("=== Example 2: PubMed esummary ===")
    ids = ["17284678", "37492310"]
    res = ep.esummary(client, db="pubmed", ids=ids)
    print(json.dumps(res, indent=2))


def example_fetch_abstracts(client: EntrezClient) -> None:
    print("=== Example 3: Fetch PubMed abstracts ===")
    pairs = wf.search_then_fetch_abstracts(client, term="cancer AND bevacizumab", limit=3)
    for pmid, text in pairs:
        print(f"\nPMID: {pmid}\n{text}\n{'-'*40}")


def example_linked_uids(client: EntrezClient) -> None:
    print("=== Example 4: Gene→Nucleotide links ===")
    mapping = wf.linked_uids(client, dbfrom="gene", ids=["672"], db="nucleotide", linkname="gene_nuccore")
    print(json.dumps(mapping, indent=2))


def example_gene_fasta(client: EntrezClient) -> None:
    print("=== Example 5: Download FASTA sequences for gene IDs ===")
    res = wf.download_fasta_for_gene_ids(client, ["672"])
    for gid, fasta in res.items():
        print(f"\n> Gene {gid}\n{fasta[:300]}...\n")  # truncate output for readability


def main() -> None:
    parser = argparse.ArgumentParser(description="Run NCBI Entrez examples.")
    parser.add_argument(
        "example",
        choices=["esearch", "esummary", "fetch-abstracts", "linked-uids", "gene-fasta"],
        help="Which example to run.",
    )
    parser.add_argument("--email", help="Contact email (or set NCBI_EMAIL).")
    parser.add_argument("--api-key", help="Optional NCBI API key.")
    args = parser.parse_args()

    client = get_client(args)

    if args.example == "esearch":
        example_esearch(client)
    elif args.example == "esummary":
        example_esummary(client)
    elif args.example == "fetch-abstracts":
        example_fetch_abstracts(client)
    elif args.example == "linked-uids":
        example_linked_uids(client)
    elif args.example == "gene-fasta":
        example_gene_fasta(client)


if __name__ == "__main__":
    main()