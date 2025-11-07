import os
import pytest

from ind.naaccr import (
    NAACCRClient,
    list_versions,
    search_data_items,
    get_data_item,
    get_attribute_history,
    get_operation_history,
)

LIVE = os.getenv("NAACCR_LIVE", "0") == "1"


@pytest.mark.skipif(not LIVE, reason="Set NAACCR_LIVE=1 to run live NAACCR API tests")
def test_versions_live():
    client = NAACCRClient()
    res = list_versions(client)
    assert isinstance(res, list)
    assert any("Version" in v for v in res)


@pytest.mark.skipif(not LIVE, reason="Set NAACCR_LIVE=1 to run live NAACCR API tests")
def test_search_and_fetch_item_live():
    client = NAACCRClient()
    items = search_data_items(client, "22", q="tumor",minimize_results=True)
    assert isinstance(items, list)
    assert len(items) > 0
    # pick first and fetch
    naaccr_id = items[0].get("XmlNaaccrId") or items[0].get("ItemNumber")
    assert naaccr_id
    full = get_data_item(client, "22", str(naaccr_id))
    assert isinstance(full, dict)
    assert full.get("ItemName")


@pytest.mark.skipif(not LIVE, reason="Set NAACCR_LIVE=1 to run live NAACCR API tests")
def test_histories_live():
    client = NAACCRClient()
    # derive a valid id from a live search to avoid 404s
    items = search_data_items(client, "22", q="tumor", minimize_results=True)
    assert items, "Expected at least one item from search"
    xml_or_number = items[0].get("ItemNumber") or items[0].get("XmlNaaccrId")
    assert xml_or_number, "ItemNumber/XmlNaaccrId not found in search results"

    attr_hist = get_attribute_history(client, str(xml_or_number), attribute="Description")
    assert isinstance(attr_hist, dict)

    op_hist = get_operation_history(client, "22", str(xml_or_number))
    assert isinstance(op_hist, dict)