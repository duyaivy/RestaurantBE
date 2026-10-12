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
from typing import Optional

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Conversation,
    ConversationStatus,
    MessageRole,
    MessageStatus,
)
from .serializers import (
    ChatMessageSerializer,
)
from .services import ConversationService

logger = logging.getLogger(__name__)


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
        conversation = ConversationService.get_or_create_conversation(request, conversation_id)

        # 3. Lưu message user
        ConversationService.save_message(
            conversation=conversation,
            role=MessageRole.USER,
            content=user_message,
        )

        # 4. Lấy lịch sử để đưa vào LLM
        history = ConversationService.build_history(conversation, limit=12)
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
            ConversationService.save_message(
                conversation=conversation,
                role=MessageRole.ASSISTANT,
                content=answer,
                status=MessageStatus.SUCCESS,
            )

        except Exception as exc:
            logger.exception("[ChatView] Lỗi khi xử lý chat: %s", exc)
            error_text = "Xin lỗi, hệ thống đang gặp sự cố. Vui lòng thử lại sau."
            ConversationService.save_message(
                conversation=conversation,
                role=MessageRole.ASSISTANT,
                content=error_text,
                status=MessageStatus.ERROR,
                error=str(exc),
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
        account, guest, session_key = ConversationService.resolve_owner(request)

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
        account, guest, session_key = ConversationService.resolve_owner(request)
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
