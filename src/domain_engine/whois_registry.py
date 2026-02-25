from __future__ import annotations

# WHOIS fallback registry for TLDs without working RDAP.
# Each entry: tld -> (whois_server, not_found_pattern)

WHOIS_REGISTRY: dict[str, tuple[str, str]] = {
    # ccTLDs without RDAP
    "it": ("whois.nic.it", "AVAILABLE"),
    "eu": ("whois.eu", "Status: AVAILABLE"),
    "ie": ("whois.weare.ie", "Not found:"),
    "at": ("whois.nic.at", "nothing found"),
    "se": ("whois.iis.se", "not found"),
    "dk": ("whois.punktum.dk", "No entries found"),
    "pt": ("whois.dns.pt", "No Match"),
    "be": ("whois.dns.be", "Status:\tAVAILABLE"),
    "de": ("whois.denic.de", "status: free"),
    "cn": ("whois.cnnic.cn", "no matching record"),
    "co": ("whois.registry.co", "domain not found"),
    "io": ("whois.nic.io", "domain not found"),
    "me": ("whois.nic.me", "domain not found"),
    "sh": ("whois.nic.sh", "Domain not found."),
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
