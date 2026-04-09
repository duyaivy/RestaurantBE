"""Embedding service backed by an external OpenAI-compatible API."""

from __future__ import annotations

import logging
import os
from typing import List

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


logger = logging.getLogger(__name__)


class ExternalAPIEmbeddingBackend:
    def __init__(self, model: str, api_key: str, base_url: str | None = None) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImproperlyConfigured("Please install the 'openai' package.") from exc

        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        logger.info(
            "Embedding backend initialized with model='%s' and base_url='%s'.",
            model,
            base_url,
        )

    def embed_text(self, text: str) -> List[float]:
        text = (text or "").strip()
        if not text:
            logger.warning("Received empty text for embedding.")
            return []
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=[text],
                extra_body={"input_type": "query", "truncate": "NONE"},
            )
        except Exception as exc:
            raise RuntimeError(self._build_embedding_error_message(exc)) from exc
        return response.data[0].embedding

    def embed_texts(self, texts: List[str], batch_size: int = 50) -> List[List[float]]:
        clean = [(t or "").strip() for t in texts if (t or "").strip()]
        if not clean:
            return []
        all_embeddings: List[List[float]] = []
        for start in range(0, len(clean), batch_size):
            batch = clean[start : start + batch_size]
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    extra_body={"input_type": "passage", "truncate": "NONE"},
                )
            except Exception as exc:
                raise RuntimeError(self._build_embedding_error_message(exc)) from exc
            all_embeddings.extend(item.embedding for item in response.data)
        return all_embeddings

    def _build_embedding_error_message(self, exc: Exception) -> str:
        message = str(exc)
        if "404" in message:
            return (
                "Embedding endpoint not found (404). "
                "Please verify CHATBOT_EMBEDDING_BASE_URL and CHATBOT_EMBEDDING_MODEL. "
                "For NVIDIA, use base_url='https://integrate.api.nvidia.com/v1' and a supported NVIDIA embedding model."
            )
        return f"Embedding request failed: {message}"


class EmbeddingService:

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        model = (
            model
            or getattr(settings, "CHATBOT_EMBEDDING_MODEL", None)
            or "nvidia/llama-3.2-nv-embedqa-1b-v2"
        )

        base_url = (
            base_url
            or getattr(settings, "CHATBOT_EMBEDDING_BASE_URL", None)
            or "https://integrate.api.nvidia.com/v1"
        )

        api_key = (
            api_key
            or getattr(settings, "CHATBOT_EMBEDDING_API_KEY", None)
            or os.getenv("CHATBOT_EMBEDDING_API_KEY")
            or getattr(settings, "NVIDIA_API_KEY", None)
            or os.getenv("NVIDIA_API_KEY")
            or getattr(settings, "OPENROUTER_API_KEY", None)
            or os.getenv("OPENROUTER_API_KEY")
        )
        if not api_key:
            raise ImproperlyConfigured(
                "Missing CHATBOT_EMBEDDING_API_KEY (or NVIDIA_API_KEY / OPENROUTER_API_KEY) for embedding service."
            )

        self._backend = ExternalAPIEmbeddingBackend(
            model=model,
            api_key=api_key,
            base_url=base_url,
        )

    def embed_text(self, text: str) -> List[float]:
        return self._backend.embed_text(text)

    def embed_texts(self, texts: List[str], batch_size: int = 50) -> List[List[float]]:
        return self._backend.embed_texts(texts, batch_size=batch_size)
