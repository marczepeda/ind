from __future__ import annotations
import urllib.parse
from typing import Dict, Optional, Union
import requests
from .urls import pug_rest_url

ACCEPT_BY_FORMAT: Dict[str, str] = {
    "XML":  "application/xml",
    "JSON": "application/json",
    "JSONP":"application/javascript",
    "ASNB": "application/ber-encoded",
    "SDF":  "chemical/x-mdl-sdfile",
    "CSV":  "text/csv",
    "PNG":  "image/png",
    "TXT":  "text/plain",
}

def _accept_for(output_spec: Optional[str], explicit_accept: Optional[str]) -> Optional[str]:
    if explicit_accept:
        return explicit_accept
    if output_spec:
        return ACCEPT_BY_FORMAT.get(output_spec.strip().upper())
    return None

_PUG_STATUS_HINT = {
    202: "Accepted (asynchronous operation pending).",
    400: "Bad request (URL or POST body syntax).",
    404: "Not found (e.g., invalid identifier).",
    405: "Not allowed (possibly invalid Accept header).",
    500: "Server-side problem or unknown error.",
    501: "Not implemented.",
    503: "Server busy; retry later.",
    504: "Timeout from server or request too broad.",
}

class PugRestError(requests.HTTPError):
    def __init__(self, response: requests.Response):
        hint = _PUG_STATUS_HINT.get(response.status_code, "HTTP error.")
        try:
            snippet = response.text.strip()
            if len(snippet) > 500:
                snippet = snippet[:500] + "…"
        except Exception:
            snippet = "<no text>"
        super().__init__(f"{response.status_code} {response.reason}: {hint}\n{snippet}",
                         response=response)

def _encode_form(d: Dict[str, Union[str, int, float, bool, list]]) -> str:
    return urllib.parse.urlencode(d, doseq=True)

def pug_fetch(
    client,  # ind.pubchem.client.PubChemClient
    *,
    input_specification: str,
    operation_specification: Optional[str] = None,
    output_specification: Optional[str] = "JSON",
    operation_options: Optional[Dict[str, Union[str, int, float, bool, list]]] = None,
    method: str = "GET",
    accept: Optional[str] = None,
    post_params: Optional[Dict[str, Union[str, int, float, bool, list]]] = None,
    files: Optional[Dict[str, tuple]] = None,
    content_type: Optional[str] = None,
    data: Optional[Union[bytes, str]] = None,
    output_file: Optional[str] = None,
    quiet: bool = False,
    timeout: Optional[float] = None,
    raise_for_status: bool = True,
) -> requests.Response:
    """
    Execute request via client's session (rate-limited + retries) and optionally write to file.
    """
    url = pug_rest_url(
        input_specification=input_specification,
        operation_specification=operation_specification,
        output_specification=output_specification or "",
        operation_options=operation_options or {},
        base=client.base_url,
    )

    headers: Dict[str, str] = {}
    resolved_accept = _accept_for(output_specification, accept)
    if resolved_accept:
        headers["Accept"] = resolved_accept

    method = method.upper()
    if method not in {"GET", "POST"}:
        raise ValueError("method must be 'GET' or 'POST'")

    req_kwargs: Dict[str, object] = {"headers": headers}
    if timeout is not None:
        req_kwargs["timeout"] = timeout

    if method == "POST":
        if files is not None:
            req_kwargs["files"] = files
            if post_params:
                req_kwargs["data"] = post_params
        elif data is not None:
            if content_type:
                headers["Content-Type"] = content_type
            req_kwargs["data"] = data
        elif post_params:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            req_kwargs["data"] = _encode_form(post_params)
        else:
            headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
            req_kwargs["data"] = b""

    resp = client.request(method=method, url=url, **req_kwargs)

    if raise_for_status and not (200 <= resp.status_code < 300):
        raise PugRestError(resp)

    if output_file:
        import pathlib
        path = pathlib.Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        ctype = (resp.headers.get("Content-Type") or "").lower()
        text_like = any(x in ctype for x in ("json", "xml", "csv", "text", "javascript"))
        if text_like:
            path.write_text(resp.text, encoding="utf-8")
        else:
            path.write_bytes(resp.content)
        if not quiet:
            size_kb = len(resp.content) / 1024
            print(f"[ind.pubchem] wrote {size_kb:.1f} KB → {path.resolve()}")

    return resp