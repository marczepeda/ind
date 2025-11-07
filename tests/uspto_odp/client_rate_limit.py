'''
tests/uspto_odp/client_rate_limit.py — USPTO Open Data Portal Client Rate Limit Tests
Date: 2025-11-02

Usage:
  python tests/uspto_odp/client_rate_limit.py

Notes:
  • These tests verify the behavior of the USPTOClient when rate limits are exceeded.
  • They simulate various scenarios to ensure the client handles rate limits gracefully.
  • Output is human-readable; redirect to a file if you want an artifact.
'''

import io
import time
import types
import pytest
from unittest.mock import MagicMock, patch
from ind.uspto_odp.client import USPTOClient, RateLimitError
import contextlib


class DummyResp:
    """Fake response object mimicking requests.Response."""
    def __init__(self, status_code=200, data=None, reason="OK", content=b""):
        self.status_code = status_code
        self._data = data or {}
        self.reason = reason
        self._content = content
        self._iter = [content]

    def json(self):
        if self._data is None:
            raise ValueError("no json")
        return self._data

    def iter_content(self, chunk_size=1024):
        yield self._content


def test_request_json_retries_on_429(monkeypatch):
    """Should sleep 5s once and retry exactly once on 429."""
    client = USPTOClient()

    # mock session.request to return 429 once, then 200
    call_count = {"n": 0}

    def fake_request(method, url, **kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return DummyResp(status_code=429, data={"error": "Too Many Requests"})
        return DummyResp(status_code=200, data={"ok": True})

    client.session.request = fake_request

    with patch("time.sleep", return_value=None) as sleep_mock:
        result = client.request_json("GET", "/test")

    assert result == {"ok": True}
    assert call_count["n"] == 2, "should retry exactly once"
    sleep_mock.assert_called_once_with(5)


def test_throttle_downloads(monkeypatch):
    """Throttle should delay when >5 downloads started within 10s."""
    client = USPTOClient()
    now = time.time()
    # fill deque with 5 timestamps all within the 10s window
    client._download_starts.extend([now - 1, now - 2, now - 3, now - 4, now - 5])

    with patch("time.sleep", wraps=lambda x: None) as sleep_mock:
        client._throttle_downloads()
    # after throttling, the deque should have 6 timestamps
    assert len(client._download_starts) == 6
    sleep_mock.assert_called_once()
    args, _ = sleep_mock.call_args
    assert args[0] >= 0  # should have slept some positive duration


def test_download_url_warns_after_20(monkeypatch, capsys):
    """Should warn after ~15 and 20 downloads of the same file."""
    client = USPTOClient()
    # mock network get to always return DummyResp
    client.session.get = lambda *a, **kw: DummyResp(status_code=200, content=b"ok")

    with patch.object(client, "_throttle_downloads", return_value=None):
        for i in range(21):
            client.download_url("https://example.com/file.zip")

    out = capsys.readouterr().out
    assert "Heads-up" in out
    assert "20/year" in out

# -----------------------------
# Standalone "demo" runners
# -----------------------------
def demo_request_json_retries_on_429():
    """
    Run outside pytest: demonstrate that a 429 triggers one retry after a 5s sleep.
    Prints a short PASS/FAIL summary.
    """
    print("\n[DEMO] request_json retries on 429")
    client = USPTOClient()

    call_count = {"n": 0}

    def fake_request(method, url, **kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return DummyResp(status_code=429, data={"error": "Too Many Requests"})
        return DummyResp(status_code=200, data={"ok": True})

    # monkey-patch request + sleep without pytest
    client.session.request = fake_request
    with patch("time.sleep", return_value=None) as sleep_mock:
        result = client.request_json("GET", "/test")

    passed = (result == {"ok": True} and call_count["n"] == 2 and sleep_mock.call_count == 1)
    print(f"result={result}, calls={call_count['n']}, slept={sleep_mock.call_args}")
    print("PASS" if passed else "FAIL")


def demo_throttle_downloads():
    """
    Run outside pytest: demonstrate that throttling sleeps when >5 downloads in 10s window.
    Prints a short PASS/FAIL summary.
    """
    print("\n[DEMO] throttle_downloads enforces ≤5 starts/10s")
    client = USPTOClient()
    now = time.time()
    client._download_starts.clear()
    client._download_starts.extend([now - 1, now - 2, now - 3, now - 4, now - 5])

    with patch("time.sleep", wraps=lambda x: None) as sleep_mock:
        client._throttle_downloads()

    passed = (len(client._download_starts) == 6 and sleep_mock.call_count == 1)
    print(f"starts={len(client._download_starts)}, slept={sleep_mock.call_args}")
    print("PASS" if passed else "FAIL")


def demo_download_url_warns_after_20():
    """
    Run outside pytest: demonstrate heads-up and warning messages after repeated downloads.
    Captures stdout and prints the captured output.
    """
    print("\n[DEMO] download_url emits heads-up and warning after many downloads")
    client = USPTOClient()
    client.session.get = lambda *a, **kw: DummyResp(status_code=200, content=b"ok")

    # Avoid real sleeping in throttler
    with patch.object(client, "_throttle_downloads", return_value=None):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            for _ in range(21):
                client.download_url("https://example.com/file.zip")
        out = buf.getvalue()

    print("Captured output:")
    print(out.strip())
    passed = ("Heads-up" in out and "20/year" in out)
    print("PASS" if passed else "FAIL")


if __name__ == "__main__":
    print("uspto_odp.client rate-limit demos")
    print("This file can be run directly to produce human-readable output,")
    print("or executed via pytest to run the unit tests.\n")

    try:
        demo_request_json_retries_on_429()
    except Exception as e:
        print(f"[DEMO] request_json_retries_on_429 raised: {e}")

    try:
        demo_throttle_downloads()
    except Exception as e:
        print(f"[DEMO] throttle_downloads raised: {e}")

    try:
        demo_download_url_warns_after_20()
    except Exception as e:
        print(f"[DEMO] download_url_warns_after_20 raised: {e}")