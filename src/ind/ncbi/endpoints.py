from __future__ import annotations
from typing import Iterable, List, Dict, Any, Optional
from Bio import Entrez
from .client import EntrezClient
from .utils import parse_xml, read_text, chunked
import json

# ---- Core E-utilities ----

def esearch(
    client: EntrezClient,
    db: str,
    term: str,
    *,
    retmax: int = 20,
    retstart: int = 0,
    usehistory: bool = True,
    sort: Optional[str] = None,
    field: Optional[str] = None,
    datetype: Optional[str] = None,
    mindate: Optional[str] = None,
    maxdate: Optional[str] = None,
    webenv: Optional[str] = None,
    query_key: Optional[str] = None,
    rettype: Optional[str] = None,   # 'uilist' or 'count'
    retmode: str = "xml",            # 'xml' or 'json'
    idtype: Optional[str] = None,    # e.g., 'acc' for sequence DBs
    reldate: Optional[int] = None,
) -> Any:
    handle = client.call(
        Entrez.esearch,
        db=db,
        term=term,
        retmax=retmax,
        retstart=retstart,
        usehistory="y" if usehistory else "n",
        sort=sort,
        field=field,
        datetype=datetype,
        mindate=mindate,
        maxdate=maxdate,
        WebEnv=webenv,
        query_key=query_key,
        rettype=rettype,
        retmode=retmode,
        idtype=idtype,
        reldate=reldate,
    )
    if retmode == "xml":
        return parse_xml(handle)
    # JSON or other text modes
    text = read_text(handle)
    try:
        return json.loads(text)
    except Exception:
        return text

def esummary(
    client: EntrezClient,
    db: str,
    ids: Iterable[str] = (),
    *,
    webenv: Optional[str] = None,
    query_key: Optional[str] = None,
    retstart: int = 0,
    retmax: Optional[int] = None,
    retmode: str = "xml",       # 'xml' or 'json'
    version: Optional[str] = None,  # e.g., '2.0'
) -> Any:
    handle = client.call(
        Entrez.esummary,
        db=db,
        id=",".join(ids) if ids else None,
        webenv=webenv,
        query_key=query_key,
        retstart=retstart,
        retmax=retmax,
        retmode=retmode,
        version=version,
    )
    if retmode == "xml":
        return parse_xml(handle)
    text = read_text(handle)
    try:
        return json.loads(text)
    except Exception:
        return text

def efetch(
    client: EntrezClient,
    db: str,
    ids: Iterable[str] = (),
    *,
    rettype: Optional[str] = None,
    retmode: str = "xml",
    webenv: Optional[str] = None,
    query_key: Optional[str] = None,
    retstart: int = 0,
    retmax: Optional[int] = None,
    strand: Optional[int] = None,       # sequence DBs: 1 (plus) or 2 (minus)
    seq_start: Optional[int] = None,    # sequence DBs
    seq_stop: Optional[int] = None,     # sequence DBs
    complexity: Optional[int] = None,   # sequence DBs: 0..4
) -> Any:
    handle = client.call(
        Entrez.efetch,
        db=db,
        id=",".join(ids) if ids else None,
        rettype=rettype,
        retmode=retmode,
        webenv=webenv,
        query_key=query_key,
        retstart=retstart,
        retmax=retmax,
        strand=strand,
        seq_start=seq_start,
        seq_stop=seq_stop,
        complexity=complexity,
    )
    return parse_xml(handle) if retmode == "xml" else read_text(handle)

def elink(
    client: EntrezClient,
    dbfrom: str,
    *,
    db: Optional[str] = None,
    ids: Iterable[str] = (),
    linkname: Optional[str] = None,
    cmd: Optional[str] = None,
    webenv: Optional[str] = None,
    query_key: Optional[str] = None,
    term: Optional[str] = None,
    holding: Optional[str] = None,
    datetype: Optional[str] = None,
    reldate: Optional[int] = None,
    mindate: Optional[str] = None,
    maxdate: Optional[str] = None,
    idtype: Optional[str] = None,
    retmode: str = "xml",  # 'xml', 'json', 'ref', 'text', 'html' (pass-through)
) -> Any:
    handle = client.call(
        Entrez.elink,
        dbfrom=dbfrom,
        db=db,
        id=",".join(ids) if ids else None,
        linkname=linkname,
        cmd=cmd,
        webenv=webenv,
        query_key=query_key,
        term=term,
        holding=holding,
        datetype=datetype,
        reldate=reldate,
        mindate=mindate,
        maxdate=maxdate,
        idtype=idtype,
        retmode=retmode,
    )
    if retmode == "xml":
        return parse_xml(handle)
    return read_text(handle)

def einfo(
    client: EntrezClient,
    db: Optional[str] = None,
    *,
    version: Optional[str] = None,   # e.g., '2.0'
    retmode: str = "xml",            # 'xml' or 'json'
) -> Any:
    handle = client.call(Entrez.einfo, db=db, version=version, retmode=retmode)
    if retmode == "xml":
        return parse_xml(handle)
    text = read_text(handle)
    try:
        return json.loads(text)
    except Exception:
        return text

def egquery(client: EntrezClient, term: str) -> Dict[str, Any]:
    handle = client.call(Entrez.egquery, term=term, retmode="xml")
    return parse_xml(handle)

def espell(client: EntrezClient, db: str, term: str) -> Dict[str, Any]:
    handle = client.call(Entrez.espell, db=db, term=term, retmode="xml")
    return parse_xml(handle)

def ecitmatch(client: EntrezClient, bdata: str, *, retmode: str = "xml") -> Any:
    """
    E-utilities ecitmatch: Given citation strings, retrieve matching PubMed IDs.
    `bdata` should be pipe-delimited citation lines per NCBI spec.
    """
    handle = client.call(Entrez.ecitmatch, db="pubmed", bdata=bdata, retmode=retmode)
    return parse_xml(handle) if retmode == "xml" else read_text(handle)

def epost(client: EntrezClient, db: str, ids: Iterable[str]) -> Dict[str, Any]:
    handle = client.call(Entrez.epost, db=db, id=",".join(ids), retmode="xml")
    return parse_xml(handle)

# ---- Convenience helpers ----

def search_then_summary(
    client: EntrezClient,
    db: str,
    term: str,
    *,
    retmax: int = 50,
    summary_chunk: int = 200,
) -> Dict[str, Any]:
    """Search a term, then batch esummary for all UIDs."""
    s = esearch(client, db=db, term=term, retmax=retmax, usehistory=True)
    ids = s.get("IdList", [])
    summaries: List[Dict[str, Any]] = []
    for group in chunked(ids, summary_chunk):
        res = esummary(client, db=db, ids=group)
        summaries.append(res)
    return {"search": s, "summaries": summaries}