from __future__ import annotations

from typing import Any

import psycopg


def execute_query(cursor: psycopg.Cursor, query: str, data: Any | None) -> list[tuple]:
    """Execute a SQL statement with optional parameters and return any fetched rows."""
    if data is None:
        cursor.execute(query)
    elif isinstance(data, dict):
        cursor.execute(query, data)
    elif isinstance(data, list):
        if len(data) == 0:
            raise ValueError("Data file is empty; there is nothing to execute.")

        if all(isinstance(item, dict) for item in data):
            cursor.executemany(query, data)
        elif all(isinstance(item, (list, tuple)) for item in data):
            cursor.executemany(query, data)
        else:
            cursor.executemany(query, [(item,) for item in data])
    else:
        cursor.execute(query, (data,))

    if cursor.description is None:
        return []
    return cursor.fetchall()


def connect_and_execute(database_url: str, query: str, data: Any | None, dry_run: bool) -> list[tuple]:
    """Open a connection, run the query, and return the result rows."""
    if dry_run:
        return []

    with psycopg.connect(database_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            return execute_query(cur, query, data)
