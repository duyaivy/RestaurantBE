"""
VectorDBService
---------------
Wrapper quanh ChromaDB PersistentClient.
Cấu hình qua settings:
  CHATBOT_CHROMA_DIR        : đường dẫn thư mục lưu Chroma (mặc định chatbot/rag/.chroma)
  CHATBOT_CHROMA_COLLECTION : tên collection (mặc định "restaurant_chatbot")
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from django.conf import settings


class VectorDBService:
    def __init__(
        self,
        collection_name: Optional[str] = None,
        persist_directory: Optional[str] = None,
    ) -> None:
        default_chroma_dir = Path(__file__).resolve().parent / ".chroma"

        self.persist_directory = str(
            persist_directory
            or getattr(settings, "CHATBOT_CHROMA_DIR", None)
            or os.getenv("CHATBOT_CHROMA_DIR")
            or default_chroma_dir
        )

        self.collection_name = (
            collection_name
            or getattr(settings, "CHATBOT_CHROMA_COLLECTION", None)
            or os.getenv("CHATBOT_CHROMA_COLLECTION")
            or "restaurant_chatbot"
        )

        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

        self._client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def upsert_documents(self, documents: List[Dict[str, Any]]) -> int:
        """
        Upsert danh sách document vào collection.
        Mỗi document phải có: id, content, embedding, metadata (optional).
        Trả về số document được upsert thành công.
        """
        if not documents:
            return 0

        ids, texts, metadatas, embeddings = [], [], [], []

        for doc in documents:
            embedding = doc.get("embedding")
            content = str(doc.get("content") or "").strip()

            if not embedding or not content:
                continue

            ids.append(str(doc["id"]))
            texts.append(content)
            metadatas.append(self._sanitize_metadata(doc.get("metadata") or {}))
            embeddings.append(embedding)

        if not ids:
            return 0

        self._collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        return len(ids)

    def delete_by_where(self, where: Dict[str, Any]) -> None:
        """Xoá document theo filter metadata."""
        if not where:
            return
        self._collection.delete(where=where)

    def delete_by_source_type(self, source_type: str) -> None:
        """Xoá toàn bộ document có metadata.source_type == source_type."""
        if not source_type:
            return
        self._collection.delete(where={"source_type": source_type})

    def delete_all(self) -> None:
        """Xoá toàn bộ collection rồi tạo lại."""
        self._client.delete_collection(self.collection_name)
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm vector gần nhất.
        Trả về list dict: {id, content, metadata, distance}
        distance dùng cosine → giá trị càng nhỏ càng liên quan.
        """
        if not query_embedding:
            return []

        kwargs: Dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        result = self._collection.query(**kwargs)

        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        return [
            {
                "id": ids[i] if i < len(ids) else None,
                "content": documents[i],
                "metadata": metadatas[i] if i < len(metadatas) else {},
                "distance": distances[i] if i < len(distances) else None,
            }
            for i in range(len(documents))
        ]

    def count(self) -> int:
        """Trả về tổng số document trong collection."""
        return self._collection.count()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        ChromaDB chỉ chấp nhận str | int | float | bool trong metadata.
        Các kiểu khác được convert hoặc loại bỏ.
        """
        clean: Dict[str, Any] = {}
        for key, value in metadata.items():
            if value is None:
                continue
            if isinstance(value, bool):
                clean[key] = value
            elif isinstance(value, (str, int, float)):
                clean[key] = value
            elif isinstance(value, Decimal):
                clean[key] = float(value)
            elif isinstance(value, (datetime, date)):
                clean[key] = value.isoformat()
            else:
                try:
                    clean[key] = json.dumps(value, ensure_ascii=False)
                except (TypeError, ValueError):
                    clean[key] = str(value)
        return clean
