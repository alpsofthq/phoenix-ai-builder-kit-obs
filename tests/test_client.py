import importlib.util
import io
import json
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("quickstart", Path(__file__).parents[1] / "examples/python/quickstart.py")
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)
KEY = "ck_live_synthetic_test_only"


class Reply(io.BytesIO):
    def __init__(self, status, body):
        super().__init__(json.dumps(body).encode())
        self.status = status
        self.headers = {"retry-after": "60", "x-request-id": "test-request"}


class ClientTests(unittest.TestCase):
    def test_paths(self):
        self.assertIn("symbol=005930", client.request_for(["disclosures", "005930"])[0])
        self.assertIn("TEST%3A", client.request_for(["analysis", "TEST:0000000000-26-000001"])[0])
        self.assertEqual(len(client.request_for(["screener", "US"])[1]["queries"]), 1)
        self.assertEqual(client.request_for(["short-volume", "005930"]), ("/companies/005930/short-selling?series=volume&limit=5", None))
        self.assertEqual(client.request_for(["short-balance", "AAPL"]), ("/companies/AAPL/short-selling?series=balance&limit=5", None))
        for args in [["quote", "AAPL"], ["screener", "JP"], ["analysis", "../key"]]:
            with self.assertRaises(ValueError):
                client.request_for(args)

    def test_no_redirect(self):
        self.assertIsNone(client.NoRedirect().redirect_request(None, None, 302, "", {}, "https://example.com"))

    def test_single_authenticated_request(self):
        owner = self

        class Opener:
            def open(self, req, timeout):
                owner.assertEqual(req.get_header("Authorization"), f"Bearer {KEY}")
                owner.assertEqual(timeout, 20)
                owner.assertEqual(json.loads(req.data)["queries"][0]["market"], "US")
                return Reply(200, {"results": [{"ok": True}]})

        self.assertTrue(client.call_api(client.request_for(["screener", "US"]), KEY, Opener())["results"][0]["ok"])

    def test_errors_are_not_retried_or_dumped(self):
        for status in [401, 403, 404, 410, 429, 503]:
            calls = []

            class Opener:
                def open(self, req, timeout):
                    calls.append(req)
                    return Reply(status, {"error": {"code": "TEST_ERROR", "message": KEY}})

            with self.assertRaises(RuntimeError) as caught:
                client.call_api(client.request_for(["usage"]), KEY, Opener())
            self.assertEqual(len(calls), 1)
            self.assertIn("retry_after=60", str(caught.exception))
            self.assertNotIn(KEY, str(caught.exception))

    def test_failed_query_inside_http_200(self):
        class Opener:
            def open(self, req, timeout):
                return Reply(200, {"results": [{"ok": False, "status": "invalid_input"}]})

        with self.assertRaisesRegex(RuntimeError, "Query did not succeed"):
            client.call_api(client.request_for(["screener", "US"]), KEY, Opener())


if __name__ == "__main__":
    unittest.main()
