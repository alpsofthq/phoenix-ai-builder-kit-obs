import { test } from 'node:test';
import assert from 'node:assert/strict';
import { callApi, requestFor } from '../examples/javascript/quickstart.mjs';
const key = 'ck_live_synthetic_test_only';

test('examples use valid markets, required symbols and one query', () => {
  assert.match(requestFor(['disclosures', '005930']).path, /symbol=005930/);
  assert.throws(() => requestFor(['quote', 'AAPL']));
  assert.throws(() => requestFor(['screener', 'JP']));
  assert.equal(requestFor(['screener', 'US']).path, '/screener?market=US&limit=3');
  assert.equal(requestFor(['sectors', 'KR']).path, '/sectors?market=KR&limit=3');
  assert.match(requestFor(['analysis', 'TEST:0000000000-26-000001']).path, /TEST%3A/);
  assert.throws(() => requestFor(['analysis', '../key']));
  assert.equal(requestFor(['short-volume','005930']).path,'/companies/005930/short-selling?series=volume&limit=5');
  assert.equal(requestFor(['short-balance','AAPL']).path,'/companies/AAPL/short-selling?series=balance&limit=5');
  assert.throws(() => requestFor(['short-balance','../key']));
});

test('auth, timeout and redirect policy accompany a single request', async () => {
  let calls = 0;
  const data = await callApi(requestFor(['screener', 'US']), { key, fetchImpl: async (url, init) => {
    calls++;
    assert.equal(url, 'https://api.chickstockfi.com/openapi/v1/screener?market=US&limit=3');
    assert.equal(init.headers.Authorization, `Bearer ${key}`);
    assert.equal(init.redirect, 'error');
    assert.ok(init.signal instanceof AbortSignal);
    assert.equal(init.method, 'GET'); assert.equal(init.body, undefined);
    return Response.json({ results: [{ ok: true, data: [] }] });
  } });
  assert.equal(calls, 1);
  assert.equal(data.results[0].ok, true);
});

for (const status of [401, 403, 404, 410, 429, 503]) test(`HTTP ${status} is not retried or dumped`, async () => {
  let calls = 0;
  await assert.rejects(callApi(requestFor(['usage']), { key, fetchImpl: async () => {
    calls++;
    return Response.json({ error: { code: 'TEST_ERROR', message: key } }, { status, headers: { 'retry-after': '60', 'x-request-id': 'test-request' } });
  } }), (error) => {
    assert.match(error.message, new RegExp(`HTTP ${status}`));
    assert.match(error.message, /retry_after=60/);
    assert.ok(!error.message.includes(key));
    return true;
  });
  assert.equal(calls, 1);
});

test('HTTP 200 with a failed query is an error', async () => {
  await assert.rejects(callApi(requestFor(['screener', 'US']), { key, fetchImpl: async () => Response.json({ results: [{ ok: false, status: 'invalid_input' }] }) }), /Query did not succeed/);
});

test('network errors never expose a credential-bearing underlying error', async () => {
  await assert.rejects(callApi(requestFor(['usage']), { key, fetchImpl: async () => { throw new Error(key); } }), (error) => !error.message.includes(key));
});
