# Phoenix AI Builder Kit · OBA RUN Season 2

[한국어](../README.md) · [日本語](ja.md)

This repository is the participant guide and runnable example kit for **7 November 2026**. Manage your team account, keys and usage in the [developer portal](https://openapi.chickstockfi.com/en/login). Use the [API reference](https://openapi.chickstockfi.com/en/docs) for field definitions; the full reference also includes endpoints outside the Builder plan.

## Access and limits

| Item | Value |
| --- | --- |
| REST base | `https://api.chickstockfi.com/openapi/v1` |
| DATA MCP | `https://api.chickstockfi.com/openapi/v1/mcp` |
| Authentication | `Authorization: Bearer YOUR_TEAM_KEY` (`ck_live_…`) |
| Keys | Up to 2 active DATA keys per team; accounts are distributed through the organizers |
| Pre-event | From account activation until **2026-11-07 00:00 KST**, exclusive: **1,000 total requests, 10 RPM** |
| Event | **2026-11-07 00:00–2026-11-08 00:00 KST**, end exclusive: **10,000 total requests, 20 RPM** |
| Concurrency | 2 requests per team; an event-wide congestion limit also applies |

KST is UTC+09:00. All team keys, REST, MCP and reference-console calls share the allowance. Pre-event usage does not reduce the event allowance. Key rotation and crossing midnight do not reset a phase allowance. Data access ends at expiry, with no Free-plan fallback. `/key` and MCP initialization/tool discovery do not consume the DATA allowance; metadata rate limits still apply. Admitted requests can count even when returning 400/404. Check usage in the portal or `/key`.

## Included and excluded

Included: **KR quotes/daily prices**, KR/US financials, metrics, segments, dividends and filing-derived guidance; screeners and sector information; KR disclosure lists/text, US filing lists and **already published KR/US filing analyses**; US earnings calendars, KR IR/IPO calendars and supported economic/corporate events.

Prices, market caps and valuations embedded in screener/sector outputs may be used. **Direct US/JP quotes, price history and streaming are excluded**, as are Japanese market data, news/newswire, external consensus/analyst research, all PRO/newsroom access, new AI generation/translation and **all webhooks**. Builder uses DATA MCP, not PRO MCP or OAuth.

`POST /query` accepts **one query per request**. For a US screener:

```json
{"queries":[{"dataset":"screener","market":"US","limit":3}]}
```

`GET /disclosures` requires a KR `symbol`. Use `/us-filings` for SEC filings and `/earnings` for the **US** earnings calendar. `/symbols` is KR-only. Published analysis is available at `/disclosures/{id}/analysis`: use a 14-digit DART receipt or `TICKER:ACCESSION`, URL-encoded. Missing analyses return `404 ANALYSIS_NOT_AVAILABLE` and do not trigger generation. For US listings, `analysis=published` filters to published analyses.

## Quickstart

Clone the repository, copy `.env.example` to `.env`, and replace `YOUR_TEAM_KEY` locally. With Node.js 22+ or Python 3.11+, no packages are required:

```sh
git clone https://github.com/alpsofthq/phoenix-ai-builder-kit-obs.git
cd phoenix-ai-builder-kit-obs
cp .env.example .env
# Edit .env first, then load it in a macOS/Linux shell:
set -a
. ./.env
set +a
node examples/javascript/quickstart.mjs usage
python3 examples/python/quickstart.py disclosures 005930
```

PowerShell: set `$env:PHOENIX_DATA_KEY = 'YOUR_TEAM_KEY'` locally. Other commands: `quote 005930`, `financials AAPL`, `us-filings AAPL`, `screener US`, `earnings`, `analysis FILING_ID`. Each command sends one request, with a 20-second timeout and no automatic retries. Keep API keys on your server or local CLI, never in a public frontend bundle.

## MCP

Copy/merge [Claude Code config](../config/claude.mcp.json.example) into `.mcp.json`, or [Cursor config](../config/cursor.mcp.json.example) into `.cursor/mcp.json`. Start the app with `PHOENIX_DATA_KEY` in its environment. Claude uses `${PHOENIX_DATA_KEY}`; Cursor uses `${env:PHOENIX_DATA_KEY}`. Remote MCP does not automatically load this repo's `.env`. See [Claude documentation](https://code.claude.com/docs/en/mcp#environment-variable-expansion-in-mcpjson) and [Cursor documentation](https://cursor.com/docs/mcp#config-interpolation).

First ask: “Use get_api_usage to check my markets, remaining allowance and expiry.” Then: “Use list_disclosures with symbol=005930 and limit=2; do not generate new analysis.” Tool schemas and available tools are returned by `tools/list`. HTTP 200 can still contain a JSON-RPC error or `isError: true`.

## Errors, data and publication

- For 429, obey `Retry-After`; for 503, use a small bounded retry budget with increasing delays. Do not retry invalid requests, scope denials, missing analyses, exhausted phase quotas or expired access automatically.
- `BUILDER_SCOPE_DENIED` means out of scope; `BUILDER_SINGLE_QUERY` requires one query; `BUILDER_ENDED` means expired access. Inspect query `results[].ok`, not only HTTP status.
- Preserve dates, units, currency, source and `meta.as_of`. Missing values are not zero. Follow `next_cursor` with the same filters only when another page is needed.
- Allowed data may be used as external LLM input or MCP results for your event project. This does not permit new AI generation on Phoenix AI servers.
- Project code and screen demos may be public. Credit **Phoenix AI**. Do not publish keys, passwords, sessions, full raw responses, bulk dumps or redistributable datasets. Code availability does not grant redistribution rights over API data.
- Continued service operation or data redistribution after the event requires a separate agreement. [Terms](https://openapi.chickstockfi.com/en/terms) apply.

Public integration questions: [Issues](https://github.com/alpsofthq/phoenix-ai-builder-kit-obs/issues). Account/private issues or continued use: [contact](https://openapi.chickstockfi.com/en/request) or help@alpsoft.io. Include time, method/path, status, error code and request ID, **never credentials or full payloads**.

Verified 2026-11-04 · DATA API specification 1.18.0
