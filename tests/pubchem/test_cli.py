import argparse
import sys
from pathlib import Path
import responses

from ind.pubchem.cli import run_pubchem

def test_cli_pubchem_to_stdout(rsps, tmp_path, monkeypatch):
    # Arrange a fake GET that returns JSON
    url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/JSON"
    rsps.add(responses.GET, url, json={"ok": True}, status=200)

    # Build argparse Namespace like CLI would produce
    args = argparse.Namespace(
        input_spec="compound/cid/2244",
        operation_spec=None,
        output_spec="JSON",
        opt=[],
        method="GET",
        accept=None,
        content_type=None,
        timeout=5.0,
        max_rps=100.0,
        retries=0,
        output=None,
        quiet=True,     # don't print; just test execution path
        no_raise=False,
        post=[],
    )

    rc = run_pubchem(args)
    assert rc == 0

def test_cli_pubchem_write_file(rsps, tmp_path):
    url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/PNG"
    rsps.add(responses.GET, url, body=b"\x89PNG\r\n", status=200, content_type="image/png")

    args = argparse.Namespace(
        input_spec="compound/cid/2244",
        operation_spec=None,
        output_spec="PNG",
        opt=[],
        method="GET",
        accept=None,
        content_type=None,
        timeout=5.0,
        max_rps=100.0,
        retries=0,
        output=str(tmp_path / "aspirin.png"),
        quiet=True,
        no_raise=False,
        post=[],
    )

    rc = run_pubchem(args)
    assert rc == 0
    assert (tmp_path / "aspirin.png").read_bytes().startswith(b"\x89PNG")