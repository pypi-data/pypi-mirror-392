"""
Command-line interface for HumeSQL.

Allows running a natural-language query against a MySQL/MariaDB database.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from .client import HumeSQL


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a natural-language query against a MySQL/MariaDB database using HumeSQL."
    )
    parser.add_argument("query", help="Natural language query (e.g. 'last 5 users from Nepal').")
    parser.add_argument("-H", "--host", required=True, help="Database host")
    parser.add_argument("-u", "--user", required=True, help="Database user")
    parser.add_argument("-p", "--password", default="", help="Database password")
    parser.add_argument("-d", "--database", required=True, help="Database name")
    parser.add_argument("--port", type=int, default=3306, help="Database port (default: 3306)")
    parser.add_argument("--api-key", default=None, help="Gemini API key (fallbacks: HUMESQL_AI_KEY, HUMANSQL_AI_KEY, or GEMINI_API_KEY)")
    parser.add_argument("--model", default="gemini-2.5-flash", help="Gemini model to use")
    parser.add_argument("--no-cache-schema", action="store_true", help="Disable schema caching")
    parser.add_argument("--debug", action="store_true", help="Include raw AI response in output")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    db_config: Dict[str, Any] = {
        "host": args.host,
        "user": args.user,
        "password": args.password,
        "database": args.database,
        "port": args.port,
    }

    h = HumeSQL(
        db_config=db_config,
        model=args.model,
        api_key=args.api_key,
        cache_schema=not args.no_cache_schema,
    )

    result = h.query(args.query, debug=args.debug)
    print(json.dumps(result, default=str, indent=2))

    return 0 if result.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
