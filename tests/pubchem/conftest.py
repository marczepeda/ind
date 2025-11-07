import json
import io
import os
import pytest
import responses

from ind.pubchem.client import PubChemClient

@pytest.fixture
def client():
    # Fast timeouts & low RPS to keep tests snappy
    return PubChemClient(timeout=2.0, max_rps=9999.0, max_retries=0)

@pytest.fixture(autouse=True)
def _no_env_rate_limit(monkeypatch):
    # Ensure no unexpected env-based throttling in tests
    monkeypatch.delenv("CLINICALTRIALS_LIVE", raising=False)
    monkeypatch.delenv("PUBCHEM_LIVE", raising=False)

@pytest.fixture
def rsps():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps

def json_body(**payload):
    return json.dumps(payload), {"Content-Type": "application/json"}

def text_body(text, content_type="text/plain"):
    return text, {"Content-Type": content_type}

def binary_body(data: bytes, content_type="application/octet-stream"):
    # responses will accept bytes body directly; headers must include content-type
    return data, {"Content-Type": content_type}