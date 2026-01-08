""" URLS for Aibot app."""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.signup, name="signup"),
    path("accounts/login/", views.custom_login, name="login"),
    path("accounts/logout/", views.custom_logout, name="logout"),
    path("chat-ui/", views.home, name="home"),
    path("chat/", views.chat_api, name="chat_api"),
    path("chats/", views.chats_api, name="chats_api"),
    path("chat/<int:chat_id>/messages/", views.chat_messages_api),
    path("chat/<int:chat_id>/delete/", views.delete_chat),
    path("upload/", views.upload_document),
]
