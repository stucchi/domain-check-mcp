from __future__ import annotations

import json
from typing import Annotated, Any

from mcp import types
from mcp.server.fastmcp import FastMCP

from domain_engine.engine import create_engine
from domain_engine.exceptions import DomainCheckError

_VIEW_URI = "ui://domain-check/view.html"
_BULK_VIEW_URI = "ui://domain-check/bulk-view.html"

mcp = FastMCP("domain-check")
engine = create_engine()


def _format(result: Any) -> str:
    return json.dumps(result, indent=2, ensure_ascii=False, default=str)


@mcp.resource(
    _VIEW_URI,
    mime_type="text/html;profile=mcp-app",
    meta={"ui": {"csp": {"resourceDomains": ["https://unpkg.com"]}}},
)
def domain_check_view() -> str:
    return _VIEW_HTML


@mcp.tool(meta={
    "ui": {"resourceUri": _VIEW_URI},
    "ui/resourceUri": _VIEW_URI,
})
async def check_domain(
    domain: Annotated[str, "The domain name to check (e.g. example.com)"],
) -> types.CallToolResult:
    """Check if a domain name is available for registration.

    Supports 500+ TLDs via RDAP (including .com, .net, .org, .app, .dev, .io, and many more) plus .de and .cn via WHOIS.
    """
    try:
        result = engine.check(domain)
    except DomainCheckError as exc:
        error_data = {"error": str(exc)}
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=_format(error_data))],
            structured_content=error_data,
            is_error=True,
        )

    data = result.to_dict()
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=_format(data))],
        structured_content=data,
    )


@mcp.resource(
    _BULK_VIEW_URI,
    mime_type="text/html;profile=mcp-app",
    meta={"ui": {"csp": {"resourceDomains": ["https://unpkg.com"]}}},
)
def bulk_check_view() -> str:
    return _BULK_VIEW_HTML


@mcp.tool(meta={
    "ui": {"resourceUri": _BULK_VIEW_URI},
    "ui/resourceUri": _BULK_VIEW_URI,
})
async def check_domains(
    domains: Annotated[list[str], "List of domain names to check (e.g. ['example.com', 'example.net'])"],
) -> types.CallToolResult:
    """Check multiple domain names for availability in bulk.

    Accepts a list of domains and returns the availability status of each one.
    Supports 500+ TLDs via RDAP and additional TLDs via WHOIS.
    """
    results = []
    for domain in domains:
        try:
            result = engine.check(domain)
            results.append(result.to_dict())
        except DomainCheckError as exc:
            results.append({"domain": domain, "available": None, "status": "error", "error": str(exc)})

    summary = {
        "total": len(results),
        "available": sum(1 for r in results if r.get("available") is True),
        "registered": sum(1 for r in results if r.get("available") is False),
        "errors": sum(1 for r in results if r.get("status") == "error"),
    }

    data = {"results": results, "summary": summary}

    return types.CallToolResult(
        content=[types.TextContent(type="text", text=_format(data))],
        structured_content=data,
    )


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# Embedded MCP App view – self-contained HTML rendered by hosts that support
# the MCP Apps extension (io.modelcontextprotocol/ui).  Hosts without support
# fall back to the text content returned above.
# ---------------------------------------------------------------------------

_BULK_VIEW_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  :root { color-scheme: light dark; }
  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: var(--font-sans, system-ui, -apple-system, sans-serif);
    color: light-dark(#1a1a2e, #e4e4e7);
    background: transparent;
    padding: 12px;
  }

  .card {
    border: 1px solid light-dark(#e4e4e7, #3f3f46);
    border-radius: 12px;
    overflow: hidden;
    max-width: 560px;
  }

  /* Summary bar */
  .summary {
    display: flex;
    gap: 0;
    border-bottom: 1px solid light-dark(#e4e4e7, #3f3f46);
  }

  .summary-item {
    flex: 1;
    padding: 14px 12px;
    text-align: center;
    border-right: 1px solid light-dark(#e4e4e7, #3f3f46);
  }

  .summary-item:last-child { border-right: none; }

  .summary-num {
    font-size: 22px;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 3px;
  }

  .summary-label {
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: light-dark(#71717a, #a1a1aa);
  }

  .summary-item.s-available .summary-num { color: light-dark(#16a34a, #4ade80); }
  .summary-item.s-registered .summary-num { color: light-dark(#dc2626, #f87171); }
  .summary-item.s-errors .summary-num { color: light-dark(#d97706, #fbbf24); }

  /* Results table */
  .results {
    max-height: 400px;
    overflow-y: auto;
  }

  .row {
    display: flex;
    align-items: center;
    padding: 10px 16px;
    gap: 12px;
    border-bottom: 1px solid light-dark(#f4f4f5, #27272a);
  }

  .row:last-child { border-bottom: none; }

  .row-icon {
    font-size: 18px;
    flex-shrink: 0;
    width: 24px;
    text-align: center;
  }

  .row.r-available .row-icon { color: light-dark(#16a34a, #4ade80); }
  .row.r-registered .row-icon { color: light-dark(#dc2626, #f87171); }
  .row.r-error .row-icon { color: light-dark(#d97706, #fbbf24); }

  .row-domain {
    flex: 1;
    font-family: var(--font-mono, ui-monospace, monospace);
    font-size: 14px;
    font-weight: 600;
    word-break: break-all;
  }

  .row-status {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    flex-shrink: 0;
  }

  .row.r-available .row-status { color: light-dark(#16a34a, #4ade80); }
  .row.r-registered .row-status { color: light-dark(#dc2626, #f87171); }
  .row.r-error .row-status { color: light-dark(#d97706, #fbbf24); }

  /* Loading */
  .loading {
    padding: 32px;
    text-align: center;
    color: light-dark(#71717a, #a1a1aa);
    font-size: 14px;
  }

  .spinner {
    display: inline-block;
    width: 22px;
    height: 22px;
    border: 2.5px solid light-dark(#e4e4e7, #3f3f46);
    border-top-color: light-dark(#2563eb, #60a5fa);
    border-radius: 50%;
    animation: spin .7s linear infinite;
    margin-bottom: 10px;
  }

  @keyframes spin { to { transform: rotate(360deg); } }
</style>
</head>
<body>
<div class="card">
  <div id="content">
    <div class="loading">
      <div class="spinner"></div>
      <div>Checking domains&#8230;</div>
    </div>
  </div>
</div>

<script type="module">
import { App } from "https://unpkg.com/@modelcontextprotocol/ext-apps@1.1.2/dist/src/app-with-deps.js";

var app = new App(
  { name: "Bulk Domain Check", version: "1.0.0" },
  {},
  { autoResize: true }
);

function esc(s) {
  var d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

function renderSummary(summary) {
  return '<div class="summary">' +
    '<div class="summary-item"><div class="summary-num">' + summary.total + '</div><div class="summary-label">Total</div></div>' +
    '<div class="summary-item s-available"><div class="summary-num">' + summary.available + '</div><div class="summary-label">Available</div></div>' +
    '<div class="summary-item s-registered"><div class="summary-num">' + summary.registered + '</div><div class="summary-label">Registered</div></div>' +
    (summary.errors > 0 ? '<div class="summary-item s-errors"><div class="summary-num">' + summary.errors + '</div><div class="summary-label">Errors</div></div>' : '') +
  '</div>';
}

function renderRows(results) {
  var html = '<div class="results">';
  for (var i = 0; i < results.length; i++) {
    var r = results[i];
    var cls, icon, label;
    if (r.status === "error") {
      cls = "r-error"; icon = "&#9888;"; label = r.error || "error";
    } else if (r.available) {
      cls = "r-available"; icon = "&#10003;"; label = "available";
    } else {
      cls = "r-registered"; icon = "&#10007;"; label = "registered";
    }
    html += '<div class="row ' + cls + '">' +
      '<div class="row-icon">' + icon + '</div>' +
      '<div class="row-domain">' + esc(r.domain) + '</div>' +
      '<div class="row-status">' + esc(label) + '</div>' +
    '</div>';
  }
  html += '</div>';
  return html;
}

function render(data) {
  var el = document.getElementById("content");
  var results = data.results || [];
  var summary = data.summary || {
    total: results.length,
    available: results.filter(function(r) { return r.available === true; }).length,
    registered: results.filter(function(r) { return r.available === false; }).length,
    errors: results.filter(function(r) { return r.status === "error"; }).length
  };
  el.innerHTML = renderSummary(summary) + renderRows(results);
}

function showLoading(msg) {
  document.getElementById("content").innerHTML =
    '<div class="loading"><div class="spinner"></div><div>' + esc(msg || "Checking domains...") + '</div></div>';
}

app.ontoolinput = function() { showLoading("Checking domains..."); };

app.ontoolresult = function(result) {
  var data = result.structuredContent;
  if (!data && result.content && result.content[0]) {
    try { data = JSON.parse(result.content[0].text); } catch(e) { data = { results: [] }; }
  }
  render(data || { results: [] });
};

app.onhostcontextchanged = function(ctx) {
  if (ctx.theme) document.documentElement.style.colorScheme = ctx.theme;
};

await app.connect();
</script>
</body>
</html>
"""

_VIEW_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  :root { color-scheme: light dark; }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: var(--font-sans, system-ui, -apple-system, sans-serif);
    color: light-dark(#1a1a2e, #e4e4e7);
    background: transparent;
    padding: 12px;
  }

  .card {
    border: 1px solid light-dark(#e4e4e7, #3f3f46);
    border-radius: 12px;
    overflow: hidden;
    max-width: 420px;
  }

  /* Result states */
  .result {
    padding: 28px 24px;
    text-align: center;
  }

  .result.available {
    background: light-dark(#f0fdf4, #052e16);
    border-bottom: 3px solid light-dark(#16a34a, #4ade80);
  }

  .result.registered {
    background: light-dark(#fef2f2, #450a0a);
    border-bottom: 3px solid light-dark(#dc2626, #f87171);
  }

  .result.error {
    background: light-dark(#fffbeb, #451a03);
    border-bottom: 3px solid light-dark(#d97706, #fbbf24);
  }

  .status-icon {
    font-size: 44px;
    line-height: 1;
    margin-bottom: 10px;
  }

  .available .status-icon { color: light-dark(#16a34a, #4ade80); }
  .registered .status-icon { color: light-dark(#dc2626, #f87171); }
  .error .status-icon { color: light-dark(#d97706, #fbbf24); }

  .domain-name {
    font-family: var(--font-mono, ui-monospace, monospace);
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 6px;
    word-break: break-all;
  }

  .status-label {
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
  }

  .available .status-label { color: light-dark(#16a34a, #4ade80); }
  .registered .status-label { color: light-dark(#dc2626, #f87171); }
  .error .status-label { color: light-dark(#d97706, #fbbf24); }

  .tld-info {
    margin-top: 10px;
    font-size: 12px;
    color: light-dark(#71717a, #a1a1aa);
  }

  /* Loading */
  .loading {
    padding: 32px;
    text-align: center;
    color: light-dark(#71717a, #a1a1aa);
    font-size: 14px;
  }

  .spinner {
    display: inline-block;
    width: 22px;
    height: 22px;
    border: 2.5px solid light-dark(#e4e4e7, #3f3f46);
    border-top-color: light-dark(#2563eb, #60a5fa);
    border-radius: 50%;
    animation: spin .7s linear infinite;
    margin-bottom: 10px;
  }

  @keyframes spin { to { transform: rotate(360deg); } }
</style>
</head>
<body>
<div class="card">
  <div id="content">
    <div class="loading">
      <div class="spinner"></div>
      <div>Checking domain&#8230;</div>
    </div>
  </div>
</div>

<script type="module">
import { App } from "https://unpkg.com/@modelcontextprotocol/ext-apps@1.1.2/dist/src/app-with-deps.js";

var app = new App(
  { name: "Domain Check", version: "1.0.0" },
  {},
  { autoResize: true }
);

function esc(s) {
  var d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

function render(data) {
  var el = document.getElementById("content");

  if (data.error) {
    el.innerHTML =
      '<div class="result error">' +
        '<div class="status-icon">&#9888;</div>' +
        '<div class="domain-name">' + esc(data.domain || "") + '</div>' +
        '<div class="status-label">' + esc(data.error) + '</div>' +
      '</div>';
    return;
  }

  var cls = data.available ? "available" : "registered";
  var icon = data.available ? "&#10003;" : "&#10007;";
  var label = data.available ? "Available" : "Registered";
  var tld = "." + data.domain.split(".").pop();

  el.innerHTML =
    '<div class="result ' + cls + '">' +
      '<div class="status-icon">' + icon + '</div>' +
      '<div class="domain-name">' + esc(data.domain) + '</div>' +
      '<div class="status-label">' + label + '</div>' +
      '<div class="tld-info">TLD: ' + esc(tld) + '</div>' +
    '</div>';
}

app.ontoolinput = function() {
  document.getElementById("content").innerHTML =
    '<div class="loading"><div class="spinner"></div><div>Checking domain&#8230;</div></div>';
};

app.ontoolresult = function(result) {
  var data = result.structuredContent;
  if (!data && result.content && result.content[0]) {
    try { data = JSON.parse(result.content[0].text); } catch(e) { data = {}; }
  }
  render(data || {});
};

app.onhostcontextchanged = function(ctx) {
  if (ctx.theme) document.documentElement.style.colorScheme = ctx.theme;
};

await app.connect();
</script>
</body>
</html>
"""
