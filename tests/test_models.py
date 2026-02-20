from __future__ import annotations

from domain_engine.models import DomainCheckResult


def test_available_result():
    result = DomainCheckResult(domain="example.com", available=True, status="available")
    assert result.domain == "example.com"
    assert result.available is True
    assert result.status == "available"
    assert result.raw is None


def test_registered_result_with_raw():
    raw = {"objectClassName": "domain", "handle": "example.com"}
    result = DomainCheckResult(
        domain="example.com", available=False, status="registered", raw=raw
    )
    assert result.available is False
    assert result.raw is raw


def test_to_dict_excludes_raw():
    result = DomainCheckResult(
        domain="example.com",
        available=False,
        status="registered",
        raw={"some": "data"},
    )
    d = result.to_dict()
    assert d == {
        "domain": "example.com",
        "available": False,
        "status": "registered",
    }
    assert "raw" not in d
