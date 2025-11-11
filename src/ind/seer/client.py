from __future__ import annotations

import os
import time
from typing import Any, Dict, Mapping, Optional, Union
import requests

from ..config import get_info

JSON = Union[Dict[str, Any], Any]

DEFAULT_BASE_URL = "https://api.seer.cancer.gov"
DEFAULT_USER_AGENT = "ind/seer (https://github.com/marczepeda/ind)"

class SeerError(RuntimeError):
    """Raised for HTTP or API-level errors from the SEER API."""

class SeerClient:
    """
    Minimal HTTP client for the SEER REST API.

    - Supports API key via env var `SEER_API_KEY` or constructor arg.
    - Sends the key as `X-SEERAPI-Key` header (also mirrors to `X-SEER-API-KEY` for compatibility).
    - Simple optional rate limiting to be gentle to the public API.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        user_agent: str = DEFAULT_USER_AGENT,
        rate_limit_per_sec: Optional[float] = None,
        session: Optional[requests.Session] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.user_agent = user_agent
        self.rate_limit_per_sec = rate_limit_per_sec
        self._session = session or requests.Session()
        self._last_request_ts: Optional[float] = None

        self.api_key = api_key or os.getenv("SEER_API_KEY") or get_info("SEER_API_KEY")
        # default headers
        self._session.headers.update({
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        })
        if self.api_key:
            # Some docs show `X-SEERAPI-Key`; support both header spellings to be safe.
            self._session.headers.update({
                "X-SEERAPI-Key": self.api_key,
                "X-SEER-API-KEY": self.api_key,
            })
        else:
            raise SeerError("""SEER_API_KEY not provided; either...
    - set SEER_API_KEY in configuration (once): ind config set --id SEER_API_KEY --info your_api_key
    - pass api_key to SeerClient (every time)
    - set SEER_API_KEY environment variable (every session): export SEER_API_KEY=your_api_key
Refer to https://api.seer.cancer.gov/usage to retrieve your SEER_API_KEY.""")

        if extra_headers:
            self._session.headers.update(dict(extra_headers))

    # ---- internals ---------------------------------------------------------

    def _respect_rate_limit(self) -> None:
        if not self.rate_limit_per_sec:
            return
        now = time.monotonic()
        if self._last_request_ts is None:
            self._last_request_ts = now
            return
        min_interval = 1.0 / self.rate_limit_per_sec
        elapsed = now - self._last_request_ts
        if elapsed < min_interval:
            time.sleep(max(0.0, min_interval - elapsed))
        self._last_request_ts = time.monotonic()

    def _url(self, path: str) -> str:
        p = path if path.startswith("/") else f"/{path}"
        return f"{self.base_url}{p}"

    # ---- public ------------------------------------------------------------

    def request_json(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> JSON:
        """
        Perform an HTTP request and return parsed JSON.
        Raises SeerError on network, HTTP, or JSON errors.
        """
        self._respect_rate_limit()
        url = self._url(path)
        try:
            resp = self._session.request(
                method.upper(),
                url,
                params=params,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise SeerError(f"HTTP error ({path}): {exc}") from exc

        if not (200 <= resp.status_code < 300):
            snippet = resp.text[:500]
            raise SeerError(
                f"HTTP error ({path}): {resp.status_code} {resp.reason}; body: {snippet}"
            )
        try:
            return resp.json()
        except ValueError as exc:
            snippet = resp.text[:500]
            raise SeerError(f"Invalid JSON for {path}; body starts with: {snippet}") from exc
