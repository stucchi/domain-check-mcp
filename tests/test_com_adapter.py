from __future__ import annotations

import httpx
import pytest

from domain_engine.adapters.rdap import RDAPAdapter
from domain_engine.exceptions import DomainCheckError, RateLimitedError


def _com_adapter(**kwargs) -> RDAPAdapter:
    return RDAPAdapter("com", "https://rdap.verisign.com/com/v1", **kwargs)


def test_available_domain(httpx_mock):
    httpx_mock.add_response(status_code=404)
    result = _com_adapter().check("xyznotreal123.com")
    assert result.available is True
    assert result.status == "available"


def test_registered_domain(httpx_mock):
    body = {"objectClassName": "domain", "handle": "google.com"}
    httpx_mock.add_response(status_code=200, json=body)
    result = _com_adapter().check("google.com")
    assert result.available is False
    assert result.status == "registered"
    assert result.raw == body


def test_rate_limited(httpx_mock):
    httpx_mock.add_response(status_code=429)
    with pytest.raises(RateLimitedError):
        _com_adapter().check("example.com")


def test_unexpected_status(httpx_mock):
    httpx_mock.add_response(status_code=500)
    with pytest.raises(DomainCheckError, match="500"):
        _com_adapter().check("example.com")


def test_timeout(httpx_mock):
    httpx_mock.add_exception(httpx.ReadTimeout("timed out"))
    with pytest.raises(DomainCheckError, match="timed out"):
        _com_adapter(timeout=0.1).check("example.com")
