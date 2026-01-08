"""AI utils for aibot app."""

import os
from groq import Groq

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
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )

        return response.choices[0].message.content

    except Exception as e:  # pylint: disable=broad-exception-caught
        print("❌ GROQ ERROR:", e)
        return "⚠️ AI failed to respond."
