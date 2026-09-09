import sqlite3
import os
import json
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "submission_history.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            issues_json TEXT NOT NULL,
            total_issues INTEGER NOT NULL,
            quality_score INTEGER NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_user_file ON submissions(user_id, filename)")
    conn.commit()
    conn.close()


def save_submission(user_id: str, filename: str, issues: list, quality_score: int):
    conn = get_connection()
    conn.execute(
        "INSERT INTO submissions (user_id, filename, timestamp, issues_json, total_issues, quality_score) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            user_id,
            filename,
            datetime.now(timezone.utc).isoformat(),
            json.dumps(issues),
            len(issues),
            quality_score,
        ),
    )
    conn.commit()
    conn.close()


def get_previous_submission(user_id: str, filename: str):
    """Returns this user's most recent PRIOR submission of this same filename, or None if it's their first."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM submissions WHERE user_id = ? AND filename = ? ORDER BY id DESC LIMIT 1",
        (user_id, filename),
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "id": row["id"],
        "timestamp": row["timestamp"],
        "issues": json.loads(row["issues_json"]),
        "total_issues": row["total_issues"],
        "quality_score": row["quality_score"],
    }


def get_user_history(user_id: str, filename: str = None, limit: int = 20):
    """Returns this user's submission history, optionally filtered to one filename,
    most recent first."""
    conn = get_connection()
    if filename:
        rows = conn.execute(
            "SELECT * FROM submissions WHERE user_id = ? AND filename = ? ORDER BY id DESC LIMIT ?",
            (user_id, filename, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM submissions WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "filename": r["filename"],
            "timestamp": r["timestamp"],
            "total_issues": r["total_issues"],
            "quality_score": r["quality_score"],
        }
        for r in rows
    ]


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at: {os.path.abspath(DB_PATH)}")