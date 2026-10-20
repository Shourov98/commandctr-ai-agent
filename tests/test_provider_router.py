import pytest

from app.services.gemini_service import GeminiServiceError
from app.services.provider_router import ImageProviderRouter, TextProviderRouter


class FakeOpenAI:
    enabled = True
    model = "openai-text"
    image_model = "openai-image"

    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[str] = []

    async def generate_structured_output(self, **_kwargs):
        self.calls.append("text")
        if self.fail:
            raise Exception("OpenAI unavailable")
        return {"provider": "openai"}

    async def generate_structured_output_with_web_search(self, **_kwargs):
        return await self.generate_structured_output(**_kwargs)

    async def edit_image(self, **_kwargs):
        self.calls.append("image")
        if self.fail:
            raise Exception("OpenAI unavailable")
        return b"openai-image"


class FakeGemini:
    enabled = True
    model = "gemini-text"
    image_model = "gemini-image"

    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[str] = []

    async def generate_structured_output(self, **_kwargs):
        self.calls.append("text")
        if self.fail:
            raise GeminiServiceError("Gemini unavailable")
        return {"provider": "gemini"}

    async def edit_image(self, **_kwargs):
        self.calls.append("image")
        if self.fail:
            raise GeminiServiceError("Gemini unavailable")
        return b"gemini-image"


@pytest.mark.anyio
async def test_text_router_honors_openai_preference_then_falls_back() -> None:
    openai = FakeOpenAI()
    gemini = FakeGemini()
    router = TextProviderRouter(
        openai_service=openai, gemini_service=gemini, openai_enabled=True, gemini_enabled=True, preference="openai"
    )

    assert await router.generate_structured_output(system_prompt="x", user_payload={}, schema={}) == {"provider": "openai"}
    assert openai.calls == ["text"]
    assert gemini.calls == []


@pytest.mark.anyio
async def test_image_router_falls_back_when_preferred_provider_fails() -> None:
    openai = FakeOpenAI()
    gemini = FakeGemini(fail=True)
    router = ImageProviderRouter(
        openai_service=openai, gemini_service=gemini, openai_enabled=True, gemini_enabled=True, preference="gemini"
    )

    assert await router.edit_image(prompt="x", image_bytes=b"source", filename="source.png", mime_type="image/png") == b"openai-image"
    assert gemini.calls == ["image"]
    assert openai.calls == ["image"]
