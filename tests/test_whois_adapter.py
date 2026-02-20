from __future__ import annotations

import socket
from unittest.mock import patch, MagicMock

import pytest

from domain_engine.adapters.whois import WhoisAdapter
from domain_engine.exceptions import DomainCheckError


def _make_adapter(**kwargs) -> WhoisAdapter:
    return WhoisAdapter("de", "whois.denic.de", "status: free", **kwargs)


def _mock_whois(response: str):
    """Patch socket.create_connection to return a fake WHOIS response."""
    mock_sock = MagicMock()
    mock_sock.recv.side_effect = [response.encode(), b""]
    mock_sock.__enter__ = lambda s: s
    mock_sock.__exit__ = MagicMock(return_value=False)
    return patch("socket.create_connection", return_value=mock_sock)


def test_available_domain():
    with _mock_whois("% This is the DENIC whois\nStatus: free\n"):
        result = _make_adapter().check("xyznotreal123.de")
    assert result.available is True
    assert result.status == "available"


def test_registered_domain():
    with _mock_whois("Domain: example.de\nStatus: connect\n"):
        result = _make_adapter().check("example.de")
    assert result.available is False
    assert result.status == "registered"


def test_timeout():
    with patch("socket.create_connection", side_effect=socket.timeout("timed out")):
        with pytest.raises(DomainCheckError, match="timed out"):
            _make_adapter(timeout=0.1).check("example.de")


def test_connection_error():
    with patch("socket.create_connection", side_effect=OSError("Connection refused")):
        with pytest.raises(DomainCheckError, match="Connection refused"):
            _make_adapter().check("example.de")
