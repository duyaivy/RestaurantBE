"""Embedding service backed by an external OpenAI-compatible API."""

from __future__ import annotations

import hashlib
import logging
import os
from typing import List

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured


logger = logging.getLogger(__name__)


class ExternalAPIEmbeddingBackend:
    def __init__(self, model: str, api_key: str, base_url: str | None = None) -> None:
        try:
            from google import genai
        except ImportError as exc:
            raise ImproperlyConfigured("Please install the 'google-genai' package.") from exc

        self.model = model
        self.client = genai.Client(api_key=api_key)
        logger.info(
            "Embedding backend initialized with model='%s'.",
            model,
        )

    def embed_text(self, text: str) -> List[float]:
        import time
        text = (text or "").strip()
        if not text:
            logger.warning("Received empty text for embedding.")
            return []

        def _call():
            return self.client.models.embed_content(
                model=self.model,
                contents=text,
            )

        try:
            delay = 2.0
            for attempt in range(5):
                try:
                    response = _call()
                    break
                except Exception as exc:
                    exc_str = str(exc)
                    if "429" in exc_str or "RESOURCE_EXHAUSTED" in exc_str:
                        logger.warning(
                            "Embedding rate limit hit (429). Retrying in %.2f seconds (attempt %d/5)...",
                            delay,
                            attempt + 1,
                        )
                        time.sleep(delay)
                        delay *= 2.0
                    else:
                        raise
            else:
                response = _call()
        except Exception as exc:
            raise RuntimeError(self._build_embedding_error_message(exc)) from exc
        return response.embeddings[0].values

    def embed_texts(self, texts: List[str], batch_size: int = 50) -> List[List[float]]:
        import time
        clean = [(t or "").strip() for t in texts if (t or "").strip()]
        if not clean:
            return []
        all_embeddings: List[List[float]] = []
        for start in range(0, len(clean), batch_size):
            batch = clean[start : start + batch_size]

            def _call():
                return self.client.models.embed_content(
                    model=self.model,
                    contents=batch,
                )

            try:
                delay = 2.0
                for attempt in range(5):
                    try:
                        response = _call()
                        break
                    except Exception as exc:
                        exc_str = str(exc)
                        if "429" in exc_str or "RESOURCE_EXHAUSTED" in exc_str:
                            logger.warning(
                                "Embedding batch rate limit hit (429). Retrying in %.2f seconds (attempt %d/5)...",
                                delay,
                                attempt + 1,
                            )
                            time.sleep(delay)
                            delay *= 2.0
                        else:
                            raise
                else:
                    response = _call()
            except Exception as exc:
                raise RuntimeError(self._build_embedding_error_message(exc)) from exc
            all_embeddings.extend(item.values for item in response.embeddings)
        return all_embeddings

    def _build_embedding_error_message(self, exc: Exception) -> str:
        return f"Embedding request failed: {exc}"


class LocalEmbeddingBackend:
    _model_instance = None

    def __init__(
        self,
        model: str,
        device: str = "cpu",
        normalize: bool = True,
    ) -> None:
        self.model = model
        self.device = device
        self.normalize = normalize
        logger.info(
            "LocalEmbeddingBackend initialized with model='%s', device='%s', normalize=%s.",
            model,
            device,
            normalize,
        )

    def _get_model(self):
        if LocalEmbeddingBackend._model_instance is None:
            logger.info("Loading sentence-transformers model '%s' on %s...", self.model, self.device)
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise ImproperlyConfigured("Please install the 'sentence-transformers' package.") from exc
            LocalEmbeddingBackend._model_instance = SentenceTransformer(self.model, device=self.device)
            logger.info("Model loaded successfully.")
        return LocalEmbeddingBackend._model_instance

    def embed_text(self, text: str) -> List[float]:
        text = (text or "").strip()
        if not text:
            logger.warning("Received empty text for embedding.")
            return []

        prefixed_text = f"query: {text}"
        model = self._get_model()
        embedding = model.encode(
            prefixed_text,
            normalize_embeddings=self.normalize,
            show_progress_bar=False,
        )
        return embedding.tolist()

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        clean = [(t or "").strip() for t in texts if (t or "").strip()]
        if not clean:
            return []

        prefixed_texts = [f"passage: {t}" for t in clean]
        model = self._get_model()
        embeddings = model.encode(
            prefixed_texts,
            batch_size=batch_size,
            normalize_embeddings=self.normalize,
            show_progress_bar=False,
        )
        return embeddings.tolist()


class EmbeddingService:

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        device: str | None = None,
        normalize: bool | None = None,
    ) -> None:
        self.provider = (
            provider
            or getattr(settings, "CHATBOT_EMBEDDING_PROVIDER", None)
            or "local"
        )

        self.model = (
            model
            or getattr(settings, "CHATBOT_EMBEDDING_MODEL", None)
            or ("intfloat/multilingual-e5-small" if self.provider == "local" else "gemini-embedding-001")
        )

        if self.provider == "local":
            self.device = device or getattr(settings, "CHATBOT_EMBEDDING_DEVICE", "cpu")
            self.normalize = normalize if normalize is not None else getattr(settings, "CHATBOT_EMBEDDING_NORMALIZE", True)
            self._backend = LocalEmbeddingBackend(
                model=self.model,
                device=self.device,
                normalize=self.normalize,
            )
        else:
            base_url = (
                base_url
                or getattr(settings, "CHATBOT_EMBEDDING_BASE_URL", None)
                or "https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            api_key = (
                api_key
                or getattr(settings, "CHATBOT_EMBEDDING_API_KEY", None)
                or os.getenv("CHATBOT_EMBEDDING_API_KEY")
                or getattr(settings, "GEMINI_API_KEY", None)
                or os.getenv("GEMINI_API_KEY")
            )
            if not api_key:
                raise ImproperlyConfigured(
                    "Missing CHATBOT_EMBEDDING_API_KEY (or GEMINI_API_KEY) for external embedding service."
                )
            self._backend = ExternalAPIEmbeddingBackend(
                model=self.model,
                api_key=api_key,
                base_url=base_url,
            )

    def embed_text(self, text: str) -> List[float]:
        text = (text or "").strip()
        if not text:
            return []

        h = hashlib.md5(text.encode("utf-8")).hexdigest()
        cache_key = f"emb:{self.provider}:{self.model}:{h}"
        cached_val = cache.get(cache_key)
        if cached_val is not None:
            logger.debug("Embedding cache hit for text: '%s...'", text[:30])
            return cached_val

        embedding = self._backend.embed_text(text)
        if embedding:
            cache.set(cache_key, embedding, timeout=2592000)  # 30 days cache
        return embedding

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        return self._backend.embed_texts(texts, batch_size=batch_size)
