from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class IngestService:
    def __init__(
        self,
        raw_data_dir: Optional[str] = None,
        chunking_service=None,
        embedding_service=None,
        vector_db_service=None,
        catalog_document_service=None,
    ) -> None:
        from .catalog_document import CatalogDocumentService
        from .chunking import TextChunkingService
        from .embedding import EmbeddingService
        from .vector_db import VectorDBService

        self.raw_data_dir = Path(
            raw_data_dir or (Path(__file__).resolve().parent / "raw_data")
        )
        self.chunking_service = chunking_service or TextChunkingService()
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_db_service = vector_db_service or VectorDBService()
        self.catalog_document_service = (
            catalog_document_service or CatalogDocumentService()
        )

    def is_ready(self) -> bool:
        """Vector DB readiness check for first-time initialization."""
        try:
            return self.vector_db_service.count() > 0
        except Exception:
            logger.exception("[RAG] Unable to check vector db readiness")
            return False

    def ingest_all(
        self,
        reset_collection: bool = False,
        include_markdown: bool = True,
        include_catalog: bool = True,
    ) -> Dict[str, Any]:
        if reset_collection:
            logger.info("[RAG] Resetting vector collection before ingest")
            self.vector_db_service.delete_all()

        result: Dict[str, Any] = {}

        if include_catalog:
            result["catalog"] = self._ingest_catalog_data()

        if include_markdown:
            result["markdown"] = self._ingest_markdown_files()

        result["total_documents_in_db"] = self.vector_db_service.count()
        return result

    def ingest_single_dish(self, dish_id: int) -> bool:
        """
        Upsert only one dish document to keep indexing out of request flow.
        """
        from restaurantBE.dishes.models import Dish

        try:
            dish = Dish.objects.select_related("category_id").get(pk=dish_id)
        except Dish.DoesNotExist:
            logger.warning("[RAG] Dish %s does not exist", dish_id)
            return False

        category = getattr(dish, "category_id", None)
        document = self.catalog_document_service.build_dish_document(
            dish=dish,
            category=category,
        )
        inserted = self._embed_and_upsert([document])
        return inserted > 0

    def _ingest_catalog_data(self) -> Dict[str, Any]:
        from restaurantBE.categories.models import Category
        from restaurantBE.dishes.models import Dish

        categories = list(Category.objects.all().order_by("id"))
        category_documents = [
            self.catalog_document_service.build_category_document(category)
            for category in categories
        ]

        dishes = list(Dish.objects.select_related("category_id").all().order_by("id"))
        dish_documents = []
        for dish in dishes:
            category = getattr(dish, "category_id", None)
            dish_documents.append(
                self.catalog_document_service.build_dish_document(
                    dish=dish,
                    category=category,
                )
            )

        indexed_categories = self._reindex_documents(
            source_type="CATEGORY", documents=category_documents
        )
        indexed_dishes = self._reindex_documents(
            source_type="DISH", documents=dish_documents
        )

        return {
            "categories": indexed_categories,
            "dishes": indexed_dishes,
            "total_documents": indexed_categories + indexed_dishes,
        }

    def _ingest_markdown_files(self) -> Dict[str, Any]:
        files = self._get_supported_files()
        total_files = 0
        total_chunks = 0
        file_results: List[Dict[str, Any]] = []

        for file_path in files:
            chunk_count = self._ingest_markdown_file(file_path)
            total_files += 1
            total_chunks += chunk_count
            file_results.append({"file": file_path.name, "chunks": chunk_count})

        return {
            "total_files": total_files,
            "total_chunks": total_chunks,
            "files": file_results,
        }

    def _ingest_markdown_file(self, file_path: Path) -> int:
        if not file_path.exists():
            return 0

        raw_text = file_path.read_text(encoding="utf-8")
        chunks = self.chunking_service.split_text(raw_text)
        if not chunks:
            return 0

        relative_source = file_path.relative_to(self.raw_data_dir).as_posix()
        documents = []
        for index, chunk_text in enumerate(chunks):
            documents.append(
                {
                    "id": self._build_chunk_id(relative_source, index),
                    "content": chunk_text,
                    "metadata": {
                        "source_type": "MARKDOWN",
                        "source": relative_source,
                        "object_id": f"{relative_source}:{index}",
                        "title": file_path.stem,
                        "language": "vi_en",
                        "chunk_index": index,
                        "file_name": file_path.name,
                    },
                }
            )

        self.vector_db_service.delete_by_where({"source": relative_source})
        return self._embed_and_upsert(documents)

    def _reindex_documents(
        self, source_type: str, documents: List[Dict[str, Any]]
    ) -> int:
        self.vector_db_service.delete_by_source_type(source_type)
        return self._embed_and_upsert(documents)

    def _embed_and_upsert(self, documents: List[Dict[str, Any]]) -> int:
        valid_documents = [
            document
            for document in documents
            if str(document.get("content") or "").strip()
        ]
        if not valid_documents:
            return 0

        texts = [document["content"] for document in valid_documents]
        embeddings = self.embedding_service.embed_texts(texts)

        prepared_documents = []
        for document, embedding in zip(valid_documents, embeddings):
            prepared_documents.append({**document, "embedding": embedding})

        return self.vector_db_service.upsert_documents(prepared_documents)

    def _get_supported_files(self) -> List[Path]:
        if not self.raw_data_dir.exists():
            return []

        supported_suffixes = {".md", ".txt"}
        return sorted(
            path
            for path in self.raw_data_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in supported_suffixes
        )

    @staticmethod
    def _build_chunk_id(source: str, chunk_index: int) -> str:
        safe_source = source.replace("/", "__").replace("\\", "__").replace(".", "_")
        return f"{safe_source}__chunk_{chunk_index}"
