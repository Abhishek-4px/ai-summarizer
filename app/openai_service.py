import os
import json
import traceback

from google import genai
from google.genai import types

from app.schemas import SummaryResponse

# Lazy client init — HF Spaces injects secrets at container runtime
_client = None

MODEL_ID = "gemini-2.5-flash-lite"

SYSTEM_PROMPT = (
    "You are a summarization assistant. Summarize the given text concisely "
    "in 2-3 sentences. Extract 3-5 key points as a list. Return only valid "
    "JSON matching the provided schema."
)

SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "key_points": {
            "type": "array",
            "items": {"type": "string"},
        },
        "word_count": {"type": "integer"},
    },
    "required": ["summary", "key_points", "word_count"],
}


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it as a Secret in your "
                "Hugging Face Space settings."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def summarize_text(text: str) -> SummaryResponse:
    """Call Gemini with structured JSON output and return a SummaryResponse."""
    word_count = len(text.split())

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=f"Text to summarize:\n{text}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=SUMMARY_SCHEMA,
                temperature=0.2,
            ),
        )

        data = json.loads(response.text)
        # Override word_count with the actual count from input text
        data["word_count"] = word_count

        return SummaryResponse(**data)

    except Exception as e:
        # Log the full traceback for debugging
        traceback.print_exc()
        # Re-raise with the actual error message so routes.py can surface it
        raise RuntimeError(str(e)) from e
