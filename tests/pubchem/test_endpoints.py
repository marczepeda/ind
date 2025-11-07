import responses
from ind.pubchem.client import PubChemClient
from ind.pubchem.endpoints import (
    get_compound_record,
    get_compound_properties,
    get_synonyms,
    get_ids,
    get_assaysummary,
    fast_search,
)

def test_get_compound_record_json(rsps, client: PubChemClient):
    url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/JSON"
    rsps.add(responses.GET, url, json={"PC_Compounds": []}, status=200)
    resp = get_compound_record(client, "2244", output="JSON")
    assert resp.status_code == 200

def test_get_compound_properties_csv_post(rsps, client: PubChemClient):
    url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/property/MolecularFormula,MolecularWeight/CSV"
    rsps.add(responses.POST, url,
             body="CID,MolecularFormula,MolecularWeight\n1,H2O,18\n", status=200, content_type="text/csv")
    resp = get_compound_properties(
        client,
        identifiers="1,2,3",
        properties="MolecularFormula,MolecularWeight",
        output="CSV",
        method="POST",
        post_cid="1,2,3",
    )
    assert resp.text.splitlines()[0].startswith("CID,")

def test_get_synonyms_compound_name(rsps, client: PubChemClient):
    url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/synonyms/JSON"
    rsps.add(responses.GET, url, json={"InformationList": {}}, status=200)
    resp = get_synonyms(client, "compound", "name", "aspirin", output="JSON")
    assert resp.ok

def test_get_ids_cids_from_name(rsps, client: PubChemClient):
    url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/cids/JSON?list_return=listkey"
    rsps.add(responses.GET, url, json={"IdentifierList": {"ListKey": "xxxx"}}, status=200)
    resp = get_ids(
        client,
        domain="compound",
        namespace="name",
        identifiers="aspirin",
        id_type="cids",
        output="JSON",
        options={"list_return": "listkey"},
    )
    assert resp.json()["IdentifierList"]["ListKey"] == "xxxx"

def test_fast_search_formula(rsps, client: PubChemClient):
    url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/fastformula/C6H12O/cids/JSON?MaxRecords=10"
    rsps.add(responses.GET, url, json={"IdentifierList": {"CID": [2244]}}, status=200)
    resp = fast_search(
        client,
        kind="fastformula",
        by="",  # ignored for fastformula
        query="C6H12O",
        options={"MaxRecords": 10},
        return_kind="cids",
        output="JSON",
    )
    assert 2244 in resp.json()["IdentifierList"]["CID"]