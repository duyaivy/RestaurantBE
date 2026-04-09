from __future__ import annotations

from rest_framework import serializers


class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=4000)
    conversation_id = serializers.IntegerField(required=False, min_value=1)


class CitationSerializer(serializers.Serializer):
    source = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField(required=False, allow_blank=True)
    distance = serializers.FloatField(required=False, allow_null=True)


class ChatResponseSerializer(serializers.Serializer):
    conversation_id = serializers.IntegerField()
    answer = serializers.CharField()
    citations = CitationSerializer(many=True)


class ConversationListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    status = serializers.CharField()
    last_message_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()


class MessageSerializer(serializers.Serializer):
    id = serializers.CharField()
    role = serializers.CharField()
    content = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
