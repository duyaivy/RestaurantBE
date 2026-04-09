from django.contrib import admin

from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "guest", "session_key", "status", "last_message_at")
    list_filter = ("status", "created_at")
    search_fields = ("id", "session_key")
    readonly_fields = ("created_at", "updated_at", "last_message_at")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "role", "status", "sequence", "created_at")
    list_filter = ("role", "status", "created_at")
    search_fields = ("conversation__id", "content")
    readonly_fields = ("id", "created_at", "updated_at")
