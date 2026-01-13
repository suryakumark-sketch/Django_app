"""AI utils for aibot app."""

import os
import re
from groq import Groq


def clean_markdown(text):
    """Remove markdown formatting symbols from text."""
    if not text:
        return text
    
    # Remove markdown headers (##, ###, etc.)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove bold/italic markers (**text**, *text*, __text__, _text_)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    # Remove code blocks (```code```)
    text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
    
    # Remove inline code (`code`)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove HTML tags like <br>
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove markdown links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove markdown list markers (-, *, +)
    text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
    
    # Remove markdown table separators (|)
    text = re.sub(r'\|', ' ', text)
    
    # Remove markdown horizontal rules (---, ***)
    text = re.sub(r'^[-*]{3,}$', '', text, flags=re.MULTILINE)
    
    # Remove curly braces and backslashes
    text = text.replace('{', '').replace('}', '')
    text = text.replace('\\', '')
    
    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    return text


def get_ai_reply(prompt):
    """Get AI reply for a given prompt."""
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "⚠️ GROQ API key not set."

        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Always respond in plain text format without using markdown formatting, symbols, or special characters. Write naturally like ChatGPT."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000
        )

        reply = response.choices[0].message.content
        
        # Clean markdown symbols from the response
        reply = clean_markdown(reply)
        
        return reply

    except Exception as e:  # pylint: disable=broad-exception-caught
        print("❌ GROQ ERROR:", e)
        return "⚠️ AI failed to respond."
