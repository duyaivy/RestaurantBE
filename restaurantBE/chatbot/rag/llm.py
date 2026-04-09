from __future__ import annotations

import logging
import os
import re
from typing import List, Optional

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are VietFood assistant for a restaurant in Da Nang. "
    "Answer in Vietnamese when the user writes Vietnamese, otherwise answer in English. "
    "Use only the provided CONTEXT. If context is missing or insufficient, be honest and "
    "ask the user to contact restaurant staff for confirmation. "
    "Keep answers concise, warm, and practical. "
    "Do not reveal internal metadata, ids, or distance scores. "
    "Return only the final answer for the user. "
    "Never include hidden reasoning, internal analysis, or step-by-step self-talk."
)


class LLMService:
    """Wrapper around OpenAI chat completion for RAG answer generation."""

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
            raise ImproperlyConfigured(
                "Missing OPENROUTER_API_KEY (or OPENAI_API_KEY) for chatbot LLM service."
            )

        self.base_url = (
            base_url
            or getattr(settings, "CHATBOT_LLM_BASE_URL", None)
            or os.getenv("CHATBOT_LLM_BASE_URL")
            or "https://openrouter.ai/api/v1"
        )

        self.model = (
            model
            or getattr(settings, "CHATBOT_LLM_MODEL", None)
            or os.getenv("CHATBOT_LLM_MODEL")
            or "nvidia/nemotron-3-super-120b-a12b:free"
        )

        configured_temperature = getattr(settings, "CHATBOT_LLM_TEMPERATURE", None)
        env_temperature = os.getenv("CHATBOT_LLM_TEMPERATURE")
        if temperature is not None:
            self.temperature = temperature
        elif configured_temperature is not None:
            self.temperature = float(configured_temperature)
        elif env_temperature is not None:
            self.temperature = float(env_temperature)
        else:
            self.temperature = 0.2

        if reasoning_enabled is not None:
            self.reasoning_enabled = reasoning_enabled
        else:
            configured_reasoning = getattr(
                settings, "CHATBOT_LLM_REASONING_ENABLED", None
            )
            env_reasoning = os.getenv("CHATBOT_LLM_REASONING_ENABLED")
            if configured_reasoning is not None:
                self.reasoning_enabled = bool(configured_reasoning)
            elif env_reasoning is not None:
                self.reasoning_enabled = env_reasoning.lower() in {
                    "1",
                    "true",
                    "yes",
                    "on",
                }
            else:
                self.reasoning_enabled = False

        # Free-tier models often expose verbose reasoning content.
        if self.reasoning_enabled and self.model.endswith(":free"):
            logger.warning(
                "Disabling reasoning for free model '%s' to avoid verbose trace output.",
                self.model,
            )
            self.reasoning_enabled = False

        try:
            from openai import OpenAI  # type: ignore
        except ImportError as exc:
            raise ImproperlyConfigured("Please install openai package.") from exc

        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def generate(
        self,
        user_message: str,
        context_text: str,
        history: Optional[List[dict]] = None,
        max_tokens: int = 700,
    ) -> str:
        messages: List[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

        if history:
            for item in history[-12:]:
                role = str(item.get("role") or "").lower()
                content = str(item.get("content") or "").strip()
                if role in {"user", "assistant"} and content:
                    messages.append({"role": role, "content": content})

        prompt = self._build_user_prompt(
            user_message=user_message, context_text=context_text
        )
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

        choice = response.choices[0] if response.choices else None
        message = choice.message if choice else None
        content = message.content.strip() if message and message.content else ""
        finish_reason = (choice.finish_reason or "").lower() if choice else ""

        if content:
            if self._looks_truncated_output(content, finish_reason):
                content = self._continue_truncated_answer(
                    messages=messages,
                    partial_answer=content,
                    max_tokens=max_tokens,
                )

            return self._finalize_answer(
                raw_answer=content,
                user_message=user_message,
                max_tokens=max_tokens,
            )

        return (
            "Xin loi, toi chua tim du thong tin de tra loi chinh xac. "
            "Ban co the hoi theo mon cu the hoac lien he nhan vien nha hang."
        )

    @staticmethod
    def _build_user_prompt(user_message: str, context_text: str) -> str:
        clean_context = (context_text or "").strip()
        if clean_context:
            return (
                "CONTEXT:\n" f"{clean_context}\n\n" "USER QUESTION:\n" f"{user_message}"
            )

        return (
            "CONTEXT:\nNo relevant context retrieved.\n\n"
            "USER QUESTION:\n"
            f"{user_message}"
        )

    def _finalize_answer(
        self, raw_answer: str, user_message: str, max_tokens: int
    ) -> str:
        answer = (raw_answer or "").strip()
        if not answer:
            return ""

        if not self._looks_like_reasoning_leak(answer):
            return answer

        logger.warning(
            "Detected reasoning-style output; attempting rewrite to final answer."
        )
        rewritten = self._rewrite_to_final_answer(
            leaked_answer=answer,
            user_message=user_message,
            max_tokens=max_tokens,
        )
        if rewritten and not self._looks_like_reasoning_leak(rewritten):
            return rewritten

        # Last resort: never return internal reasoning text to clients.
        return (
            "Xin lỗi, mình chưa thể trả lời rõ ràng ở lượt này. "
            "Bạn có thể hỏi lại ngắn gọn hơn để mình trả lời chính xác hơn nhé."
        )

    def _rewrite_to_final_answer(
        self,
        leaked_answer: str,
        user_message: str,
        max_tokens: int,
    ) -> str:
        rewrite_messages = [
            {
                "role": "system",
                "content": (
                    "Rewrite the assistant draft into a user-facing final answer only. "
                    "Do not include analysis, chain-of-thought, checklist, or step-by-step reasoning. "
                    "Keep it concise and practical."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Original user question:\n{user_message}\n\n"
                    f"Leaked draft answer:\n{leaked_answer}\n\n"
                    "Return only the final answer text."
                ),
            },
        ]

        rewrite_kwargs = {
            "model": self.model,
            "messages": rewrite_messages,
            "temperature": min(self.temperature, 0.2),
            "max_tokens": max_tokens,
        }
        if self.reasoning_enabled:
            rewrite_kwargs["extra_body"] = {"reasoning": {"enabled": False}}

        try:
            rewrite_response = self._client.chat.completions.create(**rewrite_kwargs)
            rewrite_message = (
                rewrite_response.choices[0].message
                if rewrite_response.choices
                else None
            )
            return (
                rewrite_message.content.strip()
                if rewrite_message and rewrite_message.content
                else ""
            )
        except Exception:
            logger.exception("Failed to rewrite leaked reasoning output")
            return ""

    @staticmethod
    def _looks_like_reasoning_leak(text: str) -> bool:
        if not text:
            return False

        lowered = text.lower()
        patterns = [
            r"\bokay,?\s+t[oô]i\s+c[aầ]n\b",
            r"\bt[oô]i\s+s[eẽ]\s+ki[eể]m\s+tra\b",
            r"\bph[aầ]n\s+th[uứ]\b",
            r"\bqu[eé]t\s+l[aạ]i\b",
            r"\bcontext\s+([đd]?[aã]?)?\s*cung\s*c[aấ]p\b",
            r"\bchain[- ]of[- ]thought\b",
            r"\bstep-by-step\b",
        ]
        if any(re.search(pattern, lowered) for pattern in patterns):
            return True

        # Heuristic: analysis responses usually have many numbered sections.
        numbered_sections = len(re.findall(r"(?m)^\s*\d+\.\s", text))
        return numbered_sections >= 3

    @staticmethod
    def _looks_truncated_output(text: str, finish_reason: str) -> bool:
        if not text:
            return False

        if finish_reason == "length":
            return True

        tail = text.rstrip()
        if tail.endswith("**") or tail.endswith("*") or tail.endswith("("):
            return True

        return not tail.endswith((".", "!", "?", '"', "'", "..."))

    def _continue_truncated_answer(
        self,
        messages: List[dict],
        partial_answer: str,
        max_tokens: int,
    ) -> str:
        continue_messages = [
            *messages,
            {"role": "assistant", "content": partial_answer},
            {
                "role": "user",
                "content": (
                    "Continue exactly from where you stopped. "
                    "Do not repeat previous content. "
                    "Output only the remaining continuation text."
                ),
            },
        ]

        continue_kwargs = {
            "model": self.model,
            "messages": continue_messages,
            "temperature": min(self.temperature, 0.2),
            "max_tokens": max(120, min(400, max_tokens)),
        }
        if self.reasoning_enabled:
            continue_kwargs["extra_body"] = {"reasoning": {"enabled": False}}

        try:
            continue_response = self._client.chat.completions.create(**continue_kwargs)
            continue_choice = (
                continue_response.choices[0] if continue_response.choices else None
            )
            continuation = (
                continue_choice.message.content.strip()
                if continue_choice
                and continue_choice.message
                and continue_choice.message.content
                else ""
            )
            if not continuation:
                return partial_answer

            return self._merge_continuation(partial_answer, continuation)
        except Exception:
            logger.exception("Failed to continue truncated answer")
            return partial_answer

    @staticmethod
    def _merge_continuation(partial: str, continuation: str) -> str:
        base = partial.rstrip()
        extra = continuation.lstrip()

        # Drop duplicated overlap if continuation restates recent tail.
        tail = base[-80:]
        if tail and extra.startswith(tail):
            extra = extra[len(tail) :].lstrip()

        return f"{base}{extra}"
