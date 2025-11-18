from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional

import httpx

from .exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    LoceZapError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TransportError,
    ValidationError,
)
from .response import wrap_response_payload

DEFAULT_BASE_URL = "https://apizap.loce.io/"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 2
DEFAULT_BACKOFF_FACTOR = 0.5
USER_AGENT = "loce-zap-python/0.1.0"


@dataclass(frozen=True)
class TransportConfig:
    base_url: str = DEFAULT_BASE_URL
    timeout: float = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR
    default_headers: Mapping[str, str] = field(default_factory=dict)


def _build_headers(api_key: str, overrides: Optional[Mapping[str, str]] = None) -> Dict[str, str]:
    headers: Dict[str, str] = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    if overrides:
        headers.update(overrides)
    return headers


def _should_retry(response: Optional[httpx.Response]) -> bool:
    if response is None:
        return True
    if response.status_code in (408, 425, 429):
        return True
    return response.status_code >= 500


def _raise_for_response(response: httpx.Response) -> None:
    payload: Any
    try:
        payload = response.json()
    except ValueError:
        payload = None

    message = None
    error_code = None

    if isinstance(payload, Mapping):
        message = payload.get("message") or payload.get("error_description")
        error_code = payload.get("error")

    message = message or response.text or "Unknown API error"

    exception: LoceZapError

    if response.status_code == 400:
        exception = ValidationError(message, response=payload)
    elif response.status_code == 401:
        exception = AuthenticationError(message, response=payload)
    elif response.status_code == 403:
        exception = AuthorizationError(message, response=payload)
    elif response.status_code == 404:
        exception = NotFoundError(message, response=payload)
    elif response.status_code == 429:
        exception = RateLimitError(message, response=payload)
    elif response.status_code >= 500:
        exception = ServerError(message, response=payload)
    else:
        details = payload if isinstance(payload, Mapping) else {"error": error_code, "message": message}
        exception = APIError(message, response=details)

    raise exception


class SyncHttpClient:
    def __init__(self, api_key: str, *, config: Optional[TransportConfig] = None) -> None:
        if not api_key:
            raise ValueError("api_key is required")

        self._config = config or TransportConfig()
        headers = _build_headers(api_key, self._config.default_headers)
        self._client = httpx.Client(
            base_url=self._config.base_url.rstrip("/"),
            timeout=self._config.timeout,
            headers=headers,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Mapping[str, Any]] = None,
        params: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        response: Optional[httpx.Response] = None
        for attempt in range(self._config.max_retries + 1):
            try:
                response = self._client.request(method, path, json=json, params=params)
            except httpx.TimeoutException as exc:
                if attempt == self._config.max_retries:
                    raise TransportError("Timeout ao chamar a API Loce Zap") from exc
                self._backoff(attempt)
                continue
            except httpx.TransportError as exc:
                if attempt == self._config.max_retries:
                    raise TransportError(f"Erro de transporte: {exc}") from exc
                self._backoff(attempt)
                continue

            if _should_retry(response) and attempt < self._config.max_retries:
                self._backoff(attempt)
                continue

            break

        if response is None:
            raise TransportError("Unable to reach the Loce Zap API after retries")

        if response.is_error:
            _raise_for_response(response)

        return self._deserialize(response)

    def close(self) -> None:
        self._client.close()

    def _backoff(self, attempt: int) -> None:
        delay = self._config.backoff_factor * (2**attempt)
        time.sleep(delay)

    @staticmethod
    def _deserialize(response: httpx.Response) -> Any:
        if response.status_code == 204:
            return None
        if response.headers.get("content-type", "").startswith("application/json"):
            try:
                data = response.json()
            except ValueError as exc:
                raise TransportError("Failed to decode API response as JSON") from exc
            return wrap_response_payload(data)
        return response.text

    def __enter__(self) -> "SyncHttpClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        self.close()


class AsyncHttpClient:
    def __init__(self, api_key: str, *, config: Optional[TransportConfig] = None) -> None:
        if not api_key:
            raise ValueError("api_key is required")

        self._config = config or TransportConfig()
        headers = _build_headers(api_key, self._config.default_headers)
        self._client = httpx.AsyncClient(
            base_url=self._config.base_url.rstrip("/"),
            timeout=self._config.timeout,
            headers=headers,
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Mapping[str, Any]] = None,
        params: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        response: Optional[httpx.Response] = None
        for attempt in range(self._config.max_retries + 1):
            try:
                response = await self._client.request(method, path, json=json, params=params)
            except httpx.TimeoutException as exc:
                if attempt == self._config.max_retries:
                    raise TransportError("Timeout ao chamar a API Loce Zap") from exc
                await self._backoff(attempt)
                continue
            except httpx.TransportError as exc:
                if attempt == self._config.max_retries:
                    raise TransportError(f"Erro de transporte: {exc}") from exc
                await self._backoff(attempt)
                continue

            if _should_retry(response) and attempt < self._config.max_retries:
                await self._backoff(attempt)
                continue

            break

        if response is None:
            raise TransportError("Unable to reach the Loce Zap API after retries")

        if response.is_error:
            _raise_for_response(response)

        return self._deserialize(response)

    async def close(self) -> None:
        await self._client.aclose()

    async def _backoff(self, attempt: int) -> None:
        delay = self._config.backoff_factor * (2**attempt)
        await asyncio.sleep(delay)

    @staticmethod
    def _deserialize(response: httpx.Response) -> Any:
        if response.status_code == 204:
            return None
        if response.headers.get("content-type", "").startswith("application/json"):
            try:
                data = response.json()
            except ValueError as exc:
                raise TransportError("Failed to decode API response as JSON") from exc
            return wrap_response_payload(data)
        return response.text

    async def __aenter__(self) -> "AsyncHttpClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        await self.close()
