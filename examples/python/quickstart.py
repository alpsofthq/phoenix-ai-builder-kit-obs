"""Python 3.11+. One request per command; standard library only, no automatic retries."""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.chickstockfi.com/openapi/v1"
HELP = "usage | quote KR_CODE | financials SYMBOL | short-volume SYMBOL | short-balance SYMBOL | disclosures KR_CODE | us-filings TICKER | screener KR|US | earnings | analysis FILING_ID"


def request_for(args):
    command = args[0] if args else "usage"
    argument = args[1] if len(args) == 2 else ""
    if len(args) > 2:
        raise ValueError("Too many arguments. Run with --help.")

    def match(pattern, label):
        if not re.fullmatch(pattern, argument):
            raise ValueError(f"Invalid {label}. Run with --help.")
        return argument

    if command in ("usage", "earnings"):
        if argument:
            raise ValueError("This command takes no argument.")
        return ("/key" if command == "usage" else "/earnings?limit=3", None)
    if command == "quote":
        return (f"/quotes/{match(r'[0-9A-Z]{6}', 'KR code')}", None)
    if command == "financials":
        symbol = match(r"[A-Za-z0-9.\-]{1,12}", "symbol")
        return (f"/companies/{symbol}/financials?account=revenue,operating_income&limit=8", None)
    if command in ("short-volume", "short-balance"):
        symbol = match(r"[A-Za-z0-9.\-]{1,12}", "symbol")
        series = "volume" if command == "short-volume" else "balance"
        return (f"/companies/{symbol}/short-selling?series={series}&limit=5", None)
    if command == "disclosures":
        return (f"/disclosures?symbol={match(r'[0-9A-Z]{6}', 'KR code')}&limit=2", None)
    if command == "us-filings":
        symbol = match(r"[A-Za-z][A-Za-z0-9.\-]{0,11}", "US ticker")
        return (f"/us-filings?symbol={symbol}&limit=2", None)
    if command == "screener":
        return ("/query", {"queries": [{"dataset": "screener", "market": match(r"KR|US", "market"), "limit": 3}]})
    if command == "analysis":
        identifier = match(r"(?:\d{14}|[A-Za-z0-9.\-]+:\d{10}-\d{2}-\d{6})", "filing ID")
        return (f"/disclosures/{urllib.parse.quote(identifier, safe='')}/analysis", None)
    raise ValueError(f"Unknown command. {HELP}")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Do not forward the Authorization header to a redirect destination."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def safe(value):
    return re.sub(r"[^A-Za-z0-9_:.+ /-]", "", str(value if value is not None else "-"))[:120]


def call_api(request, key=None, opener=None):
    key = key if key is not None else os.environ.get("PHOENIX_DATA_KEY", "")
    if not key.startswith("ck_live_") or re.search(r"\s", key):
        raise ValueError("Set PHOENIX_DATA_KEY to your team DATA key (ck_live_…).")
    path, body = request
    if not path.startswith("/") or path.startswith("//"):
        raise ValueError("Expected a relative API path.")
    headers = {"Authorization": f"Bearer {key}", "Accept": "application/json", "User-Agent": "api-client-example/1.0"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers=headers, method="POST" if body is not None else "GET")
    opener = opener or urllib.request.build_opener(NoRedirect())
    try:
        response = opener.open(req, timeout=20)
    except urllib.error.HTTPError as error:
        response = error
    except (urllib.error.URLError, TimeoutError, OSError):
        raise RuntimeError("Network, TLS or timeout error. No automatic retry; check your connection.") from None
    with response:
        status = response.status
        request_id = safe(response.headers.get("x-request-id"))
        retry_after = safe(response.headers.get("retry-after"))
        try:
            data = json.loads(response.read())
        except (ValueError, UnicodeError):
            raise RuntimeError(f"HTTP {status}: non-JSON response. Request ID: {request_id}") from None
    error = data.get("error") if isinstance(data, dict) else None
    if not 200 <= status < 300 or error:
        code = safe(error.get("code") if isinstance(error, dict) else None)
        raise RuntimeError(f"HTTP {status}; code={code}; request_id={request_id}; retry_after={retry_after}")
    nested = data.get("data") if isinstance(data, dict) else None
    results = data.get("results", nested.get("results") if isinstance(nested, dict) else None) if isinstance(data, dict) else None
    if isinstance(results, list) and any(isinstance(row, dict) and row.get("ok") is False for row in results):
        raise RuntimeError("Query did not succeed. Check the dataset, market and inputs; no automatic retry.")
    return data


if __name__ == "__main__":
    if "--help" in sys.argv:
        print(HELP)
    else:
        try:
            print(json.dumps(call_api(request_for(sys.argv[1:])), ensure_ascii=False, indent=2))
        except (ValueError, RuntimeError) as error:
            print(str(error), file=sys.stderr)
            sys.exit(1)
