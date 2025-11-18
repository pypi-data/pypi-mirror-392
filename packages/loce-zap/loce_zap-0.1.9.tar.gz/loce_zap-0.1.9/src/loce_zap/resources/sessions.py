from __future__ import annotations

from typing import Mapping, cast

from ..http import AsyncHttpClient, SyncHttpClient
from ..types import SessionConnectResponse, SessionDisconnectResponse, SessionListResponse


class SessionResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def connect(
        self,
        session_name: str,
        webhook_url: str,
        webhook_messages: bool = True
    ) -> SessionConnectResponse:
        body = _build_connect_payload(
            session_name=session_name,
            webhook_url=webhook_url,
            webhook_messages=webhook_messages
        )
        data = self._http.request("POST", "/v1/session/connect", json=body)
        return cast(SessionConnectResponse, data)

    def disconnect(self, session_id: str) -> SessionDisconnectResponse:
        data = self._http.request("DELETE", f"/v1/session/disconnect/{session_id}")
        return cast(SessionDisconnectResponse, data)

    def list_sessions(self) -> SessionListResponse:
        data = self._http.request("GET", "/v1/session/all")
        return cast(SessionListResponse, data)


class AsyncSessionResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def connect(
        self,
        session_name: str,
        webhook_url: str,
        webhook_messages: bool = True
    ) -> SessionConnectResponse:
        body = _build_connect_payload(
            session_name=session_name,
            webhook_url=webhook_url,
            webhook_messages=webhook_messages
        )
        data = await self._http.request("POST", "/v1/session/connect", json=body)
        return cast(SessionConnectResponse, data)

    async def disconnect(self, session_id: str) -> SessionDisconnectResponse:
        data = await self._http.request("DELETE", f"/v1/session/disconnect/{session_id}")
        return cast(SessionDisconnectResponse, data)

    async def list_sessions(self) -> SessionListResponse:
        data = await self._http.request("GET", "/v1/session/all")
        return cast(SessionListResponse, data)


def _build_connect_payload(
    *,
    session_name: str,
    webhook_url: str,
    webhook_messages: bool
) -> Mapping[str, object]:
    if not webhook_url or not isinstance(webhook_url, str):
        raise ValueError("webhookUrl is required when connecting a session")

    resolved_name = session_name.strip() if isinstance(session_name, str) else ""
    if not resolved_name:
        resolved_name = "Loce Zap Session"

    return {
        "sessionName": resolved_name,
        "webhookUrl": webhook_url,
        "webhookMessages": webhook_messages
    }
