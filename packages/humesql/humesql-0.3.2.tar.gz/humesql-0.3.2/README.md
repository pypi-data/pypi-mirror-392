# HumeSQL

HumeSQL turns natural language into safe SQL, runs it against your MySQL/MariaDB database, and returns JSON rows. It introspects your schema, prompts Gemini to craft SQL, applies guardrails, executes the query, and responds with the SQL, reasoning, and results.

- **Fast start:** drop in DB creds + Gemini key, ask questions in English.  
- **Safe by default:** blocks destructive SQL, adds LIMITs, only uses tables in your schema.  
- **Flexible:** Python API + CLI, schema caching, debug output from the LLM.

> Documentation: https://nirajang20.github.io/HumeSQL/

## Installation
PyPI:
```bash
pip install humesql
```

From source:
```bash
pip install -e .
```

## Quickstart (Python)
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

Response structure (keys may be `null` on errors):
- `ok`: bool
- `sql`: generated SQL
- `reasoning`: short explanation
- `limit_applied`: bool or `null`
- `rows`: list of result dicts (if SELECT)
- `time_ms`: total time in milliseconds
- `raw_ai_response`: only when `debug=True`

## Configuration
Environment variable priority for the Gemini key:
1) Explicit `api_key` argument  
2) `HUMESQL_AI_KEY` (preferred)  
3) `HUMANSQL_AI_KEY` (legacy)  
4) `GEMINI_API_KEY`

Example:
```bash
export HUMESQL_AI_KEY="your-gemini-key"
```

## CLI
Run one-off queries from the terminal:
```bash
humesql "last 5 customers from Nepal" \
  -H localhost -u root -p "" -d classicmodels --port 3306 \
  --api-key "$HUMESQL_AI_KEY" --model gemini-2.5-flash --debug
```

Key flags:
- `query` (positional): natural language input
- `-H/--host`, `-u/--user`, `-p/--password`, `-d/--database`, `--port`
- `--api-key`: override env vars
- `--model`: Gemini model (default `gemini-2.5-flash`)
- `--no-cache-schema`: disable schema caching
- `--debug`: include raw AI response in output

Exit code `0` on success, `1` on error.

## API highlights
```python
HumeSQL(
    db_config: dict,
    model: str = "gemini-2.5-flash",
    api_key: str | None = None,
    cache_schema: bool = True,
)
```
- `.query(user_text: str, debug: bool = False) -> dict`
- `.refresh_schema_cache()`

### Safety guardrails
- Blocks SQL containing `DROP`, `TRUNCATE`, `ALTER`, `;`, or `information_schema`
- Adds `LIMIT 100` if the model omits it on SELECT
- Rejects non-JSON or malformed model responses

### Schema caching
- Enabled by default; disable with `cache_schema=False`
- Call `refresh_schema_cache()` after DB schema changes

### Prompting tips
- Be explicit about filters: “last 5 orders from customers in Nepal”
- Name entities when possible: table/column hints help
- State aggregations/ranges: “average order value per month in 2023”

## Troubleshooting
- **API key not valid:** check `HUMESQL_AI_KEY` or pass `--api-key`; ensure the key has access to your chosen Gemini model.
- **Model not found (404):** pick a supported model, e.g., `--model gemini-2.5-flash`.
- **DB connection errors:** verify host/port/user/password and MySQL reachability.
- **Malformed JSON from model:** rerun with `debug=True` to inspect `raw_ai_response`.
- **Schema changes not reflected:** call `refresh_schema_cache()` or disable caching.

## Development
- Install deps: `pip install -e .`
- Example: set env vars + DB creds, then `python example.py`
- Type check / lint locally as needed

## License
MIT — see `LICENSE`.
