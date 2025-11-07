from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Union
import requests
from urllib.parse import urlencode

JSON = Union[Dict[str, Any], Any]


class NAACCRClient:
    """
    Tiny HTTP client for the NAACCR Data Dictionary API.

    Base docs: https://apps.naaccr.org/data-dictionary/api/1.0/documentation/
    """

    def __init__(
        self,
        base_url: str = "https://apps.naaccr.org/data-dictionary/api/1.0",
        *,
        session: Optional[requests.Session] = None,
        timeout: float = 15.0,
        headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        if headers:
            self.session.headers.update(dict(headers))

    def _url(self, path: str) -> str:
        path = path.lstrip("/")
        return f"{self.base_url}/{path}"

    def _build_url_with_special_params(
        self, path: str, params: Optional[Mapping[str, Any]]
    ) -> str:
        """
        Build URL manually for special NAACCR parameters that must keep quotes,
        e.g. minimize_results="true".
        """
        if not params:
            return self._url(path)

        base = self._url(path)
        # Parameters that require quoted values
        special_params = {"minimize_results"}

        regular = {k: v for k, v in params.items() if k not in special_params}
        special = {k: v for k, v in params.items() if k in special_params}

        query_parts = []
        if regular:
            query_parts.append(urlencode(regular))
        for k, v in special.items():
            # append without URL encoding the quotes
            query_parts.append(f"{k}=\"{v}\"")

        query_string = "&".join(query_parts)
        return f"{base}?{query_string}"

    def request_json(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> JSON:
        # Handle special quoted params
        special_params = {"minimize_results"}
        if params and any(k in special_params for k in params):
            url = self._build_url_with_special_params(path, params)
            resp = self.session.request(method.upper(), url, timeout=self.timeout)
        else:
            url = self._url(path)
            resp = self.session.request(method.upper(), url, params=params, timeout=self.timeout)

        resp.raise_for_status()
        return resp.json()