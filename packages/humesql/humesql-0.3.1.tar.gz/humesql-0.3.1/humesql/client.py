"""
Public client API for HumeSQL.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import time

from .db import get_schema, execute_sql
from .ai import generate_sql_with_gemini
from .utils import load_json_safely, HumanSQLException


@dataclass
class HumeSQLConfig:
    db_config: Dict[str, Any]
    model: str = "gemini-2.5-flash"
    api_key: Optional[str] = None
    cache_schema: bool = True


class HumeSQL:
    """
    Main entrypoint.

    Example:
        from humesql import HumeSQL

        db = {
            "host": "localhost",
            "user": "root",
            "password": "pass",
            "database": "shop",
            "port": 3306,
        }

        h = HumeSQL(db)
        res = h.query("show me the last 10 customers from Nepal")
        print(res["sql"])
        print(res["rows"])
    """

    def __init__(
        self,
        db_config: Dict[str, Any],
        model: str = "gemini-2.5-flash",
        api_key: Optional[str] = None,
        cache_schema: bool = True,
    ) -> None:
        self.config = HumeSQLConfig(
            db_config=db_config,
            model=model,
            api_key=api_key,
            cache_schema=cache_schema,
        )
        self._schema_cache: Optional[Dict[str, Any]] = None

    # -----------------------
    # Internal helpers
    # -----------------------

    def _get_schema(self) -> Dict[str, Any]:
        if self.config.cache_schema and self._schema_cache is not None:
            return self._schema_cache

        schema = get_schema(self.config.db_config)

        if self.config.cache_schema:
            self._schema_cache = schema

        return schema

    # -----------------------
    # Public API
    # -----------------------

    def refresh_schema_cache(self) -> None:
        """Force reload of schema cache from DB."""
        self._schema_cache = get_schema(self.config.db_config)

    def query(
        self,
        user_text: str,
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Main function:
          1. Read schema
          2. Ask AI for SQL
          3. Execute SQL
          4. Return JSON result

        Returns:
            {
              "ok": bool,
              "error": str | None,
              "sql": str | None,
              "limit_applied": bool | None,
              "reasoning": str | None,
              "rows": list[dict] | None,
              "time_ms": float,
              "raw_ai_response": str (if debug=True),
            }
        """
        start_total = time.time()
        ai_raw: Optional[str] = None

        try:
            schema = self._get_schema()

            ai_raw = generate_sql_with_gemini(
                nl_query=user_text,
                schema=schema,
                model=self.config.model,
                api_key=self.config.api_key,
            )

            ai_json = load_json_safely(ai_raw)

            if not isinstance(ai_json, dict):
                raise HumanSQLException(
                    "AI response must be a JSON object with 'sql', "
                    "'reasoning', and 'limit_applied' fields."
                )

            sql = ai_json.get("sql")
            reasoning = ai_json.get("reasoning")
            limit_applied = ai_json.get("limit_applied")

            if not sql or not isinstance(sql, str):
                raise HumanSQLException(
                    "AI did not return a valid 'sql' string in JSON."
                )

            # Basic guardrail against obviously destructive statements.
            lowered = sql.lower()
            forbidden = (" drop ", " truncate ", " alter ", ";", " information_schema ")
            if any(f in lowered for f in forbidden):
                raise HumanSQLException(
                    f"Generated SQL looks unsafe and was blocked:\n{sql}"
                )

            # Execute SQL safely
            rows = execute_sql(self.config.db_config, sql, fetch=True)

            total_ms = round((time.time() - start_total) * 1000.0, 2)

            result: Dict[str, Any] = {
                "ok": True,
                "error": None,
                "sql": sql,
                "limit_applied": bool(limit_applied)
                if isinstance(limit_applied, bool)
                else None,
                "reasoning": reasoning,
                "rows": rows,
                "time_ms": total_ms,
            }

            if debug:
                result["raw_ai_response"] = ai_raw

            return result

        except HumanSQLException as e:
            total_ms = round((time.time() - start_total) * 1000.0, 2)
            result: Dict[str, Any] = {
                "ok": False,
                "error": str(e),
                "sql": None,
                "limit_applied": None,
                "reasoning": None,
                "rows": None,
                "time_ms": total_ms,
            }
            if debug:
                result["raw_ai_response"] = ai_raw
            return result
        except Exception as e:  # noqa: BLE001
            total_ms = round((time.time() - start_total) * 1000.0, 2)
            result: Dict[str, Any] = {
                "ok": False,
                "error": f"Unexpected error: {e}",
                "sql": None,
                "limit_applied": None,
                "reasoning": None,
                "rows": None,
                "time_ms": total_ms,
            }
            if debug:
                result["raw_ai_response"] = ai_raw
            return result
