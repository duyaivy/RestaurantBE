from __future__ import annotations

import logging
import os
import re
from typing import List, Optional, Dict, Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are VietFood assistant for a restaurant in Da Nang. "
    "Answer in Vietnamese when the user writes Vietnamese. "
    "Use only the provided CONTEXT. "
    "IMPORTANT: If you suggest dishes, you MUST extract the exact Numeric ID and Image URL "
    "provided in the context. Do not translate or invent IDs. "
    "Format each dish at the end: [ITEM: Name | Numeric_ID | Image_URL]. "
    "Example: [ITEM: Bún bò Huế | 101 | https://restaurant.com/anh.jpg]"
)


class LLMService:
    """Wrapper around OpenAI chat completion for RAG answer generation with item extraction."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
        reasoning_enabled: Optional[bool] = None,
    ) -> None:
        self.api_key = (
            api_key
            or getattr(settings, "OPENROUTER_API_KEY", None)
            or os.getenv("OPENROUTER_API_KEY")
            or getattr(settings, "OPENAI_API_KEY", None)
            or os.getenv("OPENAI_API_KEY")
        )
        if not self.api_key:
            raise ImproperlyConfigured("Missing API Key for chatbot LLM service.")

        self.base_url = (
            base_url
            or getattr(settings, "CHATBOT_LLM_BASE_URL", None)
            or os.getenv("CHATBOT_LLM_BASE_URL")
            or "https://integrate.api.nvidia.com/v1"  # Mặc định dùng NVIDIA
        )

        self.model = (
            model
            or getattr(settings, "CHATBOT_LLM_MODEL", None)
            or os.getenv("CHATBOT_LLM_MODEL")
            or "nvidia/nemotron-3-super-120b-a12b"
        )

        # Cấu hình Temperature
        conf_temp = getattr(settings, "CHATBOT_LLM_TEMPERATURE", 0.2)
        self.temperature = temperature if temperature is not None else float(conf_temp)

        # Cấu hình Reasoning
        conf_reasoning = getattr(settings, "CHATBOT_LLM_REASONING_ENABLED", False)
        self.reasoning_enabled = (
            reasoning_enabled if reasoning_enabled is not None else bool(conf_reasoning)
        )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImproperlyConfigured("Please install openai package.") from exc

        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def generate(
        self,
        user_message: str,
        context_text: str,
        history: Optional[List[dict]] = None,
        max_tokens: int = 800,
    ) -> Dict[str, Any]:
        """Giải quả kết quả kèm theo danh sách món ăn đã trích xuất."""
        messages: List[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

        if history:
            for item in history[-12:]:
                role = str(item.get("role") or "").lower()
                content = str(item.get("content") or "").strip()
                if role in {"user", "assistant"} and content:
                    messages.append({"role": role, "content": content})

        prompt = self._build_user_prompt(user_message, context_text)
        messages.append({"role": "user", "content": prompt})

        request_kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": max_tokens,
        }

        if self.reasoning_enabled:
            request_kwargs["extra_body"] = {"reasoning": {"enabled": True}}

        response = self._client.chat.completions.create(**request_kwargs)
        raw_content = (
            response.choices[0].message.content.strip() if response.choices else ""
        )

        # Bóc tách dữ liệu ITEM
        final_answer, suggested_items = self._parse_items(raw_content)

        return {"answer": final_answer, "items": suggested_items}

    @staticmethod
    def _parse_items(content: str) -> tuple[str, List[dict]]:
        """Bóc tách [ITEM: Name | ID | Image] từ chuỗi văn bản."""
        # Tìm pattern: [ITEM: Tên | ID | Link Ảnh]
        pattern = r"\[ITEM:\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\]"
        matches = re.findall(pattern, content)

        items = []
        for m in matches:
            items.append(
                {"name": m[0].strip(), "id": m[1].strip(), "image_url": m[2].strip()}
            )

        # Xóa các tag ITEM khỏi nội dung trả về để user không thấy chữ thô
        clean_text = re.sub(r"\[ITEM:.*?\]", "", content).strip()
        return clean_text, items

    @staticmethod
    def _build_user_prompt(user_message: str, context_text: str) -> str:
        clean_context = (context_text or "").strip()
        if clean_context:
            return f"CONTEXT:\n{clean_context}\n\nUSER QUESTION:\n{user_message}"
        return f"CONTEXT:\nNo relevant context.\n\nUSER QUESTION:\n{user_message}"
