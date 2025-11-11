# tests/ncbi/test_workflows.py
from __future__ import annotations
import types
import io
import json
import builtins
import pytest

# We avoid importing Bio.Entrez for the test environment; instead we monkeypatch
# your endpoints to call our fake Entrez.* functions via the client wrapper.

from ind.ncbi.client import EntrezClient, NCBIConfig
from ind.ncbi import endpoints as ep
from ind.ncbi import workflows as wf

class FakeHandle(io.StringIO):
    def close(self):
        super().close()

class FakeEntrez:
    def __init__(self):
        self.calls = []

    # esearch returns XML parsed by Entrez.read; but our client returns the handle
    # and endpoints.parse_xml() calls Entrez.read(handle). We'll bypass by returning JSON-ish
    # encoded string and intercept parse_xml if needed. Simpler: we fake endpoints.parse_xml
    # by monkeypatching in the test to json.loads.
    def esearch(self, **kwargs):
        self.calls.append(("esearch", kwargs))
        retmax = int(kwargs.get("retmax", 20))
        retstart = int(kwargs.get("retstart", 0))
        total = 230
        ids = list(map(str, range(retstart + 1, min(retstart + retmax, total) + 1)))
        payload = {"IdList": ids, "RetStart": str(retstart), "RetMax": str(retmax), "Count": str(total)}
        return FakeHandle(json.dumps(payload))

    def efetch(self, **kwargs):
        self.calls.append(("efetch", kwargs))
        ids = (kwargs.get("id") or "").split(",")
        rettype = kwargs.get("rettype")
        retmode = kwargs.get("retmode")
        if rettype == "abstract" and retmode == "text":
            blocks = []
            for i in ids:
                blocks.append(f"PMID: {i}\nTI  - Title {i}\nAB  - Abstract text for {i}")
            return FakeHandle("\n\n".join(blocks))
        if rettype == "fasta" and retmode == "text":
            blocks = []
            for i in ids:
                blocks.append(f">seq|{i}\nATGCATGCATGC")
            return FakeHandle("\n".join(blocks))
        return FakeHandle("")

    def elink(self, **kwargs):
        self.calls.append(("elink", kwargs))
        ids = (kwargs.get("id") or "").split(",") if kwargs.get("id") else []
        # Map each id -> two nuccore ids
        linkset = []
        for gid in ids:
            linkset.append({
                "IdList": [gid],
                "LinkSetDb": [{"Link": [{"Id": f"{gid}001"}, {"Id": f"{gid}002"}]}],
            })
        return FakeHandle(json.dumps({"LinkSet": linkset}))

@pytest.fixture
def fake_entrez(monkeypatch):
    # Patch in our FakeEntrez and a JSON parser for parse_xml
    fe = FakeEntrez()

    from ind.ncbi import client as client_mod
    from ind.ncbi import utils as utils_mod

    # Redirect Entrez.* used by client.call(...)
    # We'll monkeypatch at the module attribute level used by endpoints.
    monkeypatch.setattr(ep, "Entrez", types.SimpleNamespace(
        esearch=fe.esearch, efetch=fe.efetch, elink=fe.elink, einfo=None, esummary=None, egquery=None, espell=None, epost=None
    ))

    # parse_xml should parse JSON string emitted by our FakeHandle
    monkeypatch.setattr(ep, "parse_xml", lambda h: json.loads(h.read()))

    return fe

def test_paged_esearch_and_fetch_abstracts(fake_entrez):
    client = EntrezClient(NCBIConfig(email="you@org.tld"))
    res = wf.search_then_fetch_abstracts(client, term="cancer", limit=5)
    assert len(res) == 5
    # first pair
    pmid, abstract = res[0]
    assert pmid == "1"
    assert "Abstract text for 1" in abstract

def test_linked_and_fasta(fake_entrez):
    client = EntrezClient(NCBIConfig(email="you@org.tld"))
    mapping = wf.linked_uids(client, dbfrom="gene", ids=["101", "202"], db="nucleotide", linkname="gene_nuccore")
    assert mapping["101"] == ["101001", "101002"]
    assert mapping["202"] == ["202001", "202002"]

    fasta = wf.download_fasta_for_gene_ids(client, ["101"])
    assert "seq|101001" in fasta["101"]
    assert "ATGC" in fasta["101"]