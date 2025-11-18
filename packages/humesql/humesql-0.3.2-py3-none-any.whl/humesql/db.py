"""
Database helpers for HumeSQL.

Currently supports MySQL/MariaDB via mysql-connector-python.
"""

from typing import Dict, Any, List, Optional

from .utils import HumanSQLException

try:  # pragma: no cover - dependency check
    import mysql.connector
    from mysql.connector.connection import MySQLConnection
except ImportError:  # pragma: no cover
    mysql = None  # type: ignore[assignment]
    MySQLConnection = Any  # type: ignore[misc]


def get_connection(db_config: Dict[str, Any]) -> MySQLConnection:
    """
    Create a MySQL connection using mysql-connector.
    db_config example:
    {
        "host": "localhost",
        "user": "root",
        "password": "pass",
        "database": "mydb",
        "port": 3306,
    }
    """
    if mysql is None:
        raise HumanSQLException(
            "mysql-connector-python is required. Install it with "
            "`pip install mysql-connector-python`."
        )

    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as e:
        raise HumanSQLException(f"Error connecting to DB: {e}") from e


def get_schema(db_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Read DB schema: list tables and columns.
    Returns a dict:
    {
      "table_name": [
        {
          "Field": "...",
          "Type": "...",
          "Null": "NO/YES",
          "Key": "...",
          "Default": "...",
          "Extra": "..."
        },
        ...
      ],
      ...
    }
    """
    conn = get_connection(db_config)
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]

        schema: Dict[str, Any] = {}
        for table in tables:
            cursor.execute(f"SHOW FULL COLUMNS FROM `{table}`")
            cols = cursor.fetchall()
            col_names = [d[0] for d in cursor.description]

            cols_struct = [
                {col_names[i]: value for i, value in enumerate(row)}
                for row in cols
            ]
            schema[table] = cols_struct

        return schema
    finally:
        conn.close()


def execute_sql(
    db_config: Dict[str, Any],
    sql: str,
    params: Optional[Dict[str, Any]] = None,
    fetch: bool = True,
) -> List[Dict[str, Any]]:
    """
    Execute SQL and return rows as list of dicts (if SELECT).
    For non-SELECT, returns empty list by default.
    """
    conn = get_connection(db_config)
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or {})

        rows: List[Dict[str, Any]] = []
        if fetch and cursor.with_rows:
            rows = cursor.fetchall()

        conn.commit()
        cursor.close()
        return rows
    except mysql.connector.Error as e:
        raise HumanSQLException(f"DB error while executing SQL: {e}") from e
    finally:
        conn.close()
