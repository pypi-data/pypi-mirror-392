from __future__ import annotations

from typing import Dict, Optional, cast

from ..http import AsyncHttpClient, SyncHttpClient
from ..types import DeleteOrEditMessageResponse, SendMessageResponse


def _base_payload(
    session_id: str,
    to: str,
    *,
    external_id: Optional[str] = None,
    quote_id: Optional[str] = None,
) -> Dict[str, object]:
    if not to or not isinstance(to, str):
        raise ValueError("'to' is required when sending a message")
    body: Dict[str, object] = {"sessionId": session_id, "phone": to}
    if external_id:
        body["externalId"] = external_id
    if quote_id:
        body["quoteId"] = quote_id
    return body


def _delete_payload(session_id: str, message_id: str, to: str) -> Dict[str, object]:
    if not message_id:
        raise ValueError("'messageId' is required")
    if not to:
        raise ValueError("'to' is required")
    return {"sessionId": session_id, "messageId": message_id, "phone": to}


class MessageResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def send_message_text(
        self,
        session_id: str,
        to: str,
        text: str,
        *,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        if not text:
            raise ValueError("'text' is required in send_message_text")
        body = _base_payload(session_id, to, external_id=external_id, quote_id=quote_id)
        body["message"] = text
        data = self._http.request("POST", "/v1/message/text", json=body)
        return cast(SendMessageResponse, data)

    def send_message_image(
        self,
        session_id: str,
        to: str,
        image_url: str,
        *,
        caption: Optional[str] = None,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        if not image_url:
            raise ValueError("'imageUrl' is required in send_message_image")
        body = _base_payload(session_id, to, external_id=external_id, quote_id=quote_id)
        body["imageUrl"] = image_url
        if caption:
            body["caption"] = caption
        data = self._http.request("POST", "/v1/message/image", json=body)
        return cast(SendMessageResponse, data)

    def send_message_audio(
        self,
        session_id: str,
        to: str,
        audio_url: str,
        *,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        if not audio_url:
            raise ValueError("'audioUrl' is required in send_message_audio")
        body = _base_payload(session_id, to, external_id=external_id, quote_id=quote_id)
        body["audioUrl"] = audio_url
        data = self._http.request("POST", "/v1/message/audio", json=body)
        return cast(SendMessageResponse, data)

    def send_message_document(
        self,
        session_id: str,
        to: str,
        file_url: str,
        *,
        file_name: Optional[str] = None,
        caption: Optional[str] = None,
        mimetype: Optional[str] = None,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        if not file_url:
            raise ValueError("'fileUrl' is required in send_message_document")
        body = _base_payload(session_id, to, external_id=external_id, quote_id=quote_id)
        body["fileUrl"] = file_url
        if caption:
            body["caption"] = caption
        if file_name:
            body["fileName"] = file_name
        if mimetype:
            body["mimetype"] = mimetype
        data = self._http.request("POST", "/v1/message/document", json=body)
        return cast(SendMessageResponse, data)

    def send_message_location(
        self,
        session_id: str,
        to: str,
        *,
        latitude: float,
        longitude: float,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        body = _base_payload(session_id, to, external_id=external_id, quote_id=quote_id)
        body["latitude"] = latitude
        body["longitude"] = longitude
        data = self._http.request("POST", "/v1/message/location", json=body)
        return cast(SendMessageResponse, data)

    def send_message_video(
        self,
        session_id: str,
        to: str,
        video_url: str,
        *,
        caption: Optional[str] = None,
        mimetype: Optional[str] = None,
        gif_playback: Optional[bool] = None,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        if not video_url:
            raise ValueError("'videoUrl' is required in send_message_video")
        body = _base_payload(session_id, to, external_id=external_id, quote_id=quote_id)
        body["videoUrl"] = video_url
        if caption:
            body["caption"] = caption
        if mimetype:
            body["mimetype"] = mimetype
        if isinstance(gif_playback, bool):
            body["gifPlayback"] = gif_playback
        data = self._http.request("POST", "/v1/message/video", json=body)
        return cast(SendMessageResponse, data)

    def send_message_sticker(
        self,
        session_id: str,
        to: str,
        sticker_url: str,
        *,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        if not sticker_url:
            raise ValueError("'stickerUrl' is required in send_message_sticker")
        body = _base_payload(session_id, to, external_id=external_id, quote_id=quote_id)
        body["stickerUrl"] = sticker_url
        data = self._http.request("POST", "/v1/message/sticker", json=body)
        return cast(SendMessageResponse, data)

    def delete_message(self, session_id: str, message_id: str, to: str) -> DeleteOrEditMessageResponse:
        payload = _delete_payload(session_id, message_id, to)
        data = self._http.request("POST", "/v1/message/delete", json=payload)
        return cast(DeleteOrEditMessageResponse, data)

    def edit_message(self, session_id: str, message_id: str, to: str, text: str) -> DeleteOrEditMessageResponse:
        if not text:
            raise ValueError("'text' is required in edit_message")
        payload = _delete_payload(session_id, message_id, to)
        payload["newMessage"] = text
        data = self._http.request("POST", "/v1/message/edit", json=payload)
        return cast(DeleteOrEditMessageResponse, data)


class AsyncMessageResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def send_message_text(
        self,
        session_id: str,
        to: str,
        text: str,
        *,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        if not text:
            raise ValueError("'text' is required in send_message_text")
        body = _base_payload(session_id, to, external_id=external_id, quote_id=quote_id)
        body["message"] = text
        data = await self._http.request("POST", "/v1/message/text", json=body)
        return cast(SendMessageResponse, data)

    async def send_message_image(
        self,
        session_id: str,
        to: str,
        image_url: str,
        *,
        caption: Optional[str] = None,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        if not image_url:
            raise ValueError("'imageUrl' is required in send_message_image")
        body = _base_payload(session_id, to, external_id=external_id, quote_id=quote_id)
        body["imageUrl"] = image_url
        if caption:
            body["caption"] = caption
        data = await self._http.request("POST", "/v1/message/image", json=body)
        return cast(SendMessageResponse, data)

    async def send_message_audio(
        self,
        session_id: str,
        to: str,
        audio_url: str,
        *,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        if not audio_url:
            raise ValueError("'audioUrl' is required in send_message_audio")
        body = _base_payload(session_id, to, external_id=external_id, quote_id=quote_id)
        body["audioUrl"] = audio_url
        data = await self._http.request("POST", "/v1/message/audio", json=body)
        return cast(SendMessageResponse, data)

    async def send_message_document(
        self,
        session_id: str,
        to: str,
        file_url: str,
        *,
        file_name: Optional[str] = None,
        caption: Optional[str] = None,
        mimetype: Optional[str] = None,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        if not file_url:
            raise ValueError("'fileUrl' is required in send_message_document")
        body = _base_payload(session_id, to, external_id=external_id, quote_id=quote_id)
        body["fileUrl"] = file_url
        if caption:
            body["caption"] = caption
        if file_name:
            body["fileName"] = file_name
        if mimetype:
            body["mimetype"] = mimetype
        data = await self._http.request("POST", "/v1/message/document", json=body)
        return cast(SendMessageResponse, data)

    async def send_message_location(
        self,
        session_id: str,
        to: str,
        *,
        latitude: float,
        longitude: float,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        body = _base_payload(session_id, to, external_id=external_id, quote_id=quote_id)
        body["latitude"] = latitude
        body["longitude"] = longitude
        data = await self._http.request("POST", "/v1/message/location", json=body)
        return cast(SendMessageResponse, data)

    async def send_message_video(
        self,
        session_id: str,
        to: str,
        video_url: str,
        *,
        caption: Optional[str] = None,
        mimetype: Optional[str] = None,
        gif_playback: Optional[bool] = None,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        if not video_url:
            raise ValueError("'videoUrl' is required in send_message_video")
        body = _base_payload(session_id, to, external_id=external_id, quote_id=quote_id)
        body["videoUrl"] = video_url
        if caption:
            body["caption"] = caption
        if mimetype:
            body["mimetype"] = mimetype
        if isinstance(gif_playback, bool):
            body["gifPlayback"] = gif_playback
        data = await self._http.request("POST", "/v1/message/video", json=body)
        return cast(SendMessageResponse, data)

    async def send_message_sticker(
        self,
        session_id: str,
        to: str,
        sticker_url: str,
        *,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        if not sticker_url:
            raise ValueError("'stickerUrl' is required in send_message_sticker")
        body = _base_payload(session_id, to, external_id=external_id, quote_id=quote_id)
        body["stickerUrl"] = sticker_url
        data = await self._http.request("POST", "/v1/message/sticker", json=body)
        return cast(SendMessageResponse, data)

    async def delete_message(self, session_id: str, message_id: str, to: str) -> DeleteOrEditMessageResponse:
        payload = _delete_payload(session_id, message_id, to)
        data = await self._http.request("POST", "/v1/message/delete", json=payload)
        return cast(DeleteOrEditMessageResponse, data)

    async def edit_message(self, session_id: str, message_id: str, to: str, text: str) -> DeleteOrEditMessageResponse:
        if not text:
            raise ValueError("'text' is required in edit_message")
        payload = _delete_payload(session_id, message_id, to)
        payload["newMessage"] = text
        data = await self._http.request("POST", "/v1/message/edit", json=payload)
        return cast(DeleteOrEditMessageResponse, data)
