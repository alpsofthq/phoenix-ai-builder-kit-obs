// Node.js 22+. One request per command; no dependencies or automatic retries.
import { pathToFileURL } from 'node:url';

const BASE = 'https://api.chickstockfi.com/openapi/v1';
const HELP = 'usage | quote KR_CODE | financials SYMBOL | short-volume SYMBOL | short-balance SYMBOL | disclosures KR_CODE | us-filings TICKER | screener KR|US | sectors KR|US | earnings | analysis FILING_ID';

function requireMatch(value, pattern, label) {
  if (!pattern.test(value ?? '')) throw new Error(`Invalid ${label}. Run with --help.`);
  return value;
}

export function requestFor([command = 'usage', argument, ...extra] = []) {
  if (extra.length) throw new Error('Too many arguments. Run with --help.');
  const one = () => { if (argument) throw new Error('This command takes no argument.'); };
  switch (command) {
    case 'usage': one(); return { path: '/key' };
    case 'quote': return { path: `/quotes/${requireMatch(argument, /^[0-9A-Z]{6}$/, 'KR code')}` };
    case 'financials': return { path: `/companies/${requireMatch(argument, /^[A-Za-z0-9.\-]{1,12}$/, 'symbol')}/financials?account=revenue,operating_income&limit=8` };
    case 'short-volume':
    case 'short-balance': return { path: `/companies/${requireMatch(argument, /^[A-Za-z0-9.\-]{1,12}$/, 'symbol')}/short-selling?series=${command === 'short-volume' ? 'volume' : 'balance'}&limit=5` };
    case 'disclosures': return { path: `/disclosures?symbol=${requireMatch(argument, /^[0-9A-Z]{6}$/, 'KR code')}&limit=2` };
    case 'us-filings': return { path: `/us-filings?symbol=${requireMatch(argument, /^[A-Za-z][A-Za-z0-9.\-]{0,11}$/, 'US ticker')}&limit=2` };
    case 'screener':
    case 'sectors': return { path: `/${command}?market=${requireMatch(argument, /^(KR|US)$/, 'market')}&limit=3` };
    case 'earnings': one(); return { path: '/earnings?limit=3' };
    case 'analysis': return { path: `/disclosures/${encodeURIComponent(requireMatch(argument, /^(?:\d{14}|[A-Za-z0-9.\-]+:\d{10}-\d{2}-\d{6})$/, 'filing ID'))}/analysis` };
    default: throw new Error(`Unknown command. ${HELP}`);
  }
}

// Error fields are deliberately limited: never print headers, tokens or raw error bodies.
function safe(value) { return String(value ?? '-').replace(/[^A-Za-z0-9_:.+ /-]/g, '').slice(0, 120); }
export async function callApi(request, { key = process.env.PHOENIX_DATA_KEY, fetchImpl = fetch } = {}) {
  if (!key?.startsWith('ck_live_') || /\s/.test(key)) throw new Error('Set PHOENIX_DATA_KEY to your team DATA key (ck_live_…).');
  if (!request.path.startsWith('/') || request.path.startsWith('//')) throw new Error('Expected a relative API path.');
  let response;
  try {
    response = await fetchImpl(`${BASE}${request.path}`, {
      method: request.body ? 'POST' : 'GET',
      headers: { Authorization: `Bearer ${key}`, Accept: 'application/json', 'User-Agent': 'api-client-example/1.0', ...(request.body ? { 'Content-Type': 'application/json' } : {}) },
      body: request.body ? JSON.stringify(request.body) : undefined,
      redirect: 'error',
      signal: AbortSignal.timeout(20_000),
    });
  } catch { throw new Error('Network, TLS, redirect or timeout error. No automatic retry; check your connection.'); }
  let data;
  try { data = await response.json(); }
  catch { throw new Error(`HTTP ${response.status}: non-JSON response. Request ID: ${safe(response.headers.get('x-request-id'))}`); }
  if (!response.ok || data?.error) {
    throw new Error(`HTTP ${response.status}; code=${safe(data?.error?.code)}; request_id=${safe(response.headers.get('x-request-id'))}; retry_after=${safe(response.headers.get('retry-after'))}`);
  }
  const results = data?.results ?? data?.data?.results;
  if (Array.isArray(results) && results.some(r => r?.ok === false)) {
    throw new Error(`Query did not succeed: ${results.filter(r => r?.ok === false).map(r => safe(r.error?.code ?? r.error ?? r.status)).join(', ')}. Check the dataset and inputs.`);
  }
  return data;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  if (process.argv.includes('--help')) console.log(HELP);
  else {
    try { console.log(JSON.stringify(await callApi(requestFor(process.argv.slice(2))), null, 2)); }
    catch (error) { console.error(error.message); process.exitCode = 1; }
  }
}
