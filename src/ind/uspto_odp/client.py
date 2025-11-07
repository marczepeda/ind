"""
client.py — Core USPTO Open Data Portal HTTP client

This module provides a single, shared `USPTOClient` class that handles:
  • Session management with retries and timeouts.
  • JSON and streaming (file) requests with consistent error handling.
  • Standardized exceptions mapped to USPTO API HTTP response codes.
  • Convenience methods for direct URL downloads (e.g., Bulk API fileDownloadURI).

Endpoints throughout the SDK use this client to send requests.
All HTTP errors (400–500 range) raise typed exceptions such as:
  - BadRequestError
  - ForbiddenError
  - NotFoundError
  - PayloadTooLargeError
  - RateLimitError
  - ServerError

Usage
-----
>>> from ind.uspto.client import USPTOClient
>>> client = USPTOClient(api_key="YOUR_KEY")
>>> data = client.request_json("GET", "/api/v1/patent/status-codes")
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Deque
import time
import threading
from collections import deque

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .._version import __version__

DEFAULT_TIMEOUT = 30  # seconds

# =======================
# Exceptions
# =======================
class ApiError(Exception):
    """Base API error with optional server payload."""
    def __init__(self, message: str, status: int | None = None, payload: Any | None = None):
        super().__init__(message)
        self.status = status
        self.payload = payload


class BadRequestError(ApiError):       # 400
    pass


class ForbiddenError(ApiError):        # 403
    pass


class NotFoundError(ApiError):         # 404
    pass


class PayloadTooLargeError(ApiError):  # 413
    pass


class RateLimitError(ApiError):        # 429
    pass


class ServerError(ApiError):           # 5xx
    pass


# =======================
# Session builder
# =======================
def _build_session(api_key: Optional[str]) -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=2,                           # modest retries
        backoff_factor=5.0,                # 5s, then 10s
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST", "HEAD", "OPTIONS"),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    s.headers.update({
        "Accept": "application/json",
        "User-Agent": f"uspto-odp-sdk/{__version__} (+https://github.com/marczepeda/ind)",
    })
    if api_key:
        s.headers.update({"x-api-key": api_key})
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    return s


class _NullContext:
    def __enter__(self): return self
    def __exit__(self, *exc): return False


def _safe_json(resp: requests.Response) -> Any:
    try:
        return resp.json()
    except Exception:
        return None

def _format_error_message(status: int, reason: Optional[str], data: Optional[Dict[str, Any]]) -> str:
    # Pull most helpful details the API returns
    detail = None
    req_id = None
    if isinstance(data, dict):
        detail = data.get("errorDetails") or data.get("detailedMessage") or data.get("message") or data.get("error")
        req_id = data.get("requestIdentifier")

    parts = [f"HTTP {status}"]
    if reason:
        parts.append(reason)
    if detail:
        parts.append(f"- {detail}")
    if req_id:
        parts.append(f"(request id: {req_id})")

    return " ".join(parts)

# =======================
# Client
# =======================
@dataclass
class USPTOClient:
    """
    Shared HTTP client for the USPTO Open Data Portal (ODP).
    Provides JSON requests and streaming downloads with consistent error mapping.
    """
    base_url: str = "https://api.uspto.gov"
    timeout: int = DEFAULT_TIMEOUT
    api_key: Optional[str] = None
    session: Optional[requests.Session] = None
    serialize: bool = True  # serialize calls per API key

    def __post_init__(self):
        if self.session is None:
            self.session = _build_session(self.api_key)
        # concurrency guard and download rate limiter
        self._lock = threading.Lock()
        self._download_starts: Deque[float] = deque(maxlen=10_000)  # recent download starts
        self._per_file_counts: dict[str, int] = {}

    # -------------
    # Helpers
    # -------------
    def _url(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def _throttle_downloads(self) -> None:
        """Enforce ≤5 download starts per 10 seconds (bulk download guidance)."""
        now = time.time()
        window = 10.0
        limit = 5
        dq = self._download_starts
        # drop old timestamps
        while dq and now - dq[0] > window:
            dq.popleft()
        if len(dq) >= limit:
            sleep_for = window - (now - dq[0]) + 0.01
            time.sleep(max(0.0, sleep_for))
            # cleanup again after sleep
            now = time.time()
            while dq and now - dq[0] > window:
                dq.popleft()
        dq.append(time.time())

    # -------------
    # Low-level request
    # -------------
    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        stream: bool = False,
    ) -> requests.Response:
        url = self._url(path)
        ctx = (self._lock if self.serialize else _NullContext())
        with ctx:
            return self.session.request(
                method.upper(),
                url,
                params=params,
                json=json_body,
                timeout=self.timeout,
                stream=stream,
            )

    # -------------
    # JSON requests
    # -------------
    def request_json(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # first attempt
        resp = self.request(method, path, params=params, json_body=json_body, stream=False)
        data = _safe_json(resp)
        if resp.status_code == 200:
            return data if isinstance(data, dict) else {"_raw": data}
        # polite single retry for 429
        if resp.status_code == 429:
            time.sleep(5)
            resp = self.request(method, path, params=params, json_body=json_body, stream=False)
            data = _safe_json(resp)
            if resp.status_code == 200:
                return data if isinstance(data, dict) else {"_raw": data}
        # error
        self._raise_for_status(resp.status_code, data, resp.reason)
        raise ApiError("Unexpected error state")

    # -------------
    # Streaming downloads
    # -------------
    def download(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        dest_path: Optional[str] = None,
        chunk_bytes: int = 1024 * 1024,  # 1 MiB
    ) -> bytes | str:
        """
        Stream a file-like response. If dest_path is provided, saves to that path and
        returns the path; otherwise returns the bytes content.

        Raises the same typed errors as request_json on HTTP errors.
        """
        # Throttle *downloads* (covers petitions/patent search/download too; safe and courteous)
        self._throttle_downloads()

        # first attempt
        resp = self.request(method, path, params=params, json_body=json_body, stream=True)
        if resp.status_code == 429:
            time.sleep(5)
            resp = self.request(method, path, params=params, json_body=json_body, stream=True)

        if resp.status_code >= 400:
            # try to parse JSON error body
            data = _safe_json(resp)
            if data is None:
                data = {"message": resp.reason}
            self._raise_for_status(resp.status_code, data, resp.reason)

        if dest_path:
            with open(dest_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=chunk_bytes):
                    if chunk:
                        f.write(chunk)
            return dest_path

        return b"".join(resp.iter_content(chunk_size=chunk_bytes))

    def download_url(
        self,
        url: str,
        *,
        dest_path: Optional[str] = None,
        chunk_bytes: int = 1024 * 1024,   # 1 MiB
        headers: Optional[Mapping[str, Any]] = None,
    ) -> bytes | str:
        """
        Stream-download an absolute URL (e.g., a fileDownloadURI returned by the Bulk API).
        Uses the same session (API key, retries) as other requests.

        Returns:
            dest_path if provided, otherwise the bytes content.
        """
        # Throttle bulk downloads
        self._throttle_downloads()

        # best-effort same-file counter (helpful warnings; not persisted)
        key = url.split("?", 1)[0]
        count = self._per_file_counts.get(key, 0) + 1
        self._per_file_counts[key] = count
        if count == 15:
            print("[uspto_odp] Heads-up: you've downloaded this file ~15 times in this process.")
        elif count >= 20:
            print("[uspto_odp] WARNING: you may exceed the USPTO annual per-file limit (20/year per key).")

        # serialized fetch
        ctx = (self._lock if self.serialize else _NullContext())
        with ctx:
            resp = self.session.get(url, timeout=self.timeout, stream=True, headers=headers)

        if resp.status_code == 429:
            time.sleep(5)
            with ctx:
                resp = self.session.get(url, timeout=self.timeout, stream=True, headers=headers)

        if resp.status_code >= 400:
            data = _safe_json(resp)
            if data is None:
                data = {"message": resp.reason or f"HTTP {resp.status_code}"}
            self._raise_for_status(resp.status_code, data, resp.reason)

        if dest_path:
            with open(dest_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=chunk_bytes):
                    if chunk:
                        f.write(chunk)
            return dest_path

        return b"".join(resp.iter_content(chunk_size=chunk_bytes))

    # -------------
    # Error mapping
    # -------------
    @staticmethod
    def _raise_for_status(status: int, data: Optional[Dict[str, Any]], reason: Optional[str]) -> None:
        # Common fields returned by ODP:
        #   error, message, errorDetails, detailedMessage, requestIdentifier
        msg = _format_error_message(status, reason, data)

        if status == 400:
            raise BadRequestError(msg, status, data)
        if status == 403:
            raise ForbiddenError(msg, status, data)
        if status == 404:
            raise NotFoundError(msg, status, data)
        if status == 413:
            raise PayloadTooLargeError(msg, status, data)
        if status == 429:
            raise RateLimitError(msg, status, data)
        if status >= 500:
            raise ServerError(msg, status, data)
        raise ApiError(msg, status, data)
    
    serialize: bool = True  # new: serialize requests per client/key