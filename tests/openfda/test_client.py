import os
import pytest

from ind.openfda.client import OpenFDAClient
from ind.openfda import drug

LIVE = os.getenv("OPENFDA_LIVE") == "1"

@pytest.mark.skipif(not LIVE, reason="Set OPENFDA_LIVE=1 to run live tests")
def test_events_search_smoke():
    c = OpenFDAClient(api_key=os.getenv("OPENFDA_API_KEY"))
    res = drug.search_events(c, search="patient.reaction.reactionmeddrapt:HEADACHE", limit=3)
    assert res.meta.results is not None
    assert res.results is not None
    assert len(res.results) <= 3