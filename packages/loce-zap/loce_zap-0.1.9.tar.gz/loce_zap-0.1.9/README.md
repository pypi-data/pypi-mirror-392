# Loce Zap Python SDK

Official Python SDK for the Loce Zap multi-session WhatsApp API. It mirrors the HTTP endpoints from `/api/session` and `/api/message`.

> **Recipients:** Numbers must be in E.164 format **without** the `+` (DDI + number, 6–15 digits). Use the WhatsApp group JID (`123456@g.us`) to address groups.

## Installation

```bash
pip install loce-zap
```

For local development inside this repository:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

## Quick start

```python
import LoceZap

zap = LoceZap("your_api_key")

# 1) Connect a session and print the QR code info
qr = zap.connect("Support Session", "https://example.com/webhook", webhook_messages=True)
print(qr.status, qr.qrCode)

# 2) List current sessions
print("Current sessions:", zap.list_sessions())

# 3) Send text, image, document, location
zap.send_message_text("support-session", "5511999999999", "Hello from Python 👋")
zap.send_message_image(
    "support-session",
    "5511999999999",
    "https://files.loce.io/promo.png",
    caption="Check this out!",
)
zap.send_message_document(
    "support-session",
    "5511999999999",
    "https://files.loce.io/contract.pdf",
    file_name="Contract.pdf",
)
zap.send_message_location(
    "support-session",
    "5511999999999",
    latitude=-16.7033,
    longitude=-49.263,
)

# 4) Demonstrate edit/delete
resp = zap.send_message_text("support-session", "5511999999999", "Temporary message")
msg_id = resp.message_id
if msg_id:
    zap.edit_message("support-session", msg_id, "5511999999999", "Updated message")
    zap.delete_message("support-session", msg_id, "5511999999999")
```

## Client configuration

```python
LoceZap(
    api_key="lz_xxx"
)
```

## Session management

| Method | Description |
| --- | --- |
| `connect(session_name, webhook_url, webhook_messages=True, *, sync_full_history=False, days_history=7)` | Creates/updates a session and returns QR-code/status info. |
| `disconnect(session_id)` | Closes the WhatsApp session. |
| `list_sessions()` | Returns `{ sessions: [...] }` for the authenticated user. |

## Messaging helpers

| Helper | Description |
| --- | --- |
| `send_message_text(session_id, to, text, *, external_id=None, quote_id=None)` | Plain text message. |
| `send_message_image(session_id, to, image_url, *, caption=None, external_id=None, quote_id=None)` | Sends an image by URL. |
| `send_message_audio(session_id, to, audio_url, *, external_id=None, quote_id=None)` | Audio/PTT. |
| `send_message_document(session_id, to, file_url, *, file_name=None, caption=None, mimetype=None, external_id=None, quote_id=None)` | Documents/PDFs. |
| `send_message_location(session_id, to, *, latitude, longitude, external_id=None, quote_id=None)` | Location payload. |
| `send_message_video(session_id, to, video_url, *, caption=None, mimetype=None, gif_playback=None, external_id=None, quote_id=None)` | Video/GIF. |
| `send_message_sticker(session_id, to, sticker_url, *, external_id=None, quote_id=None)` | Sticker message. |
| `delete_message(session_id, message_id, to)` | Requests deletion of a previously sent message. |
| `edit_message(session_id, message_id, to, text)` | Updates the body of a previously sent message. |

All helpers return an `APIResponse` object (dict-like with attribute access). Fields can be read with either their original camelCase names (`resp.messageId`) or snake_case aliases (`resp.message_id`). Required fields are validated before making the HTTP call; missing `text`, `image_url`, etc. raise `ValueError` locally.

## HTTP endpoint reference

Below are the raw REST calls that the SDK issues internally. Replace `lz_xxxxxxxxxx` with your API key and `session_id`/`phone`/payload values as needed.

### Sessions

```bash
# Create or update a session (validates & returns QR status)
curl -X POST https://apizap.loce.io/v1/session/connect \
  -H 'Authorization: Bearer lz_xxxxxxxxxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "sessionName": "session_name",
    "webhookUrl": "https://example.com/webhook",
    "webhookMessages": true
  }'

# Disconnect an active session
curl -X DELETE https://apizap.loce.io/v1/session/disconnect/session_id \
  -H 'Authorization: Bearer lz_xxxxxxxxxx'

# List every session that belongs to your account
curl -X GET https://apizap.loce.io/v1/session/all \
  -H 'Authorization: Bearer lz_xxxxxxxxxx'
```

### Messages

```bash
# Send a plain text message
curl -X POST https://apizap.loce.io/v1/message/text \
  -H 'Authorization: Bearer lz_xxxxxxxxxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "sessionId": "session_id",
    "phone": "5511999999999",
    "message": "Hello from curl",
    "externalId": "optional-id",
    "quoteId": "optional-message-id"
  }'

# Send an image
curl -X POST https://apizap.loce.io/v1/message/image \
  -H 'Authorization: Bearer lz_xxxxxxxxxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "sessionId": "session_id",
    "phone": "5511999999999",
    "imageUrl": "https://files.loce.io/promo.png",
    "caption": "Check this out!",
    "externalId": "optional-id",
    "quoteId": "optional-message-id"
  }'

# Send an audio/PTT
curl -X POST https://apizap.loce.io/v1/message/audio \
  -H 'Authorization: Bearer lz_xxxxxxxxxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "sessionId": "session_id",
    "phone": "5511999999999",
    "audioUrl": "https://files.loce.io/audio.ogg",
    "externalId": "optional-id",
    "quoteId": "optional-message-id"
  }'

# Send a document/PDF
curl -X POST https://apizap.loce.io/v1/message/document \
  -H 'Authorization: Bearer lz_xxxxxxxxxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "sessionId": "session_id",
    "phone": "5511999999999",
    "fileUrl": "https://files.loce.io/contract.pdf",
    "fileName": "Contract.pdf",
    "caption": "Please review",
    "mimetype": "application/pdf",
    "externalId": "optional-id",
    "quoteId": "optional-message-id"
  }'

# Send a video/GIF
curl -X POST https://apizap.loce.io/v1/message/video \
  -H 'Authorization: Bearer lz_xxxxxxxxxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "sessionId": "session_id",
    "phone": "5511999999999",
    "videoUrl": "https://files.loce.io/product.mp4",
    "caption": "New catalog",
    "mimetype": "video/mp4",
    "gifPlayback": false,
    "externalId": "optional-id",
    "quoteId": "optional-message-id"
  }'

# Send a sticker
curl -X POST https://apizap.loce.io/v1/message/sticker \
  -H 'Authorization: Bearer lz_xxxxxxxxxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "sessionId": "session_id",
    "phone": "5511999999999",
    "stickerUrl": "https://files.loce.io/sticker.webp",
    "externalId": "optional-id",
    "quoteId": "optional-message-id"
  }'

# Send a location
curl -X POST https://apizap.loce.io/v1/message/location \
  -H 'Authorization: Bearer lz_xxxxxxxxxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "sessionId": "session_id",
    "phone": "5511999999999",
    "latitude": -16.7033,
    "longitude": -49.263,
    "externalId": "optional-id",
    "quoteId": "optional-message-id"
  }'
```

> Fields marked as optional can be safely omitted. Their presence/absence does not change the endpoint URL or HTTP verb.

Message updates/deletion mirror the SDK helpers:

```bash
curl -X POST https://apizap.loce.io/v1/message/edit \
  -H 'Authorization: Bearer lz_xxxxxxxxxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "sessionId": "session_id",
    "messageId": "message_id",
    "newMessage": "new body",
    "phone": "5511999999999"
  }'

curl -X POST https://apizap.loce.io/v1/message/delete \
  -H 'Authorization: Bearer lz_xxxxxxxxxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "sessionId": "session_id",
    "messageId": "message_id",
    "phone": "5511999999999"
  }'
```

> **Note:** The REST API currently does not expose a "list all messages" endpoint, so the SDK cannot provide that helper.

## Webhook verification

Loce Zap signs every webhook with HMAC-SHA256. Use the built-in verifier to check the `x-locezap-signature` header:

```python
from LoceZap import WebhookVerifier, WebhookSignatureError

signature = request.headers.get("x-locezap-signature")
try:
    WebhookVerifier.verify_signature(signature_header=signature, body=request.data, secret="your_api_key")
except WebhookSignatureError:
    abort(400, "Invalid signature")
```

## Error handling

| Exception | Meaning |
| --- | --- |
| `AuthenticationError` | Invalid/missing API key. |
| `AuthorizationError` | User lacks permission for that resource. |
| `RateLimitError` | Daily quota or HTTP rate limit exceeded. |
| `ValidationError` | Payload rejected (400). |
| `NotFoundError` | Session/message not found. |
| `ServerError` | 5xx returned by Loce Zap. |
| `TransportError` | Network, timeout, or JSON decoding issue after retries. |
| `WebhookSignatureError` | Incoming webhook signature mismatch. |

```python
from LoceZap import LoceZap, ValidationError

try:
    zap.send_message_text("demo", "invalid", "ping")
except ValidationError as exc:
    print("Payload rejected:", exc)
```

## Logging & troubleshooting

1. **Network failures**: repeated `TransportError` usually means base URL, proxies, or firewalls are blocking requests. Increase `timeout`/`max_retries` if needed.
2. **Rate limiting**: catch `RateLimitError`, implement exponential backoff or queueing.
3. **Inspect traffic**: set `HTTPX_LOG_LEVEL=debug` to log requests/responses for debugging.

## Build & publish

```bash
python3 -m pip install --upgrade build twine wheel
rm -rf dist
python3 -m build
python3 -m twine upload dist/*      # add --repository testpypi for dry run
```

Remember to bump `project.version` inside `pyproject.toml` before uploading to PyPI.

## License

MIT.
