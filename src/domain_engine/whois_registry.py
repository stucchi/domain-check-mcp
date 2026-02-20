from __future__ import annotations

# WHOIS fallback registry for TLDs without working RDAP.
# Each entry: tld -> (whois_server, not_found_pattern)

WHOIS_REGISTRY: dict[str, tuple[str, str]] = {
    # ccTLDs without RDAP
    "de": ("whois.denic.de", "status: free"),
    "cn": ("whois.cnnic.cn", "no matching record"),
    # TLDs whose RDAP server is unreachable — WHOIS works
    "fj": ("www.whois.fj", "does not exist"),
    "gs": ("whois.nic.gs", "does not exist"),
    "bayern": ("whois.nic.bayern", "does not exist"),
    "cat": ("whois.nic.cat", "does not exist"),
    "eus": ("whois.nic.eus", "does not exist"),
    "radio": ("whois.nic.radio", "does not exist"),
    "scot": ("whois.nic.scot", "does not exist"),
    "sport": ("whois.nic.sport", "does not exist"),
}
