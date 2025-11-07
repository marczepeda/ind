"""
All OpenFDA endpoint examples for the ind.openfda package.

Run examples with:
    python examples/openfda/all_endpoints_demo.py            # anonymous
    python examples/openfda/all_endpoints_demo.py YOUR_KEY   # positional API key
    python examples/openfda/all_endpoints_demo.py --count    # use facet count queries instead of search

Or set env var:
    export OPENFDA_API_KEY=your-key
"""

from __future__ import annotations
import os
import sys
import argparse
from pprint import pprint
from typing import Any

import requests
from ind.openfda.client import OpenFDAClient


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Demonstrate all OpenFDA endpoints.")
    p.add_argument("api_key", nargs="?", default=None, help="Optional API key (positional)")
    p.add_argument("--count", action="store_true", help="Use count/facet queries instead of search.")
    return p.parse_args(argv or sys.argv[1:])


def run(label: str, fn) -> None:
    print(f"\n— {label} —")
    try:
        res = fn()
        if hasattr(res, "results"):
            payload = res.results
        else:
            payload = res
        pprint(payload[:1] if isinstance(payload, list) else payload)
    except requests.exceptions.HTTPError as e:
        print(f"[skip] HTTPError: {e}")
    except Exception as e:
        print(f"[skip] {type(e).__name__}: {e}")


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(argv)
    api_key = ns.api_key or os.getenv("OPENFDA_API_KEY")
    client = OpenFDAClient(api_key=api_key)

    use_count = ns.count
    print(f"Using API key: {'yes' if api_key else 'no'}  |  Using count mode: {use_count}")

    from ind.openfda import drug, animal_veterinary as av, device, food, cosmetic, tobacco, other, transparency

    def maybe_count(path: str, field: str):
        if use_count:
            return client.request_json("GET", f"/{path}.json", params={"count": f"{field}.exact", "limit": 1})

    # DRUG
    print("\n=== DRUG ===")
    run("drug/event", lambda: maybe_count("drug/event", "patient.reaction.reactionmeddrapt") or drug.search_events(client, search='patient.reaction.reactionmeddrapt:"HEADACHE"', limit=1))
    run("drug/label", lambda: maybe_count("drug/label", "openfda.brand_name") or drug.search_labels(client, search='openfda.brand_name:"ADVIL"', limit=1))
    run("drug/ndc", lambda: maybe_count("drug/ndc", "product_type") or drug.search_ndc(client, search='product_type:"HUMAN OTC DRUG"', limit=1))
    run("drug/enforcement", lambda: maybe_count("drug/enforcement", "classification") or drug.search_enforcements(client, search='classification:"Class II"', limit=1))
    run("drug/drugsfda", lambda: maybe_count("drug/drugsfda", "openfda.brand_name") or drug.search_drugsfda(client, search='openfda.brand_name:"LIPITOR"', limit=1))

    # ANIMAL & VETERINARY
    print("\n=== ANIMAL & VETERINARY ===")
    run("animalandveterinary/event", lambda: maybe_count("animalandveterinary/event", "reaction") or av.search_events(client, search='reaction.veddra_term_name:"Vomiting"', limit=1))

    # DEVICE
    print("\n=== DEVICE ===")
    run("device/510k", lambda: maybe_count("device/510k", "advisory_committee") or device.search_510k_by_k_number(client, "K102041", limit=1))
    run("device/classification", lambda: maybe_count("device/classification", "device_class") or device.search_classification_by_product_code(client, "ITX", limit=1))
    run("device/pma", lambda: maybe_count("device/pma", "advisory_committee") or client.request_json("GET", "/device/pma.json", params={"search": 'advisory_committee:"RA"', "limit": 1}))
    run("device/event", lambda: maybe_count("device/event", "event_type") or device.search_device_events_by_event_type(client, "Injury", limit=1))
    run("device/recall", lambda: maybe_count("device/recall", "status") or client.request_json("GET", "/device/recall.json", params={"search": "openfda.regulation_number:880.5200", "limit": 1}))
    run("device/enforcement", lambda: maybe_count("device/enforcement", "classification") or device.search_enforcements(client, search='classification:"Class II"', limit=1))
    run("device/registrationlisting", lambda: maybe_count("device/registrationlisting", "establishment_type") or device.search_registrationlisting_by_establishment_type(client, "Manufacturer", limit=1))
    run("device/covid19serology", lambda: maybe_count("device/covid19serology", "manufacturer") or device.search_covid19serology_by_manufacturer(client, "Abbott", limit=1))
    run("device/udi", lambda: maybe_count("device/udi", "product_codes") or client.request_json("GET", "/device/udi.json", params={"limit": 1}))

    # FOOD
    print("\n=== FOOD ===")
    run("food/enforcement", lambda: maybe_count("food/enforcement", "classification") or food.search_enforcements(client, search='classification:"Class I"', limit=1))
    run("food/event", lambda: maybe_count("food/event", "reactions") or food.search_food_events_by_reaction(client, "DIARRHOEA", limit=1))

    # COSMETIC
    print("\n=== COSMETIC ===")
    run("cosmetic/event", lambda: maybe_count("cosmetic/event", "reactions") or cosmetic.search_events(client, search='reactions:"RASH"', limit=1))

    # TOBACCO
    print("\n=== TOBACCO ===")
    run("tobacco/problem", lambda: maybe_count("tobacco/problem", "tobacco_products") or tobacco.search_problems(client, search='tobacco_products:"CIGARETTE"', limit=1))

    # OTHER
    print("\n=== OTHER ===")
    run("other/historicaldocument", lambda: maybe_count("other/historicaldocument", "doc_type") or other.search_historicaldocument_by_doc_type(client, "pr", limit=1))
    run("other/nsde", lambda: maybe_count("other/nsde", "product_type") or client.request_json("GET", "/other/nsde.json", params={"limit": 1}))
    run("other/substance", lambda: maybe_count("other/substance", "substance_class") or client.request_json("GET", "/other/substance.json", params={"search": 'names.name:"PARACETAMOL"', "limit": 1}))
    run("other/unii", lambda: maybe_count("other/unii", "unii") or other.search_unii_by_substance_name(client, "WATER", limit=1))

    # TRANSPARENCY
    print("\n=== TRANSPARENCY ===")
    run("transparency/crl", lambda: maybe_count("transparency/crl", "letter_type") or client.request_json("GET", "/transparency/crl.json", params={"search": 'letter_date:"02/18/2022"', "limit": 1}))

    print("\nAll example queries attempted.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())