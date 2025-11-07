from __future__ import annotations
import urllib.parse
from typing import Optional, Dict

_PUG_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

# Tokens whose following value may contain '/' that should become '.'
# NOTE: include 'sourceid' but handle it as a special case (see below).
_VALUE_KEYS = {"sourcename", "heading", "sourceall", "sourceid"}

# Boundary tokens to stop generic "value collapsing" (unchanged)
_BOUNDARY_TOKENS = {
    "record","property","synonyms","sids","cids","aids","assaysummary","classification",
    "xrefs","description","conformers","concise","targets","doseresponse","summary",
    "pwaccs","geneids","accessions","target","activity","type",
    "XML","ASNT","ASNB","JSON","JSONP","SDF","CSV","PNG","TXT"
}

def _encode_segment(seg: str) -> str:
    # Keep ',' unencoded for lists like 'MolecularFormula,MolecularWeight'
    # Ampersand should be escaped to %26 inside a path segment.
    seg = seg.replace("&", "%26")
    return urllib.parse.quote(seg, safe=",")  # <-- allow commas

def _collapse_value(tokens: list[str], start: int) -> tuple[str, int]:
    """
    Generic collapse: join tokens until a boundary, then replace internal '/' with '.'
    Used for keys like 'sourcename', 'sourceall', 'heading'.
    """
    i = start
    chunks = []
    while i < len(tokens) and tokens[i] not in _BOUNDARY_TOKENS:
        chunks.append(tokens[i])
        i += 1
    val = "/".join(chunks).replace("/", ".")
    return val, i

def _sanitize_path(path: str) -> str:
    tokens = [t for t in path.strip("/").split("/") if t]
    out: list[str] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        out.append(_encode_segment(tok))

        if tok == "sourceid":
            # Special grammar: sourceid/<source name>/<source id>
            # Collapse ONLY the <source name> (may span multiple tokens), keep the final <source id> separate.
            # Because input_spec ends at the ID, we can treat the last token as <source id>,
            # and everything between i+1 and last-1 as the source name.
            if i + 2 < len(tokens):
                name_tokens = tokens[i + 1 : len(tokens) - 1]  # one or more tokens
                source_id_token = tokens[-1]                   # final token is <source id>
                name = "/".join(name_tokens).replace("/", ".")
                out.append(_encode_segment(name))
                out.append(_encode_segment(source_id_token))
                i = len(tokens)  # consumed all remaining tokens
                continue
            else:
                # Fallback: if structure isn't as expected, just advance normally
                i += 1
                continue

        if tok in _VALUE_KEYS:
            # Generic collapse for keys like 'sourcename', 'sourceall', 'heading'
            val, j = _collapse_value(tokens, i + 1)
            out.append(_encode_segment(val))
            i = j
        else:
            i += 1

    return "/".join(out)

def pug_rest_url(
    *,
    input_specification: str,
    operation_specification: str | None,
    output_specification: str | None = "JSON",
    operation_options: Dict[str, object] | None = None,
    base: str = _PUG_BASE,
) -> str:
    parts = [base.rstrip("/"), _sanitize_path(input_specification)]
    if operation_specification:
        parts.append(_sanitize_path(operation_specification))
    if output_specification:
        parts.append(_encode_segment(output_specification.strip().strip("/")))
    url = "/".join(parts)

    if operation_options:
        query = urllib.parse.urlencode(operation_options, doseq=True, safe="")
        if query:
            url = f"{url}?{query}"
    return url