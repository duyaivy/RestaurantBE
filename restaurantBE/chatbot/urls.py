"""
URL patterns cho chatbot app.

Include vào config/urls.py:
    path("api/chatbot/", include("chatbot.urls")),
"""

from django.urls import path

from .views import ChatView, ConversationDetailView, ConversationListView

app_name = "chatbot"

urlpatterns = [
    # Gửi tin nhắn / nhận trả lời
    path("chat/", ChatView.as_view(), name="chat"),
    # Danh sách conversations
    path("conversations/", ConversationListView.as_view(), name="conversation-list"),
    # Lịch sử messages của 1 conversation
    path(
        "conversations/<int:pk>/messages/",
        ConversationDetailView.as_view(),
        name="conversation-messages",
    ),
    # Archive / xoá conversation
    path(
        "conversations/<int:pk>/",
        ConversationDetailView.as_view(),
        name="conversation-detail",
    ),
]
