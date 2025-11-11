# tests/ncbi/test_endpoints_mock.py
from __future__ import annotations
import io
import json
import types
import pytest
from ind.ncbi.client import EntrezClient, NCBIConfig
from ind.ncbi import endpoints as ep
from ind.ncbi import utils as utils_mod

class FakeHandle(io.StringIO):
    def close(self): super().close()

def test_esearch_roundtrip(monkeypatch):
    def fake_esearch(**kwargs):
        return FakeHandle(json.dumps({"IdList": ["10", "11"]}))
    monkeypatch.setattr(ep, "Entrez", types.SimpleNamespace(esearch=fake_esearch))
    monkeypatch.setattr(ep, "parse_xml", lambda h: json.loads(h.read()))
    client = EntrezClient(NCBIConfig(email="test@tld"))
    res = ep.esearch(client, db="pubmed", term="x")
    assert res["IdList"] == ["10", "11"]