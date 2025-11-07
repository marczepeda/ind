import os
import pytest
import requests

from ind.openfda.client import OpenFDAClient

LIVE = os.getenv("OPENFDA_LIVE") == "1"

pytestmark = pytest.mark.skipif(
    not LIVE,
    reason="Set OPENFDA_LIVE=1 to run openFDA smoke tests (they hit the public API).",
)

# A lightweight, generic smoke test runner that queries many endpoints
# using a safe facet (count) to avoid heavy payloads.
# Each item is (endpoint_path_without_json, count_field)
ENDPOINTS: list[tuple[str, str]] = [
    # --- DRUG ---
    ("drug/event", "patient.reaction.reactionmeddrapt"),
    ("drug/label", "openfda.brand_name"),
    ("drug/ndc", "product_type"),
    ("drug/enforcement", "classification"),
    ("drug/drugsfda", "openfda.brand_name"),
    ("drug/shortages", "status"),

    # --- ANIMAL & VETERINARY ---
    ("animalandveterinary/event", "reaction"),

    # --- DEVICE ---
    ("device/510k", "advisory_committee"),
    ("device/classification", "device_class"),
    ("device/pma", "advisory_committee"),
    ("device/event", "event_type"),
    ("device/recall", "recall_status"),
    ("device/enforcement", "classification"),
    ("device/registrationlisting", "establishment_type"),
    ("device/covid19serology", "manufacturer"),
    ("device/udi", "product_codes.code"),

    # --- FOOD ---
    ("food/enforcement", "classification"),
    ("food/event", "reactions"),

    # --- COSMETIC ---
    ("cosmetic/event", "reactions"),

    # --- OTHER ---
    ("other/historicaldocument", "doc_type"),
    ("other/nsde", "product_type"),
    ("other/substance", "substance_class"),
    ("other/unii", "unii"),

    # --- TOBACCO ---
    ("tobacco/problem", "tobacco_products"),

    # --- TRANSPARENCY ---
    ("transparency/crl", "letter_type"),
]

@pytest.fixture(scope="module")
def client() -> OpenFDAClient:
    # Pick up optional API key if present
    api_key = os.getenv("OPENFDA_API_KEY")
    return OpenFDAClient(api_key=api_key) if api_key else OpenFDAClient()

@pytest.mark.parametrize("endpoint,count_field", ENDPOINTS)
def test_openfda_endpoint_count_smoke(client: OpenFDAClient, endpoint: str, count_field: str) -> None:
    """Hit each endpoint with a small facet query and ensure a sane meta/results structure.

    We use `count` (faceting) with limit=1 to minimize payload and avoid depending on
    specific document-level fields existing in the very latest records.

    NOTE: For `count=` queries, OpenFDA often omits `meta.results` entirely and only returns
    `meta.{disclaimer,terms,license,last_updated}` with buckets in top-level `results`.
    """
    try:
        resp = client.request_json(
            "GET",
            f"/{endpoint}.json",
            params={"count": f"{count_field}.exact", "limit": 1},
        )
    except requests.exceptions.HTTPError as e:
        pytest.xfail(f"{endpoint}: HTTP {e}")

    # Basic shape checks
    assert isinstance(resp, dict), f"{endpoint}: response not a dict"
    assert "meta" in resp, f"{endpoint}: no meta key"
    assert "results" in resp, f"{endpoint}: no results key"

    meta = resp["meta"]
    assert "last_updated" in meta, f"{endpoint}: meta missing last_updated"
    # Do not require meta.results for count queries (it may be absent by design)

# A few document-level checks for common, very-stable queries
@pytest.mark.parametrize(
    "endpoint,search,expect_keys",
    [
        ("drug/event", 'patient.reaction.reactionmeddrapt:"HEADACHE"', ("results",)),
        ("device/510k", 'product_code:ITX', ("results",)),  # example device product code
        ("food/enforcement", 'classification:"Class I"', ("results",)),
        ("cosmetic/event", 'reactions:"RASH"', ("results",)),
    ],
)
def test_openfda_endpoint_search_smoke(client: OpenFDAClient, endpoint: str, search: str, expect_keys: tuple[str, ...]) -> None:
    try:
        resp = client.request_json(
            "GET",
            f"/{endpoint}.json",
            params={"search": search, "limit": 1},
        )
    except requests.exceptions.HTTPError as e:
        pytest.xfail(f"{endpoint}: HTTP {e}")

    assert isinstance(resp, dict)
    for k in expect_keys:
        assert k in resp