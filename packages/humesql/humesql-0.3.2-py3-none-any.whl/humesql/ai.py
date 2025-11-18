"""
AI backend for HumeSQL.

Currently implemented for Google Gemini via `google-genai` library.
"""

from typing import Any, Dict, Optional
import os
import json

from .utils import HumanSQLException


try:
    # pip install google-genai
    from google import genai
except ImportError:  # pragma: no cover
    genai = None


def _get_api_key(explicit_key: Optional[str] = None) -> str:
    """
    Resolve the API key with fallbacks.

    Priority:
      1. explicit_key argument
      2. HUMESQL_AI_KEY (new)
      3. HUMANSQL_AI_KEY (legacy)
      4. GEMINI_API_KEY
    """
    if explicit_key:
        return explicit_key

    env_key = (
        os.getenv("HUMESQL_AI_KEY")
        or os.getenv("HUMANSQL_AI_KEY")  # legacy
        or os.getenv("GEMINI_API_KEY")
    )
    if not env_key:
        raise HumanSQLException(
            "No API key found. Set HUMESQL_AI_KEY (preferred), HUMANSQL_AI_KEY, "
            "or GEMINI_API_KEY, or pass api_key= to HumeSQL()."
        )
    return env_key


def build_prompt(nl_query: str, schema: Dict[str, Any]) -> str:
    """
    Build the system/user prompt sent to the model.
    Model must answer with JSON only.
    """
    schema_json = json.dumps(schema, indent=2)

    prompt = f"""
You are HumeSQL — an AI system that converts natural language queries into safe SQL.

You MUST follow these rules:

1. ALWAYS return a JSON object. Do not include explanations outside JSON.
2. JSON must follow this format exactly:

{{
  "sql": "SQL query here",
  "reasoning": "short explanation of how you understood the user query",
  "limit_applied": true or false
}}

3. When the SELECT has no LIMIT, automatically add a safe default LIMIT of 100.
4. NEVER generate dangerous SQL:
   - no DROP
   - no TRUNCATE
   - no ALTER
   - no DELETE (unless user clearly requests deletion)
   - no UPDATE without clear WHERE conditions
   - no multi-statement queries
   - no system tables or metadata tables beyond those provided in schema.

5. The database schema is provided below. Use ONLY the tables and columns that exist in the schema.

SCHEMA:
{schema_json}

6. Convert this natural language query into SQL:
"{nl_query}"

Remember: Always return JSON only, with valid SQL, no markdown formatting.
"""
    return prompt.strip()


def generate_sql_with_gemini(
    nl_query: str,
    schema: Dict[str, Any],
    model: str = "gemini-2.5-flash",
    api_key: Optional[str] = None,
) -> str:
    """
    Call Gemini model and return its raw text output.
    """
    if genai is None:
        raise HumanSQLException(
            "google-genai is not installed. Run: pip install google-genai"
        )

    key = _get_api_key(api_key)
    client = genai.Client(api_key=key)

    prompt = build_prompt(nl_query, schema)

    try:
        resp = client.models.generate_content(
            model=model,
            contents=prompt,
        )
    except Exception as e:  # noqa: BLE001
        raise HumanSQLException(f"Error calling Gemini: {e}") from e

    # The library exposes .text in most simple cases
    text = getattr(resp, "text", None)
    if not text:
        # Fallback – try to join candidates if needed
        try:
            text = "\n".join(
                c.content.parts[0].text
                for c in resp.candidates
                if c.content.parts and hasattr(c.content.parts[0], "text")
            )
        except Exception:
            raise HumanSQLException("Gemini returned an unexpected format.") from None

    return text
