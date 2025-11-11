# src/ind/ncbi/client.py
from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass
import time
import os
import threading
from typing import Iterator, Optional, Dict, Any
from Bio import Entrez
from urllib.error import HTTPError, URLError
from ..config import get_info

_DEFAULT_BASE_DELAY = 0.4  # ~2.5 req/s default; safer than hard 3/s
_KEYED_BASE_DELAY = 0.12   # ~8–9 req/s with api_key; under 10/s

class NCBIError(RuntimeError):
    """Raised for HTTP or API-level errors from the NCBI API."""

@dataclass
class NCBIConfig:
    email: str
    api_key: Optional[str] = None
    tool: str = "ind-ncbi"
    timeout: int = 30
    base_delay: Optional[float] = None  # override if you want
    max_retries: int = 3
    backoff: float = 2.0

class RateLimiter:
    def __init__(self, delay: float):
        self.delay = delay
        self._lock = threading.Lock()
        self._last = 0.0

    def wait(self) -> None:
        with self._lock:
            now = time.time()
            delta = now - self._last
            sleep_for = self.delay - delta
            if sleep_for > 0:
                time.sleep(sleep_for)
            self._last = time.time()

class EntrezClient:
    """Thin wrapper to set Entrez globals and enforce rate-limit + retries."""
    def __init__(self, cfg: NCBIConfig):
        self.cfg = cfg
        delay = cfg.base_delay
        if delay is None:
            delay = _KEYED_BASE_DELAY if cfg.api_key else _DEFAULT_BASE_DELAY
        self.rate = RateLimiter(delay)
        self.email = cfg.email or os.getenv("NCBI_EMAIL") or get_info("NCBI_EMAIL")
        self.api_key = cfg.api_key or os.getenv("NCBI_API_KEY") or get_info("NCBI_API_KEY")
        if self.email is None:
            raise NCBIError("NCBI email is required; please provide or set NCBI_EMAIL env var or config.")

    @contextmanager
    def session(self) -> Iterator[None]:
        Entrez.email = self.cfg.email
        Entrez.api_key = self.cfg.api_key
        Entrez.tool = self.cfg.tool
        Entrez.timeout = self.cfg.timeout
        yield

    def call(self, fn, *args, **kwargs) -> Any:
        """Execute an Entrez.* call with rate-limit + retry + read & parse."""
        last_err = None
        for attempt in range(1, self.cfg.max_retries + 1):
            self.rate.wait()
            try:
                with self.session():
                    handle = fn(*args, **kwargs)
                    # Most E-utilities can return XML. Let caller decide parse mode.
                    return handle
            except (HTTPError, URLError, TimeoutError) as exc:
                last_err = exc
                if attempt >= self.cfg.max_retries:
                    raise
                time.sleep((self.cfg.backoff ** (attempt - 1)) * 0.5)
        # Should not reach
        raise RuntimeError(f"Entrez call failed after retries: {last_err}")