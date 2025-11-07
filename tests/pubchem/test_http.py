import pytest
import json
import pathlib

import responses
from ind.pubchem.client import PubChemClient
from ind.pubchem.http import pug_fetch, PugRestError

def test_accept_header_inferred_from_output(rsps, client: PubChemClient):
    url_prefix = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/JSON"
    rsps.add(responses.GET, url_prefix, json={"ok": True}, status=200)
    resp = pug_fetch(
        client,
        input_specification="compound/cid/2244",
        output_specification="JSON",
    )
    assert resp.request.headers.get("Accept") == "application/json"
    assert resp.json()["ok"] is True

def test_post_form_encoding_for_cid_list(rsps, client: PubChemClient):
    url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/property/MolecularFormula,MolecularWeight/CSV"
    rsps.add(responses.POST, url, body="CID,MolecularFormula,MolecularWeight\n1,H2O,18\n", status=200,
             content_type="text/csv")

    resp = pug_fetch(
        client,
        input_specification="compound/cid/property/MolecularFormula,MolecularWeight",
        output_specification="CSV",
        method="POST",
        post_params={"cid": "1,2,3"},
    )
    # requests sends form-encoded when string given; ensure header set
    assert resp.request.headers.get("Content-Type", "").startswith("application/x-www-form-urlencoded")
    body = resp.request.body
    if isinstance(body, bytes):
        body = body.decode()
    assert "cid=1%2C2%2C3" in body

def test_file_output_text_and_binary(rsps, client: PubChemClient, tmp_path):
    # Text case
    url_json = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/JSON"
    rsps.add(responses.GET, url_json, json={"hello": "world"}, status=200)
    out_json = tmp_path / "out.json"
    pug_fetch(client, input_specification="compound/cid/2244", output_specification="JSON",
              output_file=str(out_json), quiet=True)
    assert out_json.read_text().strip().startswith("{")

    # Binary case (PNG)
    url_png = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/PNG"
    rsps.add(responses.GET, url_png, body=b"\x89PNG\r\n", status=200, content_type="image/png")
    out_png = tmp_path / "img.png"
    pug_fetch(client, input_specification="compound/cid/2244", output_specification="PNG",
              output_file=str(out_png), quiet=True)
    assert out_png.read_bytes().startswith(b"\x89PNG")

def test_error_raises_pugresterror(rsps, client: PubChemClient):
    bad = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/0/JSON"
    rsps.add(responses.GET, bad, json={"Fault": {"Code": "PUGREST.NotFound"}}, status=404)
    with pytest.raises(PugRestError) as ei:
        pug_fetch(client, input_specification="compound/cid/0", output_specification="JSON")
    msg = str(ei.value)
    assert "404" in msg and "Not found" in msg