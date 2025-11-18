from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any, Mapping, Union

from .exceptions import WebhookSignatureError

RawBody = Union[str, bytes, bytearray, Mapping[str, Any]]


def _ensure_str(body: RawBody) -> str:
    if isinstance(body, (bytes, bytearray)):
        return body.decode("utf-8")
    if isinstance(body, str):
        return body
    return json.dumps(body, separators=(",", ":"), ensure_ascii=False)


class WebhookVerifier:
    """Valida a assinatura enviada pelo Loce Zap."""

    @staticmethod
    def verify_signature(
        signature_header: str,
        *,
        body: RawBody,
        secret: str,
        tolerance: int = 5 * 60,
    ) -> bool:
        if not signature_header:
            raise WebhookSignatureError("Missing x-locezap-signature header")
        if not secret:
            raise WebhookSignatureError("Secret is required to validate webhook payloads")

        parts = {}
        for chunk in signature_header.split(","):
            if "=" in chunk:
                key, value = chunk.split("=", 1)
                parts[key.strip()] = value.strip()

        timestamp = parts.get("t")
        provided_signature = parts.get("v1")

        if not timestamp or not provided_signature:
            raise WebhookSignatureError("Assinatura mal formatada")

        now = int(time.time())
        try:
            ts = int(timestamp)
        except ValueError as exc:
            raise WebhookSignatureError("Invalid webhook timestamp") from exc

        if tolerance > 0 and abs(now - ts) > tolerance:
            raise WebhookSignatureError("Timestamp fora da janela permitida")

        raw_body = _ensure_str(body)
        data = f"{ts}.{raw_body}".encode("utf-8")
        expected = hmac.new(secret.encode("utf-8"), data, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected, provided_signature):
            raise WebhookSignatureError("Invalid webhook signature")

        return True
