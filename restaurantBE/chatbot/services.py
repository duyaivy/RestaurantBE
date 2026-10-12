"""
Conversation Service
Single Responsibility: Quản lý vòng đời của Conversation và Message.
View chỉ gọi service, không tự xử lý DB hay business logic.
"""

from __future__ import annotations

import logging
import re
from typing import List, Optional, Tuple

from rest_framework.request import Request

from restaurantBE.accounts.models import Account
from restaurantBE.chatbot.models import (
    Conversation,
    ConversationStatus,
    Message,
    MessageRole,
    MessageStatus,
)
from restaurantBE.guests.models import Guest

logger = logging.getLogger(__name__)


class ConversationService:
    """
    Single Responsibility: quản lý vòng đời của Conversation và Message.
    """

    @staticmethod
    def resolve_owner(
        request: Request,
    ) -> Tuple[Optional[Account], Optional[Guest], Optional[str]]:
        """
        Chuẩn hoá owner của conversation.
        - Account token  -> gắn account
        - Guest token    -> gắn guest
        - Anonymous      -> gắn session_key
        """
        user = getattr(request, "user", None)
        account: Optional[Account] = None
        guest: Optional[Guest] = None
        session_key: Optional[str] = None

        if isinstance(user, Guest):
            guest = user
        elif isinstance(user, Account):
            account = user
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key

        return account, guest, session_key

    @staticmethod
    def get_or_create_conversation(
        request: Request,
        conversation_id: Optional[int] = None,
    ) -> Conversation:
        """
        Lấy conversation hiện tại hoặc tạo mới.
        Hỗ trợ cả user đã login lẫn guest (session).
        """
        account, guest, session_key = ConversationService.resolve_owner(request)

        if conversation_id:
            # Tìm conversation hiện có, thuộc về user/session này
            qs = Conversation.objects.filter(
                id=conversation_id,
                status=ConversationStatus.ACTIVE,
            )
            if account:
                qs = qs.filter(account=account)
            elif guest:
                qs = qs.filter(guest=guest)
            else:
                qs = qs.filter(session_key=session_key)

            conversation = qs.first()
            if conversation:
                return conversation

        # Không truyền conversation_id: ưu tiên resume cuộc trò chuyện gần nhất
        latest_qs = Conversation.objects.filter(status=ConversationStatus.ACTIVE)
        if account:
            latest_qs = latest_qs.filter(account=account)
        elif guest:
            latest_qs = latest_qs.filter(guest=guest)
        else:
            latest_qs = latest_qs.filter(session_key=session_key)

        latest = latest_qs.order_by("-last_message_at", "-created_at").first()
        if latest:
            return latest

        # Tạo mới
        return Conversation.objects.create(
            account=account,
            guest=guest,
            session_key=session_key,
            status=ConversationStatus.ACTIVE,
        )

    @staticmethod
    def _looks_like_reasoning_leak(content: str) -> bool:
        """Private helper — kiểm tra dấu hiệu nội dung suy luận rò rỉ của AI."""
        text = (content or "").strip().lower()
        if not text:
            return False

        patterns = [
            r"\bokay,?\s+t[oô]i\s+c[aầ]n\b",
            r"\bt[oô]i\s+s[eẽ]\s+ki[eể]m\s+tra\b",
            r"\bph[aầ]n\s+th[uứ]\b",
            r"\bqu[eé]t\s+l[aạ]i\b",
        ]
        if any(re.search(pattern, text) for pattern in patterns):
            return True

        return len(re.findall(r"(?m)^\s*\d+\.\s", content)) >= 3

    @staticmethod
    def build_history(conversation: Conversation, limit: int = 12) -> List[dict]:
        """
        Lấy lịch sử chat gần nhất để đưa vào LLM context.
        Giới hạn 12 message (6 lượt) để tiết kiệm token.
        """
        messages = conversation.messages.filter(status=MessageStatus.SUCCESS).order_by(
            "-sequence"
        )[:limit]
        history = []
        for msg in reversed(list(messages)):
            if msg.role == MessageRole.ASSISTANT and ConversationService._looks_like_reasoning_leak(
                msg.content
            ):
                continue
            role = "user" if msg.role == MessageRole.USER else "assistant"
            history.append({"role": role, "content": msg.content})
        return history

    @staticmethod
    def save_message(
        conversation: Conversation,
        role: str,
        content: str,
        status: str = MessageStatus.SUCCESS,
        error: str = "",
        message_status: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Message:
        """Lưu message vào DB."""
        final_status = message_status or status
        final_error = error_message if error_message is not None else error
        return Message.objects.create(
            conversation=conversation,
            role=role,
            content=content,
            status=final_status,
            error_message=final_error,
        )
