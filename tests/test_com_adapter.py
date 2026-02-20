from __future__ import annotations

import httpx
import pytest

from domain_engine.adapters.com import ComAdapter
from domain_engine.exceptions import DomainCheckError, RateLimitedError


def test_available_domain(httpx_mock):
    httpx_mock.add_response(status_code=404)
    adapter = ComAdapter()
    result = adapter.check("xyznotreal123.com")
    assert result.available is True
    assert result.status == "available"


def test_registered_domain(httpx_mock):
    body = {"objectClassName": "domain", "handle": "google.com"}
    httpx_mock.add_response(status_code=200, json=body)
    adapter = ComAdapter()
    result = adapter.check("google.com")
    assert result.available is False
    assert result.status == "registered"
    assert result.raw == body


def test_rate_limited(httpx_mock):
    httpx_mock.add_response(status_code=429)
    adapter = ComAdapter()
    with pytest.raises(RateLimitedError):
        adapter.check("example.com")


def test_unexpected_status(httpx_mock):
    httpx_mock.add_response(status_code=500)
    adapter = ComAdapter()
    with pytest.raises(DomainCheckError, match="500"):
        adapter.check("example.com")


def test_timeout(httpx_mock):
    httpx_mock.add_exception(httpx.ReadTimeout("timed out"))
    adapter = ComAdapter(timeout=0.1)
    with pytest.raises(DomainCheckError, match="timed out"):
        adapter.check("example.com")
