# src/ind/ncbi/types.py
from __future__ import annotations
from typing import TypedDict, List, Optional

# These reflect common PubMed ESummary fields as returned by Entrez.read().
# They are intentionally partial and safe-to-extend later.

class PubMedDocSumItem(TypedDict, total=False):
    Name: str
    DataType: str
    # "Label": Optional[str]  # (sometimes present)
    # "AType": Optional[str]  # (for certain items)
    # Value fields:
    # For strings:
    __text__: Optional[str]
    # For lists:
    # "Item": Optional[List["PubMedDocSumItem"]]  # recursive in raw structures

class PubMedDocSum(TypedDict, total=False):
    Id: str
    Item: List[PubMedDocSumItem]

class PubMedESummaryResult(TypedDict, total=False):
    DocumentSummarySet: dict  # Raw container
    # Optional parsed convenience fields you may add downstream:
    # "Summaries": List[PubMedDocSum]

class ESearchResult(TypedDict, total=False):
    Count: str
    RetMax: str
    RetStart: str
    IdList: List[str]
    QueryKey: Optional[str]
    WebEnv: Optional[str]