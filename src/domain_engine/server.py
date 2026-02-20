from __future__ import annotations

import json
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP

from domain_engine.engine import create_engine
from domain_engine.exceptions import DomainCheckError

mcp = FastMCP("domain-check")
engine = create_engine()


def _format(result: Any) -> str:
    return json.dumps(result, indent=2, ensure_ascii=False, default=str)


@mcp.tool()
async def check_domain(
    domain: Annotated[str, "The domain name to check (e.g. example.com)"],
) -> str:
    """Check if a domain name is available for registration.

    Currently supports .com domains via RDAP lookup.
    """
    try:
        result = engine.check(domain)
    except DomainCheckError as exc:
        return _format({"error": str(exc)})

    return _format(result.to_dict())


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
