from __future__ import annotations

import logging
import os
import re
from typing import List, Optional, Dict, Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

from pydantic import BaseModel, Field

class EnglishChatbotResponse(BaseModel):
    answer: str = Field(
        description=(
            "The natural language answer to the user's question, based on the provided context. "
            "You MUST respond in English. "
            "You MUST format all prices and currency in English/US style "
            "(e.g., '30,000 VND', '200,000 dong', '$1.20', '$8.00') using a comma as the thousands separator and dot "
            "as the decimal separator. Never use Vietnamese currency terms like 'đồng' or 'VNĐ' with dot separators (e.g., '30.000') in English replies."
        )
    )
    suggest_items: bool = Field(
        description="True if the user's query or conversational intent is asking for food/drink suggestions, prices, menu, or recommendations. False if it is a general/informational FAQ query (like WiFi password, restaurant location, opening hours, policies, reservation general info)."
    )

class VietnameseChatbotResponse(BaseModel):
    answer: str = Field(
        description=(
            "The natural language answer to the user's question, based on the provided context. "
            "You MUST respond in Vietnamese. "
            "You MUST format all prices and currency in Vietnamese style "
            "(e.g., '30.000 đồng', '30.000 VNĐ', '30.000đ') using a dot as the thousands separator and comma as the "
            "decimal separator. Never use English separators like comma for thousands (e.g., '30,000 VND') in Vietnamese replies."
        )
    )
    suggest_items: bool = Field(
        description="True if the user's query or conversational intent is asking for food/drink suggestions, prices, menu, or recommendations. False if it is a general/informational FAQ query (like WiFi password, restaurant location, opening hours, policies, reservation general info)."
    )

# Retained for backward compatibility
ChatbotResponse = VietnameseChatbotResponse

SYSTEM_PROMPT_EN = (
    "You are VietFood assistant for a restaurant in Da Nang. "
    "You MUST respond in English. "
    "You MUST format all prices and monetary values in English/US style (e.g., '$1.20', '$8.00', '30,000 VND', '200,000 dong') with a comma as the thousands separator and dot as the decimal separator. Do not use Vietnamese terms like 'đồng' or 'VNĐ' with dot separators (e.g. do not write '30.000 đồng') in English replies. "
    "Answer naturally and concisely based strictly on the provided CONTEXT."
)

SYSTEM_PROMPT_VI = (
    "You are VietFood assistant for a restaurant in Da Nang. "
    "You MUST respond in Vietnamese. "
    "You MUST format all prices and monetary values in Vietnamese style (e.g., '30.000 đồng', '30.000 VNĐ', or '30.000đ') with a dot as the thousands separator and comma as the decimal separator. Do not use English separators like comma for thousands (e.g. do not write '30,000 VND') in Vietnamese replies. "
    "Answer naturally and concisely based strictly on the provided CONTEXT."
)

SYSTEM_PROMPT = SYSTEM_PROMPT_VI


import json

def repair_and_parse_json(text: str) -> Optional[dict]:
    text = text.strip()
    if not text.startswith("{"):
        return None
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    for suffix in ('"}', '"', '}', '"}', '", "suggest_items": false}', '", "suggest_items": true}'):
        try:
            parsed = json.loads(text + suffix)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            continue
    return None

def extract_answer_via_regex(text: str) -> Optional[str]:
    match = re.search(r'"answer"\s*:\s*"(.*)', text)
    if not match:
        match = re.search(r'\\"?answer\\"?\s*:\s*\\"(.*)', text)
    
    if match:
        rest = match.group(1)
        escaped = False
        chars = []
        for char in rest:
            if escaped:
                chars.append(char)
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                break
            else:
                chars.append(char)
        return "".join(chars)
    return None

def unwrap_nested_json(val: Any) -> str:
    if isinstance(val, str):
        val_stripped = val.strip()
        if val_stripped.startswith("{"):
            parsed = repair_and_parse_json(val_stripped)
            if parsed and isinstance(parsed, dict) and "answer" in parsed:
                return unwrap_nested_json(parsed["answer"])
            
            regex_ans = extract_answer_via_regex(val_stripped)
            if regex_ans is not None:
                return unwrap_nested_json(regex_ans)
    return val

def clean_and_parse_llm_response(raw_content: str) -> Dict[str, Any]:
    raw_content = raw_content.strip()
    if not raw_content:
        return {"answer": "", "suggest_items": False}

    # 1. Strip markdown code blocks if present
    if raw_content.startswith("```"):
        lines = raw_content.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw_content = "\n".join(lines).strip()

    # 2. Try direct/repaired JSON parsing
    parsed = repair_and_parse_json(raw_content)
    if parsed and isinstance(parsed, dict):
        answer = parsed.get("answer", "")
        suggest_items = parsed.get("suggest_items", False)
        answer = unwrap_nested_json(answer)
        if isinstance(suggest_items, str):
            suggest_items = suggest_items.lower() in {"1", "true", "yes", "on"}
        return {"answer": str(answer), "suggest_items": bool(suggest_items)}

    # 3. Fallback to regex extraction
    answer = ""
    suggest_items = False

    suggest_items_match = re.search(r'"suggest_items"\s*:\s*(true|false|1|0)', raw_content, re.IGNORECASE)
    if suggest_items_match:
        suggest_items = suggest_items_match.group(1).lower() in {"true", "1"}

    regex_ans = extract_answer_via_regex(raw_content)
    if regex_ans is not None:
        answer = regex_ans
    else:
        answer = raw_content

    answer = unwrap_nested_json(answer)

    return {"answer": str(answer), "suggest_items": bool(suggest_items)}


class LLMService:
    """Wrapper around Google GenAI for RAG answer generation."""

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
            or getattr(settings, "GEMINI_API_KEY", None)
            or os.getenv("GEMINI_API_KEY")
        )
        if not self.api_key:
            raise ImproperlyConfigured("Missing API Key for chatbot LLM service.")

        self.model = (
            model
            or getattr(settings, "CHATBOT_LLM_MODEL", None)
            or os.getenv("CHATBOT_LLM_MODEL")
            or "gemini-2.5-flash"
        )

        # Cấu hình Temperature
        conf_temp = getattr(settings, "CHATBOT_LLM_TEMPERATURE", 0.2)
        self.temperature = temperature if temperature is not None else float(conf_temp)

        # Cấu hình Max Tokens
        conf_max_tokens = getattr(settings, "CHATBOT_LLM_MAX_TOKENS", 300)
        self.max_tokens = int(conf_max_tokens)

        # Cấu hình Reasoning (kept for backward compatibility, not used by genai client directly)
        conf_reasoning = getattr(settings, "CHATBOT_LLM_REASONING_ENABLED", False)
        self.reasoning_enabled = (
            reasoning_enabled if reasoning_enabled is not None else bool(conf_reasoning)
        )

        try:
            from google import genai
        except ImportError as exc:
            raise ImproperlyConfigured("Please install google-genai package.") from exc

        self._client = genai.Client(api_key=self.api_key)
        logger.info(
            "LLM service initialized with model='%s'.",
            self.model,
        )

    def generate(
        self,
        user_message: str,
        context_text: str,
        history: Optional[List[dict]] = None,
        max_tokens: Optional[int] = None,
        lang: str = "vi",
    ) -> Dict[str, Any]:
        """Giải quyết câu trả lời."""
        from google.genai import types

        contents = []

        if history:
            for item in history[-12:]:
                role = str(item.get("role") or "").lower()
                content = str(item.get("content") or "").strip()
                if role == "assistant":
                    role = "model"
                if role in {"user", "model"} and content:
                    contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=content)]
                        )
                    )

        prompt = self._build_user_prompt(user_message, context_text)
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )
        )

        limit_tokens = max_tokens if max_tokens is not None else self.max_tokens

        system_instruction = SYSTEM_PROMPT_EN if lang == "en" else SYSTEM_PROMPT_VI
        response_schema = EnglishChatbotResponse if lang == "en" else VietnameseChatbotResponse

        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=self.temperature,
                max_output_tokens=limit_tokens,
                response_mime_type="application/json",
                response_schema=response_schema,
            )

            def _call():
                return self._client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config,
                )

            import time
            delay = 2.0
            for attempt in range(5):
                try:
                    response = _call()
                    break
                except Exception as exc:
                    exc_str = str(exc)
                    is_transient = any(
                        err in exc_str
                        for err in [
                            "429",
                            "503",
                            "500",
                            "502",
                            "504",
                            "RESOURCE_EXHAUSTED",
                            "UNAVAILABLE",
                            "DEADLINE_EXCEEDED",
                        ]
                    )
                    if is_transient:
                        logger.warning(
                            "LLM generation transient error (%s). Retrying in %.2f seconds (attempt %d/5)...",
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

            raw_content = response.text.strip() if response.text else ""
            parsed = clean_and_parse_llm_response(raw_content)
            answer = parsed["answer"]
            suggest_items = parsed["suggest_items"]
        except Exception as exc:
            logger.error("LLM generation failed: %s", exc)
            raise RuntimeError(f"LLM request failed: {exc}") from exc

        return {"answer": answer, "suggest_items": suggest_items}

    @staticmethod
    def _build_user_prompt(user_message: str, context_text: str) -> str:
        clean_context = (context_text or "").strip()
        if clean_context:
            return f"CONTEXT:\n{clean_context}\n\nUSER QUESTION:\n{user_message}"
        return f"CONTEXT:\nNo relevant context.\n\nUSER QUESTION:\n{user_message}"
