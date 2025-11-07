from __future__ import annotations

import time
from typing import Any, Dict, Mapping, Optional
import requests


DEFAULT_BASE_URL = "https://clinicaltrials.gov/api/v2"
DEFAULT_USER_AGENT = "ind/clinical_trials (https://github.com/marczepeda/ind)"


class ClinicalTrialsError(RuntimeError):
    """Raised for HTTP or API-level errors from the ClinicalTrials.gov API."""


class ClinicalTrialsClient:
    """
    Minimal HTTP client for ClinicalTrials.gov REST API 2.0.5.

    Notes
    -----
    * No auth is required.
    * Be gentle with rate limiting; this client supports a simple sleep-based throttle.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = 30.0,
        user_agent: str = DEFAULT_USER_AGENT,
        rate_limit_per_sec: Optional[float] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.user_agent = user_agent
        self.rate_limit_per_sec = rate_limit_per_sec
        self._session = session or requests.Session()
        self._last_request_ts: Optional[float] = None

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
            time.sleep(min_interval - elapsed)
        self._last_request_ts = time.monotonic()

    def request_json(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Perform an HTTP request and return parsed JSON.

        Raises
        ------
        ClinicalTrialsError on non-2xx or JSON decode failure.
        """
        self._respect_rate_limit()
        url = f"{self.base_url}{path}"
        headers = {"Accept": "application/json", "User-Agent": self.user_agent}
        try:
            resp = self._session.request(
                method.upper(), url, params=params, timeout=self.timeout, headers=headers
            )
        except requests.RequestException as exc:
            raise ClinicalTrialsError(f"HTTP error ({path}): {exc}") from exc

        if not (200 <= resp.status_code < 300):
            # Bubble up the response text to help when debugging e.g. bad params
            snippet = resp.text[:500]
            raise ClinicalTrialsError(
                f"HTTP error ({path}): {resp.status_code} {resp.reason}; body: {snippet}"
            )
        try:
            return resp.json()
        except ValueError as exc:
            snippet = resp.text[:500] if 'resp' in locals() else ''
            raise ClinicalTrialsError(
                f"Invalid JSON for {path}; body starts with: {snippet}"
            ) from exc