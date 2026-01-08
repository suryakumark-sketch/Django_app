""" Models for Aibot app."""

from django.db import models
from django.contrib.auth.models import User


class Chat(models.Model):
    """ Chat model."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)
    document_text = models.TextField(blank=True, null=True)  # ✅ STORE DOC CONTENT
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title)


class ChatMessage(models.Model):
    """ Chatmessage model."""
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10)  # user / ai
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        message_text = str(self.message)
        return f"{self.role}: {message_text[:30]}"

class Document(models.Model):
    """ Document model."""
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="documents")
    filename = models.CharField(max_length=255)
    content = models.TextField()   # ✅ extracted text
    created_at = models.DateTimeField(auto_now_add=True)
