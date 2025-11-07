from __future__ import annotations

from typing import Dict, Optional, Union
import requests

from .client import PubChemClient
from .http import pug_fetch

JsonLike = Union[dict, list]


# --- Full record --------------------------------------------------------------

def get_compound_record(
    client: PubChemClient,
    identifiers: str,               # e.g., "2244" or "2244,3382"
    *,
    output: str = "JSON",
    record_type: Optional[str] = None,   # "2d" | "3d"
    image_size: Optional[str] = None,    # "large" | "small" | "WxH"
    to_file: Optional[str] = None,
) -> requests.Response:
    """
    Retrieve full compound record(s).

    GET form:
      /compound/cid/<identifiers>/<output>

    Options (as query params):
      - record_type: "2d" | "3d"
      - image_size: "large" | "small" | "<W>x<H>" (for PNG)
    """
    opts: Dict[str, str] = {}
    if record_type:
        opts["record_type"] = record_type
    if image_size:
        opts["image_size"] = image_size

    return pug_fetch(
        client,
        input_specification=f"compound/cid/{identifiers}",
        operation_specification=None,         # whole record
        output_specification=output,
        operation_options=opts,
        output_file=to_file,
    )


# --- Properties table ---------------------------------------------------------

def get_compound_properties(
    client: PubChemClient,
    identifiers: str,                     # e.g., "1,2,3"
    properties: str,                      # e.g., "MolecularFormula,MolecularWeight"
    *,
    output: str = "CSV",
    method: str = "GET",
    post_cid: Optional[str] = None,       # e.g., "1,2,3" for long lists via POST; if None, falls back to 'identifiers'
    to_file: Optional[str] = None,
) -> requests.Response:
    """
    Retrieve a compound property table.

    GET form:
      /compound/cid/<identifiers>/property/<properties>/<output>
    POST form (use when CID list is long):
      /compound/cid/property/<properties>/<output>  with body: cid=1,2,3

    Parameters
    ----------
    identifiers : str
        Comma-separated CIDs. Used in URL path for GET, or as fallback POST body when 'post_cid' is not provided.
    properties : str
        Comma-separated property tags.
    output : str
        One of XML | ASNT | ASNB | JSON | JSONP | CSV | TXT (SDF not valid for property table).
    method : str
        'GET' or 'POST'. If 'GET', identifiers MUST appear in the path. If 'POST', they should be in the form body.
    post_cid : Optional[str]
        Explicit CID list for the POST body (cid=...). If omitted for POST, 'identifiers' is used.
    to_file : Optional[str]
        If provided, writes response to this path.
    """
    m = method.upper()
    if m == "GET":
        # Include identifiers directly in the URL path (PubChem requires it for GET)
        input_spec = f"compound/cid/{identifiers}/property/{properties}"
        post = None
    elif m == "POST":
        # Put CID list in the form body; allow explicit post_cid override
        input_spec = f"compound/cid/property/{properties}"
        post = {"cid": post_cid or identifiers}
    else:
        raise ValueError("method must be 'GET' or 'POST'")

    return pug_fetch(
        client,
        input_specification=input_spec,
        operation_specification=None,
        output_specification=output,
        method=m,
        post_params=post,
        output_file=to_file,
    )


# --- Synonyms -----------------------------------------------------------------

def get_synonyms(
    client: PubChemClient,
    domain: str,                 # "compound" | "substance"
    namespace: str,              # "cid" | "sid" | "name" | "smiles"
    id_or_text: str,
    *,
    output: str = "JSON",
    to_file: Optional[str] = None,
) -> requests.Response:
    """
    Retrieve synonyms for a compound or substance.

    Example:
      /compound/name/aspirin/synonyms/JSON
    """
    return pug_fetch(
        client,
        input_specification=f"{domain}/{namespace}/{id_or_text}/synonyms",
        operation_specification=None,
        output_specification=output,
        output_file=to_file,
    )


# --- Identifier conversions: sids/cids/aids -----------------------------------

def get_ids(
    client: PubChemClient,
    domain: str,           # "compound" | "substance" | "assay"
    namespace: str,        # e.g., "cid", "sid", "name", "sourceall", etc.
    identifiers: str,
    id_type: str,          # "sids" | "cids" | "aids"
    *,
    output: str = "JSON",
    options: Optional[Dict[str, Union[str, int]]] = None,
    to_file: Optional[str] = None,
) -> requests.Response:
    """
    Convert or retrieve identifiers (SIDs/CIDs/AIDs) with optional filters.

    Options examples:
      - list_return: grouped | flat | listkey
      - aids_type / sids_type / cids_type, etc.
    """
    return pug_fetch(
        client,
        input_specification=f"{domain}/{namespace}/{identifiers}/{id_type}",
        operation_specification=None,
        output_specification=output,
        operation_options=options or {},
        output_file=to_file,
    )


# --- Assay summary (by CIDs or SIDs) ------------------------------------------

def get_assaysummary(
    client: PubChemClient,
    domain: str,            # "compound" | "substance"
    namespace: str,         # "cid" | "sid"
    identifiers: str,
    *,
    output: str = "CSV",
    to_file: Optional[str] = None,
) -> requests.Response:
    """
    Retrieve assay summaries for given CIDs or SIDs.

    Examples:
      /compound/cid/1000,1001/assaysummary/CSV
      /substance/sid/104234342/assaysummary/XML
    """
    return pug_fetch(
        client,
        input_specification=f"{domain}/{namespace}/{identifiers}/assaysummary",
        operation_specification=None,
        output_specification=output,
        output_file=to_file,
    )


# --- Fast searches (substructure/similarity/identity/formula) -----------------

def fast_search(
    client: PubChemClient,
    kind: str,                 # "fastsubstructure" | "fastsimilarity_2d" | "fastidentity" | "fastformula"
    by: str,                   # "smiles" | "inchi" | "sdf" | "cid" | (ignored for fastformula)
    query: str,
    *,
    return_kind: str = "cids", # typically "cids"
    output: str = "JSON",
    options: Optional[Dict[str, Union[str, int, bool]]] = None,
    method: str = "GET",
    post_body: Optional[Dict[str, str]] = None,  # e.g., {"inchi": "..."} when POST is required
    to_file: Optional[str] = None,
) -> requests.Response:
    """
    Perform a synchronous ('fast...') structure or formula search.

    Examples:
      /compound/fastsubstructure/smiles/<SMILES>/cids/JSON?MaxRecords=100
      /compound/fastsimilarity_2d/cid/2244/cids/XML
      /compound/fastidentity/smiles/CCCCC/cids/XML
      /compound/fastformula/C10H21N/cids/JSON
    """
    m = method.upper()
    if kind == "fastformula":
        input_spec = f"compound/{kind}/{query}/{return_kind}"
    else:
        input_spec = f"compound/{kind}/{by}/{query}/{return_kind}"

    post_params = post_body if m == "POST" else None

    return pug_fetch(
        client,
        input_specification=input_spec,
        operation_specification=None,
        output_specification=output,
        operation_options=options or {},
        method=m,
        post_params=post_params,
        output_file=to_file,
    )