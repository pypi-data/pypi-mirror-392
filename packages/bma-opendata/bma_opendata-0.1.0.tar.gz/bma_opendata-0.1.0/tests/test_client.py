from __future__ import annotations

import unittest
from collections.abc import Mapping
from typing import Any

import requests

from bma_opendata.client import BangkokOpenDataClient, CKANApiError


class DummyResponse:
    def __init__(self, payload: dict[str, Any], status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code

    def json(self) -> dict[str, Any]:
        return self.payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class DummySession:
    def __init__(self, responses: list[DummyResponse]) -> None:
        self.responses = responses
        self.calls: list[Mapping[str, Any]] = []

    def get(self, url: str, *, params: Mapping[str, Any], headers, timeout):
        self.calls.append({"url": url, "params": dict(params)})
        if not self.responses:
            raise AssertionError("No more responses configured.")
        return self.responses.pop(0)

    def close(self) -> None:  # pragma: no cover - no resources to release
        pass


class BangkokOpenDataClientTests(unittest.TestCase):
    def test_list_datasets_returns_string_response(self) -> None:
        payload = {"help": "url", "success": True, "result": ["a", "b"]}
        session = DummySession([DummyResponse(payload)])
        client = BangkokOpenDataClient(session=session, cache_ttl=None)

        response = client.list_datasets()

        self.assertEqual(response.result, ["a", "b"])
        self.assertEqual(len(session.calls), 1)

    def test_cache_reuses_payload(self) -> None:
        payload = {"help": "url", "success": True, "result": ["only"]}
        session = DummySession([DummyResponse(payload)])
        client = BangkokOpenDataClient(session=session, cache_ttl=60)

        first = client.list_datasets()
        second = client.list_datasets()

        self.assertEqual(first.result, ["only"])
        self.assertEqual(second.result, ["only"])
        self.assertEqual(len(session.calls), 1)

    def test_error_response_raises_exception(self) -> None:
        payload = {
            "help": "url",
            "success": False,
            "error": {"message": "not found", "__type": "NotFound"},
        }
        session = DummySession([DummyResponse(payload)])
        client = BangkokOpenDataClient(session=session, cache_ttl=None)

        with self.assertRaises(CKANApiError) as ctx:
            client.list_datasets()

        self.assertIn("not found", str(ctx.exception))

    def test_missing_dataset_identifier_raises_value_error(self) -> None:
        payload = {"help": "url", "success": True, "result": {}}
        session = DummySession([DummyResponse(payload)])
        client = BangkokOpenDataClient(session=session, cache_ttl=None)

        with self.assertRaises(ValueError):
            client.get_dataset()


if __name__ == "__main__":
    unittest.main()
