from __future__ import annotations

import pytest

from domain_engine.adapters.base import TLDAdapter
from domain_engine.engine import DomainCheckEngine, create_engine
from domain_engine.exceptions import InvalidDomainError, UnsupportedTLDError
from domain_engine.models import DomainCheckResult


class FakeAdapter(TLDAdapter):
    @property
    def tld(self) -> str:
        return "fake"

    def check(self, domain: str) -> DomainCheckResult:
        return DomainCheckResult(domain=domain, available=True, status="available")


class TestDomainNormalization:
    def test_strips_whitespace(self):
        engine = DomainCheckEngine()
        engine.register_adapter(FakeAdapter())
        result = engine.check("  test.fake  ")
        assert result.domain == "test.fake"

    def test_lowercases(self):
        engine = DomainCheckEngine()
        engine.register_adapter(FakeAdapter())
        result = engine.check("TEST.FAKE")
        assert result.domain == "test.fake"


class TestDomainValidation:
    def test_rejects_empty(self):
        engine = DomainCheckEngine()
        with pytest.raises(InvalidDomainError):
            engine.check("")

    def test_rejects_no_tld(self):
        engine = DomainCheckEngine()
        with pytest.raises(InvalidDomainError):
            engine.check("example")

    def test_rejects_leading_hyphen(self):
        engine = DomainCheckEngine()
        with pytest.raises(InvalidDomainError):
            engine.check("-example.com")

    def test_rejects_trailing_hyphen(self):
        engine = DomainCheckEngine()
        with pytest.raises(InvalidDomainError):
            engine.check("example-.com")


class TestTLDRouting:
    def test_routes_to_registered_adapter(self):
        engine = DomainCheckEngine()
        engine.register_adapter(FakeAdapter())
        result = engine.check("hello.fake")
        assert result.available is True

    def test_raises_for_unsupported_tld(self):
        engine = DomainCheckEngine()
        with pytest.raises(UnsupportedTLDError, match=r"\.xyz"):
            engine.check("hello.xyz")

    def test_supported_tlds(self):
        engine = DomainCheckEngine()
        engine.register_adapter(FakeAdapter())
        assert engine.supported_tlds == ["fake"]


class TestCreateEngine:
    def test_factory_has_com(self):
        engine = create_engine()
        assert "com" in engine.supported_tlds
