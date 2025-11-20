"""HTTP client for the Bangkok Open Data CKAN Action API."""

from __future__ import annotations

import os
import time
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
from typing import Any, Optional

import requests
from requests import Response, Session

from .models import (
    DatasetResponse,
    HelpResponse,
    ResourceResponse,
    SearchResponse,
    StringListResponse,
)

DEFAULT_BASE_URL = "https://data.bangkok.go.th/api/3/action"
DEFAULT_USER_AGENT = os.getenv(
    "BMA_OPENDATA_USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36",
)


class CKANApiError(Exception):
    """Error raised when the CKAN API reports a failure."""

    def __init__(self, message: str, error_type: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.error_type = error_type

    def __str__(self) -> str:  # pragma: no cover - trivial string formatting
        base = self.message
        if self.error_type:
            return f"{self.error_type}: {base}"
        return base


@dataclass
class _CacheEntry:
    value: dict[str, Any]
    expires_at: Optional[float]


class BangkokOpenDataClient:
    """
    High-level client for interacting with the Bangkok CKAN Action API.

    Example:
        >>> from bma_opendata import BangkokOpenDataClient
        >>> client = BangkokOpenDataClient()
        >>> dataset_ids = client.list_datasets().result
        >>> if dataset_ids:
        ...     dataset = client.get_dataset(name=dataset_ids[0]).result
        ...     print(dataset.title)

    """

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        session: Optional[Session] = None,
        headers: Optional[Mapping[str, str]] = None,
        api_key: Optional[str] = None,
        timeout: Optional[float] = 10.0,
        cache_ttl: Optional[int] = 300,
    ) -> None:
        """
        Create a new API client.

        Args:
            base_url: Base CKAN Action API URL.
            session: Optional requests session. When omitted a new session is created.
            headers: Extra headers to send with every request.
            api_key: Optional CKAN API key, added via ``X-CKAN-API-Key`` header.
            timeout: Request timeout in seconds for HTTP calls.
            cache_ttl: Optional cache TTL (seconds). ``None`` disables caching entirely.

        """
        self.base_url = base_url.rstrip("/")
        self._session: Session = session or requests.Session()
        self._owns_session = session is None
        self.timeout = timeout

        resolved_api_key = api_key or os.getenv("BMA_OPENDATA_API_KEY")

        self._headers: MutableMapping[str, str] = {"User-Agent": DEFAULT_USER_AGENT}
        if headers:
            self._headers.update(headers)
        if "User-Agent" not in self._headers:
            self._headers["User-Agent"] = DEFAULT_USER_AGENT
        if resolved_api_key:
            self._headers.setdefault("X-CKAN-API-Key", resolved_api_key)

        self._cache_ttl = cache_ttl if cache_ttl and cache_ttl > 0 else None
        self._cache: dict[tuple[str, tuple[tuple[str, str], ...]], _CacheEntry] = {}

    def __enter__(self) -> BangkokOpenDataClient:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying session if this client owns it."""
        if self._owns_session:
            self._session.close()

    def clear_cache(self) -> None:
        """Clear any cached responses."""
        self._cache.clear()

    def list_datasets(self) -> StringListResponse:
        """Return a list of dataset identifiers (slugs)."""
        payload = self._request_json("package_list", params={})
        return StringListResponse.model_validate(payload)

    def get_dataset(
        self, *, id: Optional[str] = None, name: Optional[str] = None
    ) -> DatasetResponse:
        """
        Retrieve a dataset by UUID or name.

        Args:
            id: Dataset UUID.
            name: Dataset name/slug.

        Raises:
            ValueError: When both ``id`` and ``name`` are omitted.

        """
        if not id and not name:
            raise ValueError("Either 'id' or 'name' must be provided.")

        params = {"id": id, "name": name}
        payload = self._request_json("package_show", params=params)
        return DatasetResponse.model_validate(payload)

    def get_resource(self, *, id: str) -> ResourceResponse:
        """Retrieve metadata for a single resource."""
        if not id:
            raise ValueError("'id' is required to fetch a resource.")

        payload = self._request_json("resource_show", params={"id": id})
        return ResourceResponse.model_validate(payload)

    def search_datasets(
        self,
        *,
        q: Optional[str] = None,
        fq: Optional[str] = None,
        rows: Optional[int] = None,
        start: Optional[int] = None,
    ) -> SearchResponse:
        """Search datasets using CKAN's package_search endpoint."""
        params = {"q": q, "fq": fq, "rows": rows, "start": start}
        payload = self._request_json("package_search", params=params)
        return SearchResponse.model_validate(payload)

    def help(self, *, name: Optional[str] = None) -> HelpResponse:
        """Return help text for a CKAN action or list available actions."""
        payload = self._request_json("help_show", params={"name": name})
        return HelpResponse.model_validate(payload)

    def _request_json(self, endpoint: str, params: Mapping[str, Any]) -> dict[str, Any]:
        clean_params = {k: v for k, v in params.items() if v is not None}
        cache_key = self._build_cache_key(endpoint, clean_params)
        cached = self._read_cache(cache_key)
        if cached is not None:
            return cached

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self._session.get(
                url, params=clean_params, headers=self._headers, timeout=self.timeout
            )
            response.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover - network errors
            raise CKANApiError(str(exc), error_type="NetworkError") from exc

        payload = self._parse_response(response)

        if payload.get("success"):
            self._write_cache(cache_key, payload)

        return payload

    def _parse_response(self, response: Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise CKANApiError(
                "Received an invalid JSON payload from the CKAN API.",
                error_type="InvalidResponse",
            ) from exc

        if not isinstance(payload, dict):
            raise CKANApiError(
                "Unexpected response structure returned by the CKAN API.",
                error_type="InvalidResponse",
            )

        success = payload.get("success")
        if success is False:
            error_data = payload.get("error") or {}
            message = error_data.get("message", "CKAN API reported an unknown error.")
            error_type = error_data.get("__type")
            raise CKANApiError(message, error_type=error_type)

        return payload

    def _build_cache_key(
        self, endpoint: str, params: Mapping[str, Any]
    ) -> tuple[str, tuple[tuple[str, str], ...]]:
        sorted_params = tuple(
            sorted((key, str(value)) for key, value in params.items())
        )
        return endpoint, sorted_params

    def _read_cache(
        self, key: tuple[str, tuple[tuple[str, str], ...]]
    ) -> Optional[dict[str, Any]]:
        if self._cache_ttl is None:
            return None
        entry = self._cache.get(key)
        if not entry:
            return None
        if entry.expires_at is not None and entry.expires_at < time.time():
            self._cache.pop(key, None)
            return None
        return entry.value

    def _write_cache(
        self, key: tuple[str, tuple[tuple[str, str], ...]], value: dict[str, Any]
    ) -> None:
        if self._cache_ttl is None:
            return
        expires_at = time.time() + self._cache_ttl if self._cache_ttl else None
        self._cache[key] = _CacheEntry(value=value, expires_at=expires_at)


__all__ = ["BangkokOpenDataClient", "CKANApiError"]
