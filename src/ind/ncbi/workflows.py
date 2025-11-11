# src/ind/ncbi/workflows.py
from __future__ import annotations
from typing import Dict, Any, Iterable, Iterator, List, Optional, Tuple
from .client import EntrezClient
from . import endpoints as ep
from .utils import chunked

# ---------- High-level helpers ----------

def paged_esearch_uids(
    client: EntrezClient,
    db: str,
    term: str,
    *,
    chunk: int = 1000,
    limit: Optional[int] = None,
    usehistory: bool = True,
) -> Iterator[str]:
    """
    Generator over all UIDs for a query, paging with retstart/retmax.
    Stops at `limit` if provided.
    """
    retstart = 0
    yielded = 0
    while True:
        res = ep.esearch(
            client,
            db=db,
            term=term,
            retmax=min(chunk, (limit - yielded)) if limit else chunk,
            retstart=retstart,
            usehistory=usehistory,
        )
        ids = res.get("IdList", []) or []
        if not ids:
            break
        for _id in ids:
            yield _id
            yielded += 1
            if limit and yielded >= limit:
                return
        retstart += len(ids)
        if len(ids) < (chunk if not limit else min(chunk, limit - yielded)):
            break


def search_then_fetch_abstracts(
    client: EntrezClient,
    term: str,
    *,
    db: str = "pubmed",
    limit: int = 50,
) -> List[Tuple[str, str]]:
    """
    Search PubMed and return [(pmid, abstract_text)] for up to `limit` items.
    Uses efetch rettype=abstract retmode=text.
    """
    pmids = list(paged_esearch_uids(client, db=db, term=term, limit=limit))
    out: List[Tuple[str, str]] = []
    for group in chunked(pmids, 200):
        text = ep.efetch(
            client,
            db=db,
            ids=group,
            rettype="abstract",
            retmode="text",
        )
        blocks = [b for b in text.split("\n\n") if b.strip()]
        for i, pmid in enumerate(group):
            try:
                out.append((pmid, blocks[i].strip()))
            except IndexError:
                out.append((pmid, ""))
    return out


def linked_uids(
    client: EntrezClient,
    dbfrom: str,
    *,
    ids: Iterable[str],
    db: Optional[str] = None,
    linkname: Optional[str] = None,
    cmd: Optional[str] = None,
) -> Dict[str, List[str]]:
    """
    Return a mapping {source_uid: [linked_uid, ...]} using elink.
    Handles multiple possible response shapes from Entrez.read().
    """
    res = ep.elink(client, dbfrom=dbfrom, db=db, ids=ids, linkname=linkname, cmd=cmd)

    out: Dict[str, List[str]] = {}

    # Normalize structure — Entrez.read(elink) often returns a list of LinkSet dicts.
    if isinstance(res, list):
        linksets = res
    elif isinstance(res, dict):
        if "LinkSet" in res and isinstance(res["LinkSet"], list):
            linksets = res["LinkSet"]
        else:
            linksets = [res]
    else:
        linksets = [res]

    for ls in linksets:
        src_ids: List[str] = []
        idlist = ls.get("IdList")
        if isinstance(idlist, list):
            for item in idlist:
                if isinstance(item, dict) and "Id" in item:
                    src_ids.append(str(item["Id"]))
                else:
                    src_ids.append(str(item))

        # Initialize keys for all source IDs
        for src in (src_ids or ["_"]):
            out.setdefault(src, [])

        # Collect linked IDs
        ldb_list = ls.get("LinkSetDb")
        if isinstance(ldb_list, list):
            for ldb in ldb_list:
                links = ldb.get("Link") if isinstance(ldb, dict) else None
                if isinstance(links, list):
                    for link in links:
                        lid = link.get("Id") if isinstance(link, dict) else link
                        if lid is None:
                            continue
                        for src in (src_ids or ["_"]):
                            out[src].append(str(lid))

    return out


def download_fasta_for_gene_ids(
    client: EntrezClient,
    gene_ids: Iterable[str],
) -> Dict[str, str]:
    """
    For given Gene IDs, use elink to find linked nucleotide records and
    return a dict {gene_id: fasta_text}.
    """
    id_list = list(gene_ids)
    mapping = linked_uids(client, dbfrom="gene", db="nucleotide", ids=id_list, linkname="gene_nuccore")
    out: Dict[str, str] = {}
    for gid, nuccore_ids in mapping.items():
        seq_text = ""
        for group in chunked(nuccore_ids, 200):
            txt = ep.efetch(client, db="nucleotide", ids=group, rettype="fasta", retmode="text")
            seq_text += txt
        out[gid] = seq_text
    return out