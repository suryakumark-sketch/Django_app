""" Admin for aibot app."""

from django.contrib import admin
from .models import ChatMessage, Chat, Document

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin for chatmessage model."""
    list_display = ("role", "message", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("message",)


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    """Admin for chat model."""
    list_display = ("title", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "user__username")

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin for document model."""
    list_display = ("filename", "chat", "created_at")
    list_filter = ("created_at",)
    search_fields = ("filename", "content")