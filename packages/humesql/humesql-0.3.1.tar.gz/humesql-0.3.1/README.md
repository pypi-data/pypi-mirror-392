# HumeSQL

HumeSQL turns natural language into safe SQL, runs it against your MySQL/MariaDB database, and returns JSON rows. It introspects your schema, prompts Gemini to craft SQL, applies guardrails, executes, and responds with the SQL, reasoning, and results.

## Features
- Natural language → SQL → JSON rows
- MySQL/MariaDB via `mysql-connector-python`
- Gemini models (default: `gemini-2.5-flash`)
- Built-in guardrails against destructive SQL
- Schema caching for speed
- Python API and `humesql` CLI
- Debug mode to see raw model output

## Requirements
- Python 3.9+
- MySQL/MariaDB reachable from where you run HumeSQL
- Google Gemini API key with access to the chosen model

## Install
From PyPI:
```bash
pip install humesql
```

From source (editable):
```bash
pip install -e .
```

## Configuration
HumeSQL looks for an API key in this order:
1) Explicit `api_key` argument  
2) `HUMESQL_AI_KEY` (preferred)  
3) `HUMANSQL_AI_KEY` (legacy)  
4) `GEMINI_API_KEY`

Set an environment variable, for example:
```bash
export HUMESQL_AI_KEY="your-gemini-key"
```

Database credentials are passed as a dict:
```python
db = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "classicmodels",
    "port": 3306,
}
```

## Quick start (Python)
```python
from humesql import HumeSQL

db = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "classicmodels",
    "port": 3306,
}

h = HumeSQL(db, model="gemini-2.5-flash")
res = h.query("Show me the last 5 users who signed up from Nepal", debug=True)

if res["ok"]:
    print("SQL:", res["sql"])
    print("Reasoning:", res["reasoning"])
    print("Rows:", res["rows"])
else:
    print("Error:", res["error"])
    if res.get("raw_ai_response"):
        print("Raw:", res["raw_ai_response"])
```

Returned structure:
```json
{
  "ok": true,
  "error": null,
  "sql": "SELECT ...",
  "limit_applied": true,
  "reasoning": "short explanation",
  "rows": [ { "col": "value" }, ... ],
  "time_ms": 123.45,
  "raw_ai_response": "model text"  // only when debug=True
}
```

## CLI usage
Run one-off queries from the terminal:
```bash
humesql "last 5 customers from Nepal" \
  -H localhost -u root -p "" -d classicmodels --port 3306 \
  --api-key "$HUMESQL_AI_KEY" --model gemini-2.5-flash --debug
```

CLI arguments:
- `query` (positional): natural language input
- `-H/--host`, `-u/--user`, `-p/--password`, `-d/--database`, `--port`
- `--api-key`: overrides env vars
- `--model`: Gemini model name (default `gemini-2.5-flash`)
- `--no-cache-schema`: disable schema caching
- `--debug`: include raw AI response in output

Exit code is `0` on success, `1` on error.

## API reference (core)
```python
HumeSQL(
    db_config: dict,
    model: str = "gemini-2.5-flash",
    api_key: str | None = None,
    cache_schema: bool = True,
)
```

- `.query(user_text: str, debug: bool = False) -> dict`: main call
- `.refresh_schema_cache()`: reload schema immediately

### Schema caching
- Enabled by default (`cache_schema=True`)
- Turn off by passing `cache_schema=False`
- Call `refresh_schema_cache()` after DB changes (new tables/columns)

### Safety guardrails
- Blocks SQL containing `DROP`, `TRUNCATE`, `ALTER`, `;`, or `information_schema`
- Adds `LIMIT 100` if the model returns a SELECT without LIMIT
- Rejects non-JSON or malformed model responses

### Models
- Default: `gemini-2.5-flash`
- Override via constructor `model="gemini-1.5-pro-latest"` or CLI `--model ...`
- Ensure your API key has access to the chosen model

## Prompting tips
- Be specific about filters: “last 5 orders from customers in Nepal”
- Mention columns or table hints when you know them
- Include aggregation expectations: “average order value per month”
- For date ranges, state them explicitly

## Troubleshooting
- **“API key not valid”**: check `HUMESQL_AI_KEY` or pass `--api-key`; confirm Gemini access to the model.
- **404 model not found**: choose a supported model (`--model gemini-2.5-flash`).
- **DB connection errors**: verify host/port/user/password and network access to MySQL.
- **Malformed JSON from model**: rerun with `debug=True` to inspect `raw_ai_response`; the JSON sanitizer is lenient but will fail on non-JSON outputs.
- **Schema changes not reflected**: call `refresh_schema_cache()` or start with `cache_schema=False`.

## Development
- Install: `pip install -e .`
- Run example: `python example.py` (after setting env vars and DB creds)
- CLI smoke test without DB (will error for lack of key): `humesql "test" -H localhost -u root -d testdb --api-key dummy`

## License
MIT — see `LICENSE`.
