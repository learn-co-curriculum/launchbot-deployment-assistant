"""SQLite thread and message persistence."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    """Return the current UTC timestamp as an ISO string."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(database_path: str) -> sqlite3.Connection:
    """Open a SQLite connection with row dictionaries enabled."""
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_database(database_path: str) -> None:
    """Create chat persistence tables when needed."""
    with connect(database_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS threads (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                thread_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
            )
            """
        )
        conn.commit()


def row_to_thread(row: sqlite3.Row) -> dict[str, Any]:
    """Convert a thread row into an API dictionary."""
    return {
        "id": row["id"],
        "title": row["title"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def row_to_message(row: sqlite3.Row) -> dict[str, Any]:
    """Convert a message row into an API dictionary."""
    try:
        metadata = json.loads(row["metadata"] or "{}")
    except json.JSONDecodeError:
        metadata = {}

    return {
        "id": row["id"],
        "thread_id": row["thread_id"],
        "role": row["role"],
        "content": row["content"],
        "metadata": metadata,
        "created_at": row["created_at"],
    }


def list_threads(database_path: str) -> list[dict[str, Any]]:
    """Return threads ordered by most recently updated."""
    ensure_database(database_path)

    with connect(database_path) as conn:
        rows = conn.execute(
            """
            SELECT id, title, created_at, updated_at
            FROM threads
            ORDER BY updated_at DESC
            """
        ).fetchall()

    return [row_to_thread(row) for row in rows]


def create_thread(database_path: str, title: str = "New deployment chat") -> dict[str, Any]:
    """Create and return a thread."""
    ensure_database(database_path)

    thread_id = str(uuid4())
    now = utc_now()

    with connect(database_path) as conn:
        conn.execute(
            """
            INSERT INTO threads (id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (thread_id, title, now, now),
        )
        conn.commit()

    return {
        "id": thread_id,
        "title": title,
        "created_at": now,
        "updated_at": now,
    }


def get_thread(database_path: str, thread_id: str) -> dict[str, Any] | None:
    """Return one thread with its messages."""
    ensure_database(database_path)

    with connect(database_path) as conn:
        thread_row = conn.execute(
            """
            SELECT id, title, created_at, updated_at
            FROM threads
            WHERE id = ?
            """,
            (thread_id,),
        ).fetchone()

        if thread_row is None:
            return None

        message_rows = conn.execute(
            """
            SELECT id, thread_id, role, content, metadata, created_at
            FROM messages
            WHERE thread_id = ?
            ORDER BY created_at ASC
            """,
            (thread_id,),
        ).fetchall()

    return {
        "thread": row_to_thread(thread_row),
        "messages": [row_to_message(row) for row in message_rows],
    }


def update_thread_title_if_default(
    conn: sqlite3.Connection,
    *,
    thread_id: str,
    content: str,
    now: str,
) -> None:
    """Use the first user message as the title when the thread still has the default title."""
    row = conn.execute(
        "SELECT title FROM threads WHERE id = ?",
        (thread_id,),
    ).fetchone()

    if row and row["title"] == "New deployment chat":
        title = content[:60].strip()
        if len(content) > 60:
            title += "..."
        conn.execute(
            "UPDATE threads SET title = ?, updated_at = ? WHERE id = ?",
            (title, now, thread_id),
        )


def add_message(
    database_path: str,
    *,
    thread_id: str,
    role: str,
    content: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Add a message to a thread and return it."""
    ensure_database(database_path)

    message_id = str(uuid4())
    now = utc_now()
    metadata_json = json.dumps(metadata or {})

    with connect(database_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            INSERT INTO messages (id, thread_id, role, content, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (message_id, thread_id, role, content, metadata_json, now),
        )

        if role == "user":
            update_thread_title_if_default(conn, thread_id=thread_id, content=content, now=now)

        conn.execute(
            "UPDATE threads SET updated_at = ? WHERE id = ?",
            (now, thread_id),
        )
        conn.commit()

        row = conn.execute(
            """
            SELECT id, thread_id, role, content, metadata, created_at
            FROM messages
            WHERE id = ?
            """,
            (message_id,),
        ).fetchone()

    return row_to_message(row)


def delete_thread(database_path: str, thread_id: str) -> bool:
    """Delete a thread and its messages."""
    ensure_database(database_path)

    with connect(database_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.execute(
            "DELETE FROM threads WHERE id = ?",
            (thread_id,),
        )
        conn.commit()

    return cursor.rowcount > 0
