"""
Examples: Using the ind.pubchem module
======================================

This script demonstrates common PubChem PUG REST API operations
using the `ind.pubchem` package, which provides structured access
through the PubChemClient, endpoints, and pug_fetch() utility.

Requirements:
    pip install ind requests

Documentation:
    https://pubchem.ncbi.nlm.nih.gov/rest/pug
"""

from ind.pubchem.client import PubChemClient
from ind.pubchem.endpoints import (
    get_compound_record,
    get_compound_properties,
    get_synonyms,
    get_ids,
    get_assaysummary,
    fast_search,
)
from ind.pubchem.http import pug_fetch
from pprint import pprint


def example_1_simple_record():
    """Fetch full compound record for aspirin (CID 2244) as JSON."""
    client = PubChemClient()
    resp = get_compound_record(client, "2244", output="JSON", record_type="2d")
    print("CID 2244 summary:")
    pprint(resp.json())


def example_2_property_table():
    """Fetch molecular formula and weight for multiple compounds as CSV."""
    client = PubChemClient()
    resp = get_compound_properties(
        client,
        identifiers="1,2,3,4,5",
        properties="MolecularFormula,MolecularWeight",
        output="CSV",
    )
    print(resp.text[:200], "...")


def example_3_save_sdf():
    """Download SDF record for aspirin and save to file."""
    client = PubChemClient()
    resp = get_compound_record(
        client,
        "2244",
        output="SDF",
        to_file="./results/aspirin.sdf",
    )
    print("File saved to ./results/aspirin.sdf")
    print("HTTP status:", resp.status_code)


def example_4_synonyms():
    """Retrieve synonyms for a compound by name."""
    client = PubChemClient()
    resp = get_synonyms(client, "compound", "name", "aspirin", output="JSON")
    synonyms = resp.json().get("InformationList", {}).get("Information", [{}])[0].get("Synonym", [])
    print(f"Found {len(synonyms)} synonyms for aspirin:")
    for s in synonyms[:10]:
        print("  -", s)


def example_5_interconvert_ids():
    """Convert compound names to CIDs and return as JSON."""
    client = PubChemClient()
    resp = get_ids(
        client,
        domain="compound",
        namespace="name",
        identifiers="glucose",
        id_type="cids",
        output="JSON",
        options={"list_return": "flat"},
    )
    print(resp.json())


def example_6_assay_summary():
    """Retrieve assay summary for compound CID 1000 as CSV."""
    client = PubChemClient()
    resp = get_assaysummary(client, "compound", "cid", "1000", output="CSV")
    print(resp.text.splitlines()[:5])


def example_7_structure_search():
    """Perform a fast substructure search by SMILES."""
    client = PubChemClient()
    resp = fast_search(
        client,
        kind="fastsubstructure",
        by="smiles",
        query="C1=CC=CC=C1",  # benzene ring
        output="JSON",
        options={"MaxRecords": 5},
    )
    print(resp.json())


def example_8_manual_pug_fetch():
    """Use the low-level pug_fetch() for fine control."""
    client = PubChemClient()
    resp = pug_fetch(
        client,
        input_specification="compound/cid/2244",
        operation_specification="property/MolecularFormula,MolecularWeight",
        output_specification="JSON",
        operation_options={"record_type": "2d"},
    )
    print(resp.json())


def main():
    print("=== Example 1: Full Record ===")
    example_1_simple_record()

    print("\n=== Example 2: Property Table ===")
    example_2_property_table()

    print("\n=== Example 3: Save SDF ===")
    example_3_save_sdf()

    print("\n=== Example 4: Synonyms ===")
    example_4_synonyms()

    print("\n=== Example 5: Interconvert IDs ===")
    example_5_interconvert_ids()

    print("\n=== Example 6: Assay Summary ===")
    example_6_assay_summary()

    print("\n=== Example 7: Fast Search ===")
    example_7_structure_search()

    print("\n=== Example 8: Manual PUG Fetch ===")
    example_8_manual_pug_fetch()


if __name__ == "__main__":
    main()