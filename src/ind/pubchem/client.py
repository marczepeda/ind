from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Optional, Dict, Union, Iterable
import requests

DEFAULT_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

@dataclass
class PubChemClient:
    """
    Lightweight HTTP client with connection pooling, polite rate limiting (<=5 rps),
    and simple retries for 503/504/500.
    """
    base_url: str = DEFAULT_BASE
    timeout: float = 60.0
    max_rps: float = 5.0
    max_retries: int = 3
    backoff_factor: float = 0.75
    user_agent: str = "ind.pubchem/1.0 (+https://github.com/marczepeda/ind)"
    _last_call_ts: float = 0.0
    _session: Optional[requests.Session] = None

    @property
    def session(self) -> requests.Session:
        if self._session is None:
            s = requests.Session()
            s.headers.update({"User-Agent": self.user_agent})
            self._session = s
        return self._session

    # --- polite rate limiting: no more than max_rps per second ---
    def _throttle(self) -> None:
        if self.max_rps <= 0:
            return
        min_interval = 1.0 / self.max_rps
        dt = time.time() - self._last_call_ts
        if dt < min_interval:
            time.sleep(min_interval - dt)
        self._last_call_ts = time.time()

    def request(self, * , method: str, url: str, **kwargs) -> requests.Response:
        """
        Central request method used by endpoints; handles throttling + retries.
        kwargs may include: headers, params, data, files, timeout override, etc.
        """
        self._throttle()
        timeout = kwargs.pop("timeout", self.timeout)

        attempt = 0
        while True:
            try:
                resp = self.session.request(method=method, url=url, timeout=timeout, **kwargs)
            except requests.RequestException:
                # transport error; retry if attempts remain
                if attempt < self.max_retries:
                    time.sleep(self.backoff_factor * (2 ** attempt))
                    attempt += 1
                    continue
                raise

            # Retry transient 503/504/500 with exponential backoff
            if resp.status_code in (500, 503, 504) and attempt < self.max_retries:
                time.sleep(self.backoff_factor * (2 ** attempt))
                attempt += 1
                continue

            return resp