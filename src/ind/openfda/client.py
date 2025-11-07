from __future__ import annotations
import time
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Mapping, MutableMapping, Optional

import requests

log = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.fda.gov"

@dataclass
class OpenFDAClient:
    """Thin HTTP client for OpenFDA.

    - Supports optional API key (X-Api-Key header)
    - Centralizes retries with backoff on 429/5xx
    - Adds convenience for `.json` suffixing and query params
    """

    base_url: str = DEFAULT_BASE_URL
    api_key: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3
    backoff_factor: float = 1.5
    session: requests.Session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Accept": "application/json"}
        if self.api_key:
            headers["X-Api-Key"] = self.api_key
        return headers

    def request_json(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Perform a request and return parsed JSON, with retries.

        `path` should start with '/{category}/{endpoint}.json' or similar.
        """
        url = f"{self.base_url}{path}"
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = self.session.request(
                    method.upper(), url, headers=self._headers(), params=params, timeout=self.timeout
                )
            except requests.RequestException as e:
                if attempt <= self.max_retries:
                    sleep = self.backoff_factor ** (attempt - 1)
                    log.warning("openfda request error %s; retrying in %.2fs", e, sleep)
                    time.sleep(sleep)
                    continue
                raise

            if resp.status_code in (429, 500, 502, 503, 504) and attempt <= self.max_retries:
                sleep = self.backoff_factor ** (attempt - 1)
                log.info("openfda %s -> %s; retrying in %.2fs", url, resp.status_code, sleep)
                time.sleep(sleep)
                continue

            resp.raise_for_status()
            return resp.json()