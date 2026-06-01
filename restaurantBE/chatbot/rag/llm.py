from __future__ import annotations

import logging
import os
import re
from typing import List, Optional, Dict, Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# JSON parsing utilities
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# LLM Backends
# ---------------------------------------------------------------------------

class GeminiLLMBackend:
    """Google Gemini backend using google-genai SDK."""

    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int) -> None:
        try:
            from google import genai
        except ImportError as exc:
            raise ImproperlyConfigured("Please install google-genai package.") from exc

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = genai.Client(api_key=api_key)
        logger.info("GeminiLLMBackend initialized with model='%s'.", model)

    def generate(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        response_schema: type,
        max_tokens: Optional[int] = None,
    ) -> str:
        from google.genai import types

        # Convert OpenAI-style messages to Gemini Content format
        contents = []
        for msg in messages:
            role = msg["role"]
            if role == "assistant":
                role = "model"
            if role in {"user", "model"}:
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg["content"])]
                    )
                )

        limit_tokens = max_tokens if max_tokens is not None else self.max_tokens
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=self.temperature,
            max_output_tokens=limit_tokens,
            response_mime_type="application/json",
            response_schema=response_schema,
        )

        import time
        delay = 2.0
        for attempt in range(5):
            try:
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config,
                )
                return response.text.strip() if response.text else ""
            except Exception as exc:
                exc_str = str(exc)
                is_transient = any(
                    err in exc_str
                    for err in ["429", "503", "500", "502", "504", "RESOURCE_EXHAUSTED", "UNAVAILABLE", "DEADLINE_EXCEEDED"]
                )
                if is_transient:
                    logger.warning("Gemini transient error (%s). Retrying in %.2fs (attempt %d/5)...", exc_str, delay, attempt + 1)
                    time.sleep(delay)
                    delay *= 2.0
                else:
                    raise

        # Final attempt
        response = self._client.models.generate_content(
            model=self.model, contents=contents, config=config,
        )
        return response.text.strip() if response.text else ""


class GroqLLMBackend:
    """Groq backend using OpenAI-compatible API."""

    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int) -> None:
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        logger.info("GroqLLMBackend initialized with model='%s'.", model)

    def generate(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        response_schema: type = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        import time
        import requests

        # Build OpenAI-compatible messages
        # Groq requires the word "json" in messages when using response_format=json_object
        # Groq doesn't support response_schema like Gemini, so we must describe the format in the prompt
        json_schema_hint = (
            ' You must reply with a valid JSON object in this exact format: '
            '{"answer": "<your answer text>", "suggest_items": true_or_false}. '
            'The "answer" field contains your reply. '
            'The "suggest_items" field is a boolean: true if the user asks for food/drink suggestions, prices, menu, or recommendations; false for general FAQ queries.'
        )
        system_text = system_instruction + json_schema_hint
        api_messages = [{"role": "system", "content": system_text}]
        api_messages.extend(messages)

        limit_tokens = max_tokens if max_tokens is not None else self.max_tokens

        payload = {
            "model": self.model,
            "messages": api_messages,
            "temperature": self.temperature,
            "max_tokens": limit_tokens,
            "response_format": {"type": "json_object"},
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        delay = 2.0
        for attempt in range(5):
            try:
                resp = requests.post(
                    self.API_URL,
                    headers=headers,
                    json=payload,
                    timeout=60,
                )
                if resp.status_code == 429:
                    logger.warning("Groq rate limit hit. Retrying in %.2fs (attempt %d/5)...", delay, attempt + 1)
                    time.sleep(delay)
                    delay *= 2.0
                    continue

                if resp.status_code in {500, 502, 503}:
                    logger.warning("Groq server error %d. Retrying in %.2fs (attempt %d/5)...", resp.status_code, delay, attempt + 1)
                    time.sleep(delay)
                    delay *= 2.0
                    continue

                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()

            except requests.exceptions.Timeout:
                logger.warning("Groq timeout. Retrying in %.2fs (attempt %d/5)...", delay, attempt + 1)
                time.sleep(delay)
                delay *= 2.0
            except requests.exceptions.RequestException as exc:
                logger.warning("Groq request error (%s). Retrying in %.2fs (attempt %d/5)...", exc, delay, attempt + 1)
                time.sleep(delay)
                delay *= 2.0

        # Final attempt
        resp = requests.post(self.API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


# ---------------------------------------------------------------------------
# LLM Service (multi-provider orchestrator)
# ---------------------------------------------------------------------------

_PROVIDER_DEFAULT_MODELS = {
    "gemini": "gemini-2.5-flash-lite",
    "groq": "llama-3.3-70b-versatile",
}


class LLMService:
    """Multi-provider LLM service for RAG answer generation.

    Supported providers (via CHATBOT_LLM_PROVIDER env):
      - gemini  (default) — Google Gemini via google-genai SDK
      - groq    — Groq via OpenAI-compatible API (free, fast)
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        reasoning_enabled: Optional[bool] = None,
    ) -> None:
        # Provider
        self.provider = (
            provider
            or getattr(settings, "CHATBOT_LLM_PROVIDER", None)
            or os.getenv("CHATBOT_LLM_PROVIDER")
            or "gemini"
        ).lower()

        # Model
        default_model = _PROVIDER_DEFAULT_MODELS.get(self.provider, "gemini-2.5-flash-lite")
        self.model = (
            model
            or getattr(settings, "CHATBOT_LLM_MODEL", None)
            or os.getenv("CHATBOT_LLM_MODEL")
            or default_model
        )

        # Temperature
        conf_temp = getattr(settings, "CHATBOT_LLM_TEMPERATURE", 0.2)
        self.temperature = temperature if temperature is not None else float(conf_temp)

        # Max tokens
        conf_max_tokens = getattr(settings, "CHATBOT_LLM_MAX_TOKENS", 300)
        self.max_tokens = int(max_tokens if max_tokens is not None else conf_max_tokens)

        # Reasoning (backward compat)
        conf_reasoning = getattr(settings, "CHATBOT_LLM_REASONING_ENABLED", False)
        self.reasoning_enabled = (
            reasoning_enabled if reasoning_enabled is not None else bool(conf_reasoning)
        )

        # Initialize backend
        if self.provider == "groq":
            resolved_key = (
                api_key
                or getattr(settings, "GROQ_API_KEY", None)
                or os.getenv("GROQ_API_KEY")
            )
            if not resolved_key:
                raise ImproperlyConfigured("Missing GROQ_API_KEY for Groq LLM provider.")
            self._backend = GroqLLMBackend(
                api_key=resolved_key,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        else:
            # Default: Gemini
            resolved_key = (
                api_key
                or getattr(settings, "GEMINI_API_KEY", None)
                or os.getenv("GEMINI_API_KEY")
            )
            if not resolved_key:
                raise ImproperlyConfigured("Missing GEMINI_API_KEY for Gemini LLM provider.")
            self._backend = GeminiLLMBackend(
                api_key=resolved_key,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

    def generate(
        self,
        user_message: str,
        context_text: str,
        history: Optional[List[dict]] = None,
        max_tokens: Optional[int] = None,
        lang: str = "vi",
    ) -> Dict[str, Any]:
        """Generate a RAG answer."""
        # Build messages list (OpenAI format — used by all backends)
        messages: List[Dict[str, str]] = []
        if history:
            for item in history[-12:]:
                role = str(item.get("role") or "").lower()
                content = str(item.get("content") or "").strip()
                if role in {"user", "assistant"} and content:
                    messages.append({"role": role, "content": content})

        prompt = self._build_user_prompt(user_message, context_text)
        messages.append({"role": "user", "content": prompt})

        system_instruction = SYSTEM_PROMPT_EN if lang == "en" else SYSTEM_PROMPT_VI
        response_schema = EnglishChatbotResponse if lang == "en" else VietnameseChatbotResponse

        try:
            raw_content = self._backend.generate(
                messages=messages,
                system_instruction=system_instruction,
                response_schema=response_schema,
                max_tokens=max_tokens,
            )
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
