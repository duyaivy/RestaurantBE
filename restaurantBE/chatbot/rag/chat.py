"""
ChatService
-----------
Orchestrator: nhận user_message + history → gọi RAG → gọi LLM → trả kết quả.

SOLID:
  - Single Responsibility: chỉ điều phối luồng chat, không tự xử lý RAG hay LLM.
  - Dependency Inversion: nhận RetrievalService và LLMService qua constructor.
"""

from __future__ import annotations

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
            }

        rag_data = self.retrieval_service.build_context(
            query=clean_message,
            top_k=top_k,
            max_distance=max_distance,
        )

        answer = self.llm_service.generate(
            user_message=clean_message,
            context_text=rag_data["context_text"],
            history=history or [],
        )

        return {
            "answer": answer,
            "citations": rag_data["citations"],
        }
