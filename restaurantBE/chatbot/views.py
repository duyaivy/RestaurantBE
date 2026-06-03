"""
Chatbot Views
-------------
Endpoints:
  POST /api/chatbot/chat/
      → Gửi tin nhắn, nhận trả lời từ AI.
      → Tự tạo conversation mới nếu không có conversation_id.
      → Lưu message vào DB.

  GET  /api/chatbot/conversations/
      → Danh sách conversation của user (hoặc session).

  GET  /api/chatbot/conversations/<id>/messages/
      → Lịch sử tin nhắn của 1 conversation.

  DELETE /api/chatbot/conversations/<id>/
      → Đóng (archive) 1 conversation.

Auth:
  - Nếu user đã login: dùng request.user để gắn conversation.
  - Nếu chưa login: dùng session_key (guest user).
"""

from __future__ import annotations

import logging
import re
from typing import List, Optional, Tuple

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from restaurantBE.accounts.models import Account
from restaurantBE.guests.models import Guest

from .models import (
    Conversation,
    ConversationStatus,
    Message,
    MessageRole,
    MessageStatus,
)
from .serializers import (
    ChatMessageSerializer,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_or_create_conversation(
    request: Request,
    conversation_id: Optional[int],
) -> Conversation:
    """
    Lấy conversation hiện tại hoặc tạo mới.
    Hỗ trợ cả user đã login lẫn guest (session).
    """
    account, guest, session_key = _resolve_conversation_owner(request)

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


def _resolve_conversation_owner(
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


def _build_history(conversation: Conversation, limit: int = 12) -> List[dict]:
    """
    Lấy lịch sử chat gần nhất để đưa vào LLM context.
    Giới hạn 12 message (6 lượt) để tiết kiệm token.
    """
    messages = conversation.messages.filter(status=MessageStatus.SUCCESS).order_by(
        "-sequence"
    )[:limit]
    history = []
    for msg in reversed(list(messages)):
        if msg.role == MessageRole.ASSISTANT and _looks_like_reasoning_leak(
            msg.content
        ):
            continue
        role = "user" if msg.role == MessageRole.USER else "assistant"
        history.append({"role": role, "content": msg.content})
    return history


def _looks_like_reasoning_leak(content: str) -> bool:
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


def _save_message(
    conversation: Conversation,
    role: str,
    content: str,
    message_status: str = MessageStatus.SUCCESS,
    error_message: str = "",
) -> Message:
    return Message.objects.create(
        conversation=conversation,
        role=role,
        content=content,
        status=message_status,
        error_message=error_message,
    )


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------


class ChatView(APIView):
    """
    POST /api/chatbot/chat/

    Body:
      {
        "message": "Có món chay không?",
        "conversation_id": 42   // optional
      }

    Response:
      {
        "conversation_id": 42,
        "answer": "Dạ có ạ...",
        "citations": [...]
      }
    """

    permission_classes = [AllowAny]

    # Lazy init — chỉ khởi tạo 1 lần, tái sử dụng
    _chat_service = None

    @classmethod
    def _get_chat_service(cls):
        if cls._chat_service is None:
            from .rag.chat import ChatService

            cls._chat_service = ChatService()
        return cls._chat_service

    def post(self, request: Request) -> Response:
        # 1. Validate input
        serializer = ChatMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated = serializer.validated_data
        user_message: str = validated["message"]
        conversation_id: Optional[int] = validated.get("conversation_id")

        # 2. Lấy / tạo conversation
        conversation = _get_or_create_conversation(request, conversation_id)

        # 3. Lưu message user
        _save_message(
            conversation=conversation,
            role=MessageRole.USER,
            content=user_message,
        )

        # 4. Lấy lịch sử để đưa vào LLM
        history = _build_history(conversation, limit=12)
        # Bỏ message vừa lưu ra khỏi history (chưa có reply)
        history = [
            h
            for h in history
            if not (h["role"] == "user" and h["content"] == user_message)
        ]

        # 5. Gọi RAG + LLM
        lang = request.data.get("lang") or request.query_params.get("lang") or request.headers.get("language") or "vi"
        lang = str(lang).strip().lower()
        if lang not in ["en", "vi"]:
            lang = "vi"

        try:
            chat_service = self._get_chat_service()
            result = chat_service.reply(
                user_message=user_message,
                history=history,
                lang=lang,
            )
            answer: str = result["answer"]
            citations: list = result.get("citations", [])
            items: list = result.get("items", [])

            # 6. Lưu message bot
            _save_message(
                conversation=conversation,
                role=MessageRole.ASSISTANT,
                content=answer,
                message_status=MessageStatus.SUCCESS,
            )

        except Exception as exc:
            logger.exception("[ChatView] Lỗi khi xử lý chat: %s", exc)
            error_text = "Xin lỗi, hệ thống đang gặp sự cố. Vui lòng thử lại sau."
            _save_message(
                conversation=conversation,
                role=MessageRole.ASSISTANT,
                content=error_text,
                message_status=MessageStatus.ERROR,
                error_message=str(exc),
            )
            return Response(
                {
                    "conversation_id": conversation.id,
                    "answer": error_text,
                    "citations": [],
                    "items": [],
                },
                status=status.HTTP_200_OK,  # vẫn 200 để frontend hiển thị được
            )

        return Response(
            {
                "conversation_id": conversation.id,
                "answer": answer,
                "citations": citations,
                "items": items,
            },
            status=status.HTTP_200_OK,
        )


class ConversationListView(APIView):
    """
    GET /api/chatbot/conversations/
    Trả về danh sách conversation của user/session hiện tại.
    """

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        account, guest, session_key = _resolve_conversation_owner(request)

        if account:
            qs = Conversation.objects.filter(
                account=account,
                status=ConversationStatus.ACTIVE,
            )
        elif guest:
            qs = Conversation.objects.filter(
                guest=guest,
                status=ConversationStatus.ACTIVE,
            )
        else:
            if not session_key:
                return Response({"conversations": []})
            qs = Conversation.objects.filter(
                session_key=session_key,
                status=ConversationStatus.ACTIVE,
            )

        conversations = qs.order_by("-last_message_at")[:20]
        data = [
            {
                "id": c.id,
                "title": c.title or f"Cuộc trò chuyện #{c.id}",
                "status": c.status,
                "last_message_at": c.last_message_at,
                "created_at": c.created_at,
            }
            for c in conversations
        ]
        return Response({"conversations": data})


class ConversationDetailView(APIView):
    """
    GET    /api/chatbot/conversations/<id>/messages/  → lấy lịch sử
    DELETE /api/chatbot/conversations/<id>/           → archive conversation
    """

    permission_classes = [AllowAny]

    def _get_conversation(self, request: Request, pk: int) -> Optional[Conversation]:
        account, guest, session_key = _resolve_conversation_owner(request)
        qs = Conversation.objects.filter(pk=pk)
        if account:
            qs = qs.filter(account=account)
        elif guest:
            qs = qs.filter(guest=guest)
        else:
            if not session_key:
                return None
            qs = qs.filter(session_key=session_key)
        return qs.first()

    def get(self, request: Request, pk: int) -> Response:
        conversation = self._get_conversation(request, pk)
        if not conversation:
            return Response(
                {"error": "Không tìm thấy cuộc trò chuyện."},
                status=status.HTTP_404_NOT_FOUND,
            )

        messages = conversation.messages.filter(status=MessageStatus.SUCCESS).order_by(
            "sequence"
        )

        data = [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "status": m.status,
                "created_at": m.created_at,
            }
            for m in messages
        ]
        return Response(
            {
                "conversation_id": conversation.id,
                "messages": data,
            }
        )

    def delete(self, request: Request, pk: int) -> Response:
        conversation = self._get_conversation(request, pk)
        if not conversation:
            return Response(
                {"error": "Không tìm thấy cuộc trò chuyện."},
                status=status.HTTP_404_NOT_FOUND,
            )

        conversation.status = ConversationStatus.ARCHIVED
        conversation.save(update_fields=["status", "updated_at"])
        return Response({"message": "Đã kết thúc cuộc trò chuyện."})
