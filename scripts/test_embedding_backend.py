import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurantBE.settings.local")

import django
django.setup()

from django.core.exceptions import ImproperlyConfigured
from restaurantBE.chatbot.rag.embedding import (
    EmbeddingService,
    LocalEmbeddingBackend,
    ExternalAPIEmbeddingBackend,
)


class TestEmbeddingBackend(unittest.TestCase):

    def setUp(self):
        # Clear cached model instance between tests
        LocalEmbeddingBackend._model_instance = None

    def test_local_backend_lazy_loading(self):
        """Verify that SentenceTransformers is lazy loaded only when a model is requested."""
        # Unload sentence_transformers if it was somehow loaded
        if "sentence_transformers" in sys.modules:
            del sys.modules["sentence_transformers"]

        # Instantiate backend, it shouldn't import sentence_transformers yet
        backend = LocalEmbeddingBackend(model="intfloat/multilingual-e5-small", device="cpu")
        self.assertNotIn("sentence_transformers", sys.modules, "sentence_transformers imported too early!")

        # Now mock the SentenceTransformer class so we don't actually download/load the heavy model
        mock_transformer_class = MagicMock()
        mock_transformer_instance = MagicMock()
        mock_transformer_class.return_value = mock_transformer_instance
        
        # Mock encode to return a dummy embedding
        mock_transformer_instance.encode.return_value = MagicMock(tolist=lambda: [0.1, 0.2, 0.3])

        with patch.dict("sys.modules", {"sentence_transformers": MagicMock(SentenceTransformer=mock_transformer_class)}):
            # Requesting the model should now trigger the import (or mock usage)
            model = backend._get_model()
            self.assertIsNotNone(model)
            
            # Verify encoding/embedding behaves as expected
            emb = backend.embed_text("test query")
            self.assertEqual(emb, [0.1, 0.2, 0.3])
            
            # Verify batch embedding
            mock_transformer_instance.encode.return_value = MagicMock(tolist=lambda: [[0.1, 0.2, 0.3]])
            embs = backend.embed_texts(["test text"])
            self.assertEqual(embs, [[0.1, 0.2, 0.3]])

    def test_gemini_backend_options(self):
        """Verify that ExternalAPIEmbeddingBackend parses and applies HttpOptions and EmbedContentConfig correctly."""
        mock_genai = MagicMock()
        mock_client = MagicMock()
        mock_genai.genai.Client.return_value = mock_client
        
        # Mock response structure for genai client:
        # client.models.embed_content returns a response with .embeddings[0].values
        mock_value = MagicMock(values=[0.5, 0.6, 0.7])
        mock_response = MagicMock(embeddings=[mock_value])
        mock_client.models.embed_content.return_value = mock_response

        with patch.dict("sys.modules", {"google": mock_genai, "google.genai": mock_genai, "google.genai.types": mock_genai.types}):
            # Set up the backend
            backend = ExternalAPIEmbeddingBackend(
                model="gemini-embedding-001",
                api_key="test-api-key",
                base_url="https://test-api.google.com",
                dimensions=768,
                timeout=15,
            )

            # Check Client initialization arguments
            mock_genai.genai.Client.assert_called_once()
            called_kwargs = mock_genai.genai.Client.call_args[1]
            self.assertEqual(called_kwargs["api_key"], "test-api-key")
            
            # Check http_options passed to genai.Client
            http_options = called_kwargs.get("http_options")
            self.assertIsNotNone(http_options)

            # Test embedding text
            emb = backend.embed_text("hello world")
            self.assertEqual(emb, [0.5, 0.6, 0.7])

            # Verify client.models.embed_content was called with the correct config
            mock_client.models.embed_content.assert_called_once()
            call_kwargs = mock_client.models.embed_content.call_args[1]
            self.assertEqual(call_kwargs["model"], "gemini-embedding-001")
            self.assertEqual(call_kwargs["contents"], "hello world")
            
            # Check config structure
            config = call_kwargs.get("config")
            self.assertIsNotNone(config)

            # Assert HttpOptions was initialized with milliseconds (15 seconds * 1000 = 15000)
            mock_genai.types.HttpOptions.assert_any_call(timeout=15000)

    def test_embedding_service_routing(self):
        """Verify that EmbeddingService routes to the correct backend depending on provider selection."""
        # 1. Local Routing
        service_local = EmbeddingService(provider="local")
        self.assertEqual(service_local.provider, "local")
        self.assertIsInstance(service_local._backend, LocalEmbeddingBackend)

        # 2. Gemini Routing
        mock_genai = MagicMock()
        with patch.dict("sys.modules", {"google": mock_genai, "google.genai": mock_genai, "google.genai.types": mock_genai.types}):
            service_gemini = EmbeddingService(
                provider="gemini",
                api_key="dummy-key",
                dimensions=512,
                timeout=45,
            )
            self.assertEqual(service_gemini.provider, "gemini")
            self.assertIsInstance(service_gemini._backend, ExternalAPIEmbeddingBackend)
            self.assertEqual(service_gemini.dimensions, 512)
            self.assertEqual(service_gemini.timeout, 45)


if __name__ == "__main__":
    unittest.main()
