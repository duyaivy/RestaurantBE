"""
RetrievalService
----------------
Nhận câu hỏi → embed → query VectorDB → trả về context_text + citations.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .embedding import EmbeddingService
from .vector_db import VectorDBService


logger = logging.getLogger(__name__)


class RetrievalService:
    def __init__(
        self,
        embedding: EmbeddingService | None = None,
        vector_db: VectorDBService | None = None,
    ) -> None:
        self.embedding = embedding or EmbeddingService()
        self.vector_db = vector_db or VectorDBService()
        self._bootstrap_attempted = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None,
        max_distance: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm thuần — trả về list raw results từ vector DB.
        max_distance: lọc kết quả quá xa (cosine distance). None = không lọc.
        """
        query = (query or "").strip()
        if not query:
            return []

        self._ensure_vector_index_ready()

        query_embedding = self.embedding.embed_text(query)
        results = self.vector_db.query(
            query_embedding=query_embedding,
            top_k=top_k,
            where=where,
        )

        if max_distance is not None:
            results = [
                r
                for r in results
                if r.get("distance") is not None and r["distance"] <= max_distance
            ]

        return results

    def _ensure_vector_index_ready(self) -> None:
        """
        Nếu collection rỗng (ví dụ vừa xoá thư mục .chroma), tự ingest lại dữ liệu.
        Chỉ thử 1 lần trong vòng đời process để tránh request nào cũng reindex.
        """
        if self._bootstrap_attempted:
            return

        try:
            current_count = self.vector_db.count()
        except Exception:
            logger.exception("[RAG] Unable to read vector DB count")
            current_count = 0

        if current_count > 0:
            return

        self._bootstrap_attempted = True
        logger.warning("[RAG] Vector DB is empty. Auto-ingesting catalog + markdown...")

        try:
            from .ingest import IngestService

            ingest_service = IngestService(
                embedding_service=self.embedding,
                vector_db_service=self.vector_db,
            )
            result = ingest_service.ingest_all(
                reset_collection=False,
                include_markdown=True,
                include_catalog=True,
            )
            logger.info(
                "[RAG] Auto-ingest completed. total_documents_in_db=%s",
                result.get("total_documents_in_db"),
            )
        except Exception:
            logger.exception("[RAG] Auto-ingest failed")

    def build_context(
        self,
        query: str,
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None,
        max_distance: Optional[float] = 1.2,
    ) -> Dict[str, Any]:
        """
        Tìm kiếm + build context string cho LLM.

        Returns:
            {
              "context_text": str,   # đã format sẵn để đưa vào prompt
              "citations":    list,  # [{source, title, distance}, ...]
              "results":      list,  # raw results
            }
        """
        results = self.search(
            query=query,
            top_k=top_k,
            where=where,
            max_distance=max_distance,
        )

        context_parts: List[str] = []
        citations: List[Dict[str, Any]] = []

        for item in results:
            metadata = item.get("metadata") or {}
            source = metadata.get("source", "unknown")
            title = metadata.get("title") or source

            context_parts.append(f"[Nguồn: {title}]\n{item['content']}")
            citations.append(
                {
                    "source": source,
                    "title": title,
                    "distance": item.get("distance"),
                }
            )

        return {
            "context_text": "\n\n---\n\n".join(context_parts),
            "citations": citations,
            "results": results,
        }
