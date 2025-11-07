from ind.uspto_odp.client import USPTOClient
from ind.uspto_odp.types import Pagination, SortOrder, Filter, RangeFilter, Sort
from ind.uspto_odp.petitions.decisions import search_decisions, download_search_decisions, get_decision
import sys
from pprint import pprint


client = USPTOClient(api_key=sys.argv[1])

# Search (GET with auto POST fallback)
res = search_decisions(
    client,
    q='finalDecidingOfficeName:OFFICE OF PETITIONS',
    filters=[Filter(name="decisionTypeCodeDescriptionText", value=["DENIED"])],
    range_filters=[RangeFilter(field="petitionMailDate", valueFrom="2022-08-04", valueTo="2025-08-04")],
    sort=[Sort(field="petitionMailDate", order=SortOrder.desc)],
    pagination=Pagination(offset=0, limit=1),
)

pprint(res)

# Fetch one record (with documents)
if res.get("petitionDecisionDataBag"):
    pid = res["petitionDecisionDataBag"][0]["petitionDecisionRecordIdentifier"]
    decision = get_decision(client, pid, include_documents=True)

# Download the same query as CSV
download_search_decisions(
    client,
    q='finalDecidingOfficeName:OFFICE OF PETITIONS',
    filters=[Filter(name="decisionTypeCodeDescriptionText", value=["DENIED"])],
    range_filters=[RangeFilter(field="petitionMailDate", valueFrom="2022-08-04", valueTo="2025-08-04")],
    sort=[Sort(field="petitionMailDate", order=SortOrder.desc)],
    fields=["applicationNumberText", "petitionMailDate", "decisionTypeCodeDescriptionText"],
    pagination=Pagination(offset=0, limit=100),
    format="csv",
    dest_path="downloads/petitions_denied.csv",
)