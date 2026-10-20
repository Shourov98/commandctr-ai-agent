import base64

import pytest

from app.services import gemini_service
from app.services.gemini_service import GeminiService


@pytest.mark.anyio
async def test_edit_image_uses_configured_gemini_image_model(monkeypatch) -> None:
    recorded: dict[str, object] = {}

    class FakeResponse:
        status_code = 200
        text = ""

        @staticmethod
        def json():
            return {
                "candidates": [
                    {"content": {"parts": [{"inlineData": {"data": base64.b64encode(b"image-bytes").decode("ascii")}}]}}
                ]
            }

    class FakeClient:
        def __init__(self, **kwargs):
            recorded["timeout"] = kwargs["timeout"]

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def post(self, url, *, params, json):
            recorded.update({"url": url, "params": params, "payload": json})
            return FakeResponse()

    monkeypatch.setattr(gemini_service.httpx, "AsyncClient", FakeClient)
    service = GeminiService(
        api_key="test-key",
        model="gemini-2.5-flash",
        image_model="gemini-2.5-flash-image",
        api_base_url="https://example.test/v1beta",
        enabled=True,
    )

    result = await service.edit_image(prompt="Create a product cutout", image_bytes=b"source", mime_type="image/png")

    assert result == b"image-bytes"
    assert recorded["url"] == "https://example.test/v1beta/models/gemini-2.5-flash-image:generateContent"
    assert recorded["params"] == {"key": "test-key"}
    assert recorded["payload"]["generationConfig"]["responseModalities"] == ["IMAGE"]
