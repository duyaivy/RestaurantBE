import uuid

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ConversationStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    CLOSED = "CLOSED", "Closed"
    ARCHIVED = "ARCHIVED", "Archived"


class MessageRole(models.TextChoices):
    USER = "USER", "User"
    ASSISTANT = "ASSISTANT", "Assistant"


class MessageStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SUCCESS = "SUCCESS", "Success"
    ERROR = "ERROR", "Error"


class Conversation(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)

    account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.CASCADE,
        related_name="chat_conversations",
        null=True,
        blank=True,
    )

    guest = models.ForeignKey(
        "guests.Guest",
        on_delete=models.CASCADE,
        related_name="chat_conversations",
        null=True,
        blank=True,
    )

    # Trường hợp khách chưa login nhưng vẫn chat
    session_key = models.CharField(max_length=100, null=True, blank=True, db_index=True)

    title = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=ConversationStatus.choices,
        default=ConversationStatus.ACTIVE,
        db_index=True,
    )

    last_message_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "chatbot_conversations"
        ordering = ["-last_message_at", "-created_at"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(account__isnull=False)
                | models.Q(guest__isnull=False)
                | models.Q(session_key__isnull=False),
                name="conversation_has_owner",
            )
        ]
        indexes = [
            models.Index(fields=["account", "created_at"]),
            models.Index(fields=["guest", "created_at"]),
            models.Index(fields=["session_key", "created_at"]),
            models.Index(fields=["status", "last_message_at"]),
        ]

    def __str__(self):
        return f"Conversation {self.id}"


class Message(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    role = models.CharField(
        max_length=20,
        choices=MessageRole.choices,
        db_index=True,
    )

    content = models.TextField()

    sequence = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=MessageStatus.choices,
        default=MessageStatus.SUCCESS,
        db_index=True,
    )

    error_message = models.TextField(blank=True, default="")

    class Meta:
        db_table = "chatbot_messages"
        ordering = ["sequence", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["conversation", "sequence"],
                name="unique_message_sequence_per_conversation",
            )
        ]
        indexes = [
            models.Index(fields=["conversation", "sequence"]),
            models.Index(fields=["conversation", "created_at"]),
            models.Index(fields=["role", "created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.sequence:
            last_message = (
                Message.objects.filter(conversation=self.conversation)
                .order_by("-sequence")
                .first()
            )
            self.sequence = 1 if not last_message else last_message.sequence + 1

        super().save(*args, **kwargs)

        Conversation.objects.filter(pk=self.conversation_id).update(
            last_message_at=timezone.now()
        )

    def __str__(self):
        return f"{self.role} - {self.conversation_id} - #{self.sequence}"
