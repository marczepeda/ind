# src/ind/ncbi/utils.py
from __future__ import annotations
from typing import Iterable, Iterator, List, Any, Dict
from Bio import Entrez

def chunked(seq: Iterable[Any], size: int) -> Iterator[List[Any]]:
    buf: List[Any] = []
    for x in seq:
        buf.append(x)
        if len(buf) == size:
            yield buf
            buf = []
    if buf:
        yield buf

def parse_xml(handle) -> Dict[str, Any]:
    """Parse Entrez XML into nested dict/list using Entrez.read()."""
    try:
        return Entrez.read(handle)  # returns Python structures
    finally:
        try:
            handle.close()
        except Exception:
            pass

def read_text(handle) -> str:
    try:
        return handle.read().decode() if hasattr(handle, "decode") else handle.read()
    finally:
        try:
            handle.close()
        except Exception:
            pass