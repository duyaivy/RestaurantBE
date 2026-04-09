"""
ChatService
-----------
Orchestrator: nhận user_message + history → gọi RAG → gọi LLM → trả kết quả.

SOLID:
  - Single Responsibility: chỉ điều phối luồng chat, không tự xử lý RAG hay LLM.
  - Dependency Inversion: nhận RetrievalService và LLMService qua constructor.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from .llm import LLMService
from .retrieval import RetrievalService


class ChatService:
    def __init__(
        self,
        retrieval_service: RetrievalService | None = None,
        llm_service: LLMService | None = None,
    ) -> None:
        self.retrieval_service = retrieval_service or RetrievalService()
        self.llm_service = llm_service or LLMService()

    def reply(
        self,
        user_message: str,
        history: Optional[List[Dict[str, Any]]] = None,
        top_k: int = 5,
        max_distance: float = 1.2,
    ) -> Dict[str, Any]:
        """
        Xử lý 1 lượt chat.

        Args:
            user_message : tin nhắn người dùng
            history      : lịch sử hội thoại dạng
                           [{"role": "user"|"assistant", "content": "..."}]
            top_k        : số chunk lấy từ vector DB
            max_distance : ngưỡng cosine distance để lọc kết quả không liên quan

        Returns:
            {
              "answer"    : str,   # câu trả lời của bot
              "citations" : list,  # nguồn dữ liệu được dùng
            }
        """
        clean_message = (user_message or "").strip()
        if not clean_message:
            return {
                "answer": "Please provide a message so I can help you.",
                "citations": [],
                "items": [],
            }

        rag_data = self.retrieval_service.build_context(
            query=clean_message,
            top_k=top_k,
            max_distance=max_distance,
        )

        llm_result = self.llm_service.generate(
            user_message=clean_message,
            context_text=rag_data["context_text"],
            history=history or [],
        )

        answer = (
            llm_result.get("answer", "")
            if isinstance(llm_result, dict)
            else str(llm_result)
        )
        retrieved_items = self._extract_items_from_results(rag_data.get("results", []))

        # Nếu top results là FAQ/markdown, chạy thêm 1 lượt retrieve riêng cho món ăn.
        if not retrieved_items:
            dish_results = self.retrieval_service.search(
                query=clean_message,
                top_k=max(top_k, 8),
                where={"source_type": "DISH"},
                max_distance=None,
            )
            retrieved_items = self._extract_items_from_results(dish_results)

        # Không dùng fallback từ LLM để tránh id/image_url bị bịa.
        items = retrieved_items

        return {
            "answer": answer,
            "citations": rag_data["citations"],
            "items": items,
        }

    def _extract_items_from_results(
        self, results: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        items: List[Dict[str, str]] = []
        seen_ids = set()

        for item in results:
            metadata = item.get("metadata") or {}
            if metadata.get("source_type") != "DISH":
                continue

            dish_id = metadata.get("dish_id") or metadata.get("object_id")
            if dish_id is None:
                dish_id = self._extract_field_from_content(
                    item.get("content", ""), "Numeric_ID"
                )

            dish_id_str = str(dish_id).strip() if dish_id is not None else ""
            if not dish_id_str or dish_id_str in seen_ids:
                continue
            seen_ids.add(dish_id_str)

            name = (
                metadata.get("dish_name_vi")
                or metadata.get("dish_name_en")
                or metadata.get("title")
                or self._extract_field_from_content(
                    item.get("content", ""), "Ten tieng Viet"
                )
                or self._extract_field_from_content(
                    item.get("content", ""), "English name"
                )
                or "Unknown dish"
            )
            image_url = (
                metadata.get("image_url")
                or self._extract_field_from_content(
                    item.get("content", ""), "Image_URL"
                )
                or "(No URL provided)"
            )

            items.append(
                {
                    "name": str(name).strip(),
                    "id": dish_id_str,
                    "image_url": str(image_url).strip(),
                }
            )

        return items

    @staticmethod
    def _extract_field_from_content(content: str, field_name: str) -> str:
        pattern = rf"(?im)^\s*{re.escape(field_name)}\s*:\s*(.+?)\s*$"
        match = re.search(pattern, content or "")
        return match.group(1).strip() if match else ""
