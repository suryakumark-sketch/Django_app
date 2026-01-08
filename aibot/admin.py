""" Admin for aibot app."""

from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin for chatmessage model."""
    list_display = ("role", "message", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("message",)
