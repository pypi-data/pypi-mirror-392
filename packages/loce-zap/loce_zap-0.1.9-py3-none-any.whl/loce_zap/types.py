from __future__ import annotations

from typing import List, Optional

from .response import APIResponse


class Session(APIResponse):
    _id: Optional[str]
    id: Optional[str]
    user: Optional[str]
    name: Optional[str]
    wppId: Optional[str]
    wpp_id: Optional[str]
    phone: Optional[str]
    webhookUrl: Optional[str]
    webhook_url: Optional[str]
    webhookMessages: Optional[bool]
    webhook_messages: Optional[bool]
    syncFullHistory: Optional[bool]
    sync_full_history: Optional[bool]
    daysHistory: Optional[int]
    days_history: Optional[int]
    autoRejectCalls: Optional[bool]
    auto_reject_calls: Optional[bool]
    queueName: Optional[str]
    queue_name: Optional[str]
    createdAt: Optional[str]
    created_at: Optional[str]
    updatedAt: Optional[str]
    updated_at: Optional[str]


class SessionConnectResponse(APIResponse):
    sessionId: Optional[str]
    session_id: Optional[str]
    message: Optional[str]
    status: Optional[str]
    qrCode: Optional[str]
    qr_code: Optional[str]
    expiresAt: Optional[str]
    expires_at: Optional[str]


class SessionDisconnectResponse(APIResponse):
    sessionId: Optional[str]
    session_id: Optional[str]
    success: Optional[bool]
    message: Optional[str]


class SessionUpdateResponse(APIResponse):
    message: Optional[str]
    session: Optional[Session]


class SessionListResponse(APIResponse):
    sessions: List[Session]


class SendMessageResponse(APIResponse):
    message: Optional[str]
    success: Optional[bool]
    messageId: Optional[str]
    message_id: Optional[str]


class DeleteOrEditMessageResponse(APIResponse):
    success: Optional[bool]
    message: Optional[str]
    messageId: Optional[str]
    message_id: Optional[str]


class WebhookEnvelope(APIResponse):
    api_key: Optional[str]
    sessionId: Optional[str]
    session_id: Optional[str]
    type: Optional[str]
    payload: Optional[dict]
