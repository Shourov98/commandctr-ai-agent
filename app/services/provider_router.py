from __future__ import annotations

from typing import Any, Literal

from app.services.gemini_service import GeminiService, GeminiServiceError
from app.services.openai_service import OpenAIService, OpenAIServiceError

ProviderName = Literal["openai", "gemini"]


class TextProviderRouter:
    """Selects one enabled text provider and falls back safely on provider failure."""

    def __init__(
        self,
        *,
        openai_service: OpenAIService,
        gemini_service: GeminiService,
        openai_enabled: bool,
        gemini_enabled: bool,
        preference: str,
    ) -> None:
        self.openai_service = openai_service
        self.gemini_service = gemini_service
        self.openai_enabled = openai_enabled and openai_service.enabled
        self.gemini_enabled = gemini_enabled and gemini_service.enabled
        self.preference = preference
        self.enabled = self.openai_enabled or self.gemini_enabled
        self.model = self._model_for_primary_provider()
        self.last_provider: ProviderName | None = None

    def _providers(self) -> list[ProviderName]:
        enabled = [provider for provider, active in (("openai", self.openai_enabled), ("gemini", self.gemini_enabled)) if active]
        if self.preference in enabled:
            return [self.preference, *[provider for provider in enabled if provider != self.preference]]  # type: ignore[list-item]
        # Auto uses Gemini as the text default, preserving the previous app behavior.
        return [provider for provider in ("gemini", "openai") if provider in enabled]  # type: ignore[list-item]

    def _model_for_primary_provider(self) -> str:
        providers = self._providers()
        if not providers:
            return "fallback"
        return self.openai_service.model if providers[0] == "openai" else self.gemini_service.model

    async def generate_structured_output(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        schema: dict[str, Any],
        schema_name: str = "structured_output",
        use_google_search: bool = False,
        media_parts: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        errors: list[str] = []
        for provider in self._providers():
            try:
                if provider == "gemini":
                    result = await self.gemini_service.generate_structured_output(
                        system_prompt=system_prompt,
                        user_payload=user_payload,
                        use_google_search=use_google_search,
                        schema=schema,
                        media_parts=media_parts,
                    )
                elif use_google_search:
                    result = await self.openai_service.generate_structured_output_with_web_search(
                        system_prompt=system_prompt,
                        user_payload=user_payload,
                        schema_name=schema_name,
                        schema=schema,
                    )
                else:
                    result = await self.openai_service.generate_structured_output(
                        system_prompt=system_prompt,
                        user_payload=user_payload,
                        schema_name=schema_name,
                        schema=schema,
                    )
                self.last_provider = provider
                self.model = self.openai_service.model if provider == "openai" else self.gemini_service.model
                return result
            except (GeminiServiceError, OpenAIServiceError) as exc:
                errors.append(f"{provider}: {exc}")
        raise GeminiServiceError("No enabled text provider succeeded. " + " | ".join(errors))

    def build_inline_media_part(self, *, data: bytes, mime_type: str) -> dict[str, Any]:
        return GeminiService.build_inline_media_part(data=data, mime_type=mime_type)


class ImageProviderRouter:
    """Selects one enabled image provider and falls back safely on provider failure."""

    def __init__(
        self,
        *,
        openai_service: OpenAIService,
        gemini_service: GeminiService,
        openai_enabled: bool,
        gemini_enabled: bool,
        preference: str,
    ) -> None:
        self.openai_service = openai_service
        self.gemini_service = gemini_service
        self.openai_enabled = openai_enabled and openai_service.enabled
        self.gemini_enabled = gemini_enabled and gemini_service.enabled
        self.preference = preference
        self.enabled = self.openai_enabled or self.gemini_enabled
        self.last_provider: ProviderName | None = None

    def _providers(self) -> list[ProviderName]:
        enabled = [provider for provider, active in (("openai", self.openai_enabled), ("gemini", self.gemini_enabled)) if active]
        if self.preference in enabled:
            return [self.preference, *[provider for provider in enabled if provider != self.preference]]  # type: ignore[list-item]
        # Auto uses Gemini as the image default, then OpenAI on failure.
        return [provider for provider in ("gemini", "openai") if provider in enabled]  # type: ignore[list-item]

    async def edit_image(self, *, prompt: str, image_bytes: bytes, filename: str, mime_type: str) -> bytes:
        errors: list[str] = []
        for provider in self._providers():
            try:
                if provider == "gemini":
                    result = await self.gemini_service.edit_image(
                        prompt=prompt,
                        image_bytes=image_bytes,
                        mime_type=mime_type,
                    )
                else:
                    result = await self.openai_service.edit_image(
                        prompt=prompt,
                        image_bytes=image_bytes,
                        filename=filename,
                        mime_type=mime_type,
                        size="1024x1024",
                        background="transparent",
                    )
                self.last_provider = provider
                return result
            except (GeminiServiceError, OpenAIServiceError) as exc:
                errors.append(f"{provider}: {exc}")
        raise GeminiServiceError("No enabled image provider succeeded. " + " | ".join(errors))
