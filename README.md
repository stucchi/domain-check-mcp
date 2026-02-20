# domain-check-mcp

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)](https://www.python.org/)
![MCP Server](https://badge.mcpx.dev?type=server&features=tools 'Model Context Protocol Server')
[![MCP Enabled](https://badge.mcpx.dev?status=on 'MCP Enabled')](https://modelcontextprotocol.io)
[![Claude Compatible](https://img.shields.io/badge/Claude-Compatible-success.svg)](https://claude.ai/)
[![GitHub stars](https://img.shields.io/github/stars/stucchi/domain-check-mcp?style=social)](https://github.com/stucchi/domain-check-mcp/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/stucchi/domain-check-mcp)](https://github.com/stucchi/domain-check-mcp/issues)

MCP server for checking domain name availability. Supports 500+ TLDs via RDAP, with WHOIS fallback for .de and .cn.

## Installation

```bash
uvx domain-check-mcp
```

## Usage in .mcp.json

```json
{
  "mcpServers": {
    "domain-check": {
      "command": "uvx",
      "args": ["domain-check-mcp"]
    }
  }
}
```

## Tools

- **check_domain** — Check if a domain name is available for registration

### Example

```
check_domain("example.com")
```

Returns:

```json
{
  "domain": "example.com",
  "available": false,
  "status": "registered"
}
```

## Supported TLDs

### Via RDAP (500+)

All major gTLDs and many ccTLDs with RDAP support, sourced from the [IANA RDAP Bootstrap](https://data.iana.org/rdap/dns.json):

.com, .net, .org, .info, .app, .dev, .io, .xyz, .site, .shop, .uk, .fr, .nl, .pl, .consulting, .cloud, .tech, .blog, .store, .online, and [many more](src/domain_engine/tld_registry.py).

### Via WHOIS

| TLD | WHOIS Server |
|-----|-------------|
| .de | whois.denic.de |
| .cn | whois.cnnic.cn |

## How it works

1. Extracts the TLD from the domain name
2. Routes to the appropriate adapter (RDAP or WHOIS)
3. **RDAP**: HTTP lookup — 404 means available, 200 means registered
4. **WHOIS**: TCP port 43 lookup — pattern matching on the response
5. Returns a structured result with availability status

## Development

```bash
git clone https://github.com/stucchi/domain-check-mcp.git
cd domain-check-mcp
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## License

MIT
