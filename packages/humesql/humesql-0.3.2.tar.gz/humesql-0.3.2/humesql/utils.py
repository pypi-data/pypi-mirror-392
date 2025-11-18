import json
import re
from typing import Any


class HumanSQLException(Exception):
    """Base exception for HumeSQL errors (keeps legacy name for compatibility)."""
    pass


def sanitize_json_text(text: str) -> str:
    """
    Try to clean model output and extract a JSON blob.
    Handles cases like:
    - Markdown code fences ```json ... ```
    - Extra commentary before/after JSON
    """
    if text is None:
        raise HumanSQLException("Empty response from AI backend.")

    text = text.strip()

    # Remove markdown fences if present
    fence_pattern = r"```(?:json)?(.*?)```"
    m = re.search(fence_pattern, text, flags=re.DOTALL | re.IGNORECASE)
    if m:
        text = m.group(1).strip()

    # Try to extract substring from first '{' to last '}'
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1].strip()

    return text


def load_json_safely(text: str) -> Any:
    """Sanitize then parse JSON, raising a HumanSQLException on error."""
    cleaned = sanitize_json_text(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        snippet = cleaned[:500]
        raise HumanSQLException(
            f"Failed to parse AI JSON response: {e}\nSnippet: {snippet}"
        ) from e
