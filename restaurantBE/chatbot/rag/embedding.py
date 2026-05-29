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
    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: str | None = None,
        dimensions: int | None = None,
        timeout: int | None = None,
    ) -> None:
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise ImproperlyConfigured("Please install the 'google-genai' package.") from exc

        self.model = model
        self.dimensions = dimensions
        self.timeout = timeout

        # Configure client using types.HttpOptions
        http_opts = {}
        if base_url:
            http_opts["base_url"] = base_url
        if timeout is not None:
            # google-genai HttpOptions expects timeout in milliseconds
            http_opts["timeout"] = timeout * 1000

        http_options = types.HttpOptions(**http_opts) if http_opts else None
        self.client = genai.Client(api_key=api_key, http_options=http_options)

        logger.info(
            "Embedding backend initialized with model='%s', dimensions=%s, timeout=%s.",
            model,
            dimensions,
            timeout,
        )

    def embed_text(self, text: str) -> List[float]:
        import time
        from google.genai import types
        text = (text or "").strip()
        if not text:
            logger.warning("Received empty text for embedding.")
            return []

        def _call():
            config_opts = {}
            if self.dimensions is not None:
                config_opts["output_dimensionality"] = self.dimensions
            if self.timeout is not None:
                # google-genai HttpOptions expects timeout in milliseconds
                config_opts["http_options"] = types.HttpOptions(timeout=self.timeout * 1000)

            config = types.EmbedContentConfig(**config_opts) if config_opts else None
            return self.client.models.embed_content(
                model=self.model,
                contents=text,
                config=config,
            )

        try:
            delay = 2.0
            for attempt in range(5):
                try:
                    response = _call()
                    break
                except Exception as exc:
                    exc_str = str(exc)
                    exc_lower = exc_str.lower()
                    if (
                        "429" in exc_lower
                        or "resource_exhausted" in exc_lower
                        or "timeout" in exc_lower
                        or "handshake" in exc_lower
                        or "connect" in exc_lower
                        or "network" in exc_lower
                        or "ssl" in exc_lower
                    ):
                        logger.warning(
                            "Embedding transient error hit (%s). Retrying in %.2f seconds (attempt %d/5)...",
                            exc_str,
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
        from google.genai import types
        clean = [(t or "").strip() for t in texts if (t or "").strip()]
        if not clean:
            return []
        all_embeddings: List[List[float]] = []
        for start in range(0, len(clean), batch_size):
            batch = clean[start : start + batch_size]

            def _call():
                config_opts = {}
                if self.dimensions is not None:
                    config_opts["output_dimensionality"] = self.dimensions
                if self.timeout is not None:
                    # google-genai HttpOptions expects timeout in milliseconds
                    config_opts["http_options"] = types.HttpOptions(timeout=self.timeout * 1000)

                config = types.EmbedContentConfig(**config_opts) if config_opts else None
                return self.client.models.embed_content(
                    model=self.model,
                    contents=batch,
                    config=config,
                )

            try:
                delay = 2.0
                for attempt in range(5):
                    try:
                        response = _call()
                        break
                    except Exception as exc:
                        exc_str = str(exc)
                        exc_lower = exc_str.lower()
                        if (
                            "429" in exc_lower
                            or "resource_exhausted" in exc_lower
                            or "timeout" in exc_lower
                            or "handshake" in exc_lower
                            or "connect" in exc_lower
                            or "network" in exc_lower
                            or "ssl" in exc_lower
                        ):
                            logger.warning(
                                "Embedding batch transient error hit (%s). Retrying in %.2f seconds (attempt %d/5)...",
                                exc_str,
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
        dimensions: int | None = None,
        timeout: int | None = None,
    ) -> None:
        self.provider = (
            provider
            or getattr(settings, "CHATBOT_EMBEDDING_PROVIDER", None)
            or "local"
        ).lower()

        default_model = "gemini-embedding-001" if self.provider == "gemini" else "intfloat/multilingual-e5-small"
        self.model = (
            model
            or getattr(settings, "CHATBOT_EMBEDDING_MODEL", None)
            or default_model
        )

        self.dimensions = (
            dimensions
            if dimensions is not None
            else getattr(settings, "CHATBOT_EMBEDDING_DIMENSIONS", 768)
        )

        self.timeout = (
            timeout
            if timeout is not None
            else getattr(settings, "CHATBOT_EMBEDDING_TIMEOUT_SECONDS", 30)
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
            )
            api_key = (
                api_key
                or getattr(settings, "CHATBOT_EMBEDDING_API_KEY", None)
            )
            if not api_key:
                raise ImproperlyConfigured(
                    "Missing CHATBOT_EMBEDDING_API_KEY for external embedding service."
                )
            self._backend = ExternalAPIEmbeddingBackend(
                model=self.model,
                api_key=api_key,
                base_url=base_url,
                dimensions=self.dimensions,
                timeout=self.timeout,
            )

    def embed_text(self, text: str) -> List[float]:
        text = (text or "").strip()
        if not text:
            return []

        h = hashlib.md5(text.encode("utf-8")).hexdigest()
        dim_suffix = f":{self.dimensions}" if self.provider != "local" else ""
        cache_key = f"emb:{self.provider}:{self.model}{dim_suffix}:{h}"
        cached_val = cache.get(cache_key)
        if cached_val is not None:
            logger.debug("Embedding cache hit for text: '%s...'", text[:30])
            return cached_val

        embedding = self._backend.embed_text(text)
        if embedding:
            cache.set(cache_key, embedding, timeout=2592000)  # 30 days cache
        return embedding

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        # Pre-check cache for list of texts to make batching extremely fast is optional, 
        # but forwarding to the backend is standard.
        return self._backend.embed_texts(texts, batch_size=batch_size)
