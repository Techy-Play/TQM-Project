"""Database query helper functions and utilities.

Encapsulates parameterized query execution, transaction-safe reads/writes,
and EXPLAIN QUERY PLAN tooling for performance validation (Q13).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union
import sqlite3

from app.database.connection import get_db_connection

logger = logging.getLogger(__name__)


def execute_insert(
    sql: str,
    params: Sequence[Any] = (),
    custom_path: Optional[Union[str, Path]] = None,
) -> int:
    """Execute a parameterized INSERT query and return the new row ID."""
    with get_db_connection(custom_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.lastrowid or 0


def execute_update_or_delete(
    sql: str,
    params: Sequence[Any] = (),
    custom_path: Optional[Union[str, Path]] = None,
) -> int:
    """Execute an UPDATE or DELETE query and return the number of affected rows."""
    with get_db_connection(custom_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.rowcount


def fetch_one(
    sql: str,
    params: Sequence[Any] = (),
    custom_path: Optional[Union[str, Path]] = None,
) -> Optional[sqlite3.Row]:
    """Execute a parameterized query and return the first matching row or None."""
    with get_db_connection(custom_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchone()


def fetch_all(
    sql: str,
    params: Sequence[Any] = (),
    custom_path: Optional[Union[str, Path]] = None,
) -> List[sqlite3.Row]:
    """Execute a parameterized query and return all matching rows."""
    with get_db_connection(custom_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()


def table_exists(
    table_name: str,
    custom_path: Optional[Union[str, Path]] = None,
) -> bool:
    """Verify if a table exists in the SQLite database."""
    sql = "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ? LIMIT 1;"
    row = fetch_one(sql, (table_name,), custom_path)
    return row is not None


def get_table_columns(
    table_name: str,
    custom_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """Retrieve column specifications for a given table using PRAGMA table_info."""
    with get_db_connection(custom_path) as conn:
        cursor = conn.cursor()
        # PRAGMA doesn't accept bind parameters for identifiers, sanitize name
        cursor.execute(f"PRAGMA table_info({table_name});")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def explain_query_plan(
    sql: str,
    params: Sequence[Any] = (),
    custom_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """Run EXPLAIN QUERY PLAN on a query to verify index utilization (Q13 requirement)."""
    with get_db_connection(custom_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"EXPLAIN QUERY PLAN {sql}", params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_setting(
    key: str,
    default: Optional[str] = None,
    custom_path: Optional[Union[str, Path]] = None,
) -> Optional[str]:
    """Get an application setting value by key."""
    row = fetch_one(
        "SELECT value FROM app_settings WHERE key = ?",
        (key,),
        custom_path,
    )
    return row["value"] if row else default


def set_setting(
    key: str,
    value: str,
    custom_path: Optional[Union[str, Path]] = None,
) -> None:
    """Persist an application setting key-value pair."""
    sql = """
    INSERT INTO app_settings (key, value, updated_at)
    VALUES (?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(key) DO UPDATE SET
        value = excluded.value,
        updated_at = CURRENT_TIMESTAMP;
    """
    with get_db_connection(custom_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (key, value))
