""" Views for Aibot app."""

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required

# pylint: disable=no-member

from .models import Chat, ChatMessage, Document
from .groq_ai import get_ai_reply
from .utils import extract_text


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
    """ Home Views."""
    return render(request, "aibot/chat.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def custom_login(request):
    """Custom login view that redirects authenticated users."""
    # If user is already logged in, redirect to chatbot
    if request.user.is_authenticated:
        return redirect("/chat-ui/")
    
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect("/chat-ui/")
    else:
        form = AuthenticationForm()

    return render(request, "registration/login.html", {"form": form})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def custom_logout(request):
    """Custom logout view."""
    auth_logout(request)  # clears session + auth data
    return redirect("/accounts/login/")


# pylint: disable=too-many-locals
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def signup(request):
    """Render signup page and handle registration."""
    # If user is already logged in, redirect to chatbot
    if request.user.is_authenticated:
        return redirect("/chat-ui/")
    
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to login page after successful signup
            return redirect("/accounts/login/")
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})


# pylint: disable=too-many-locals
@login_required
@csrf_exempt
def chat_api(request):
    """ Chat API (per-user, per-chat)."""
    if request.method != "POST":
        return JsonResponse({"reply": "Invalid request"}, status=200)

    # ---------------------------
    # Parse JSON safely
    # ---------------------------
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print("JSON ERROR:", e)
        return JsonResponse({"reply": "Invalid data"}, status=200)

    message = str(data.get("message", "")).strip()
    chat_id = data.get("chat_id")

    if not message:
        return JsonResponse({"reply": "Empty message"}, status=200)

    # Always use the authenticated user for privacy
    user = request.user

    try:
        # ---------------------------
        # Get or create chat (scoped to current user)
        # ---------------------------
        chat = (
            Chat.objects.filter(id=chat_id, user=user).first()
            if chat_id
            else None
        )
        if not chat:
            chat = Chat.objects.create(user=user, title=message[:50])

        # ---------------------------
        # Save user message
        # ---------------------------
        ChatMessage.objects.create(chat=chat, role="user", message=message)

        # ---------------------------
        # Conversation history
        # ---------------------------
        history = []
        for m in chat.messages.order_by("created_at"):
            role = "User" if m.role == "user" else "Assistant"
            history.append(f"{role}: {m.message}")

        conversation_text = "\n".join(history)

        # ==================================================
        # ✅ USE ONLY LATEST DOCUMENT (IMPORTANT)
        # ==================================================
        # ==================================================
        # ✅ USE ALL DOCUMENTS (MULTI-DOC RAG)
        # ==================================================
        documents = chat.documents.order_by("-created_at")  # Newest first
        document_text = ""
        
        # Max characters for context (approx 20k chars ~ 5k tokens)
        MAX_CONTEXT_CHARS = 20000 
        current_chars = 0

        for doc in documents:
            if doc.content and doc.content.strip():
                # Format: [DOCUMENT: filename.pdf] \n content...
                content_chunk = f"\n[DOCUMENT: {doc.filename}]\n{doc.content.strip()}\n"
                
                # Check if adding this document exceeds limit
                if current_chars + len(content_chunk) > MAX_CONTEXT_CHARS:
                    # Truncate if necessary (optional: or just skip older ones)
                    remaining_space = MAX_CONTEXT_CHARS - current_chars
                    if remaining_space > 100:  # Only add if meaningful space remains
                        document_text += content_chunk[:remaining_space] + "\n...[TRUNCATED]..."
                    break
                
                document_text += content_chunk
                current_chars += len(content_chunk)

        # ==================================================
        # 🔍 SMART DETECTION: DOC vs NORMAL CHAT
        # ==================================================
        doc_keywords = [
            "document", "doc", "pdf", "file",
            "explain", "summary", "content",
            "this document", "this doc", "page", "section"
        ]

        is_doc_question = any(k in message.lower() for k in doc_keywords)

        # ==================================================
        # ✅ FINAL PROMPT (SAFE + SMART)
        # ==================================================
        if is_doc_question and document_text:
            prompt = (
                "You are a helpful assistant.\n"
                "Answer the user's question using ONLY the document below.\n"
                "Provide a detailed, comprehensive explanation with all relevant information from the document.\n"
                "Write your answer in plain text format without using markdown symbols, formatting characters, or special symbols like ##, **, <br>, |, {, }, or \\.\n"
                "Write naturally and clearly like ChatGPT, using only regular text.\n"
                "If the answer is not present in the document, say so clearly.\n\n"
                f"{document_text}\n\n"
                f"User question:\n{message}\n\n"
                "Provide a detailed and comprehensive answer in plain text:"
            )
        else:
            prompt = (
                "You are a friendly helpful assistant.\n"
                "Write your response in plain text format without using markdown symbols, formatting characters, or special symbols.\n"
                "Write naturally and clearly like ChatGPT.\n"
                f"Conversation so far:\n{conversation_text}\n\n"
                f"User: {message}\n"
                "Assistant:"
            )

        # ==================================================
        # AI CALL + FINAL FAILSAFE
        # ==================================================
        try:
            reply = get_ai_reply(prompt)

            if not reply or not reply.strip():
                reply = "I couldn’t find relevant information. Please ask in a different way."

        except Exception as e:  # pylint: disable=broad-exception-caught
            print("AI ERROR:", e)
            reply = "AI service temporarily unavailable. Please try again."

        # ---------------------------
        # Save AI reply
        # ---------------------------
        ChatMessage.objects.create(chat=chat, role="ai", message=reply)

        return JsonResponse({"reply": reply, "chat_id": chat.id})

    except Exception as e:  # pylint: disable=broad-exception-caught
        # 🚨 ABSOLUTE FAILSAFE (NO SERVER ERROR)
        print("FATAL ERROR:", e)
        return JsonResponse(
            {"reply": "Internal error occurred. Please try again."},
            status=200
        )


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def chats_api(request):
    """ Chats API (per-user, no caching)."""
    # Only return chats for the logged-in user
    chats = Chat.objects.filter(user=request.user).order_by("-id")
    return JsonResponse({
        "chats": [{"id": c.id, "title": c.title} for c in chats]
    })


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def chat_messages_api(request, chat_id):
    """ Chat Messages API (per-user)."""
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    return JsonResponse({
        "messages": [
            {"role": m.role, "message": m.message}
            for m in chat.messages.all()
        ]
    })


@login_required
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_chat(request, chat_id):
    """ Delete Chat (per-user)."""
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    chat.delete()
    return JsonResponse({"success": True})


@login_required
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def upload_document(request):
    """ Upload Document (per-user)."""
    if request.method != "POST":
        return JsonResponse({"reply": "POST only"}, status=400)

    file = request.FILES.get("document")
    chat_id = request.POST.get("chat_id")

    if not file or not chat_id:
        return JsonResponse({"reply": "Missing file or chat"})

    chat = get_object_or_404(Chat, id=chat_id, user=request.user)

    extracted_text = extract_text(file)

    # ✅ SAFETY CHECK
    if not extracted_text or not extracted_text.strip():
        extracted_text = ""

    # ✅ SAVE DOCUMENT
    Document.objects.create(
        chat=chat,
        filename=file.name,
        content=extracted_text
    )

    ChatMessage.objects.create(
        chat=chat,
        role="user",
        message=f"Uploaded document: {file.name}"
    )

    return JsonResponse({
        "reply": f"📄 {file.name} uploaded and processed successfully."
    })
