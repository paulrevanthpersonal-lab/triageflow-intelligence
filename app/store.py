import json
import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.environ.get("TRIAGEFLOW_DB_PATH", ROOT / "triageflow.db"))


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize() -> None:
    with connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS classifications (
              ticket_id TEXT PRIMARY KEY,
              created_at TEXT NOT NULL,
              subject TEXT NOT NULL,
              description TEXT NOT NULL,
              requester TEXT NOT NULL,
              affected_users INTEGER NOT NULL,
              business_service TEXT NOT NULL,
              category TEXT NOT NULL,
              category_confidence REAL NOT NULL,
              priority TEXT NOT NULL,
              priority_confidence REAL NOT NULL,
              assignment_group TEXT NOT NULL,
              needs_human_review INTEGER NOT NULL,
              result_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS feedback (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              ticket_id TEXT NOT NULL,
              created_at TEXT NOT NULL,
              accepted INTEGER NOT NULL,
              corrected_category TEXT,
              corrected_priority TEXT,
              note TEXT NOT NULL,
              FOREIGN KEY(ticket_id) REFERENCES classifications(ticket_id)
            );
            """
        )


def save_classification(payload: dict, prediction: dict) -> None:
    with connect() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO classifications VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                prediction["ticket_id"],
                datetime.now(UTC).isoformat(),
                payload["subject"],
                payload["description"],
                payload["requester"],
                payload["affected_users"],
                payload["business_service"],
                prediction["category"],
                prediction["category_confidence"],
                prediction["priority"],
                prediction["priority_confidence"],
                prediction["assignment_group"],
                int(prediction["needs_human_review"]),
                json.dumps(prediction),
            ),
        )


def save_feedback(payload: dict) -> dict:
    with connect() as connection:
        exists = connection.execute(
            "SELECT ticket_id FROM classifications WHERE ticket_id = ?", (payload["ticket_id"],)
        ).fetchone()
        if not exists:
            raise KeyError(payload["ticket_id"])
        cursor = connection.execute(
            """
            INSERT INTO feedback(
              ticket_id, created_at, accepted, corrected_category, corrected_priority, note
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload["ticket_id"],
                datetime.now(UTC).isoformat(),
                int(payload["accepted"]),
                payload.get("corrected_category"),
                payload.get("corrected_priority"),
                payload.get("note", ""),
            ),
        )
        return {"feedback_id": cursor.lastrowid, "status": "recorded"}


def recent_classifications(limit: int = 25) -> list[dict]:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT ticket_id, created_at, subject, requester, affected_users, business_service,
                   category, category_confidence, priority, priority_confidence,
                   assignment_group, needs_human_review
            FROM classifications ORDER BY created_at DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def operational_metrics() -> dict:
    with connect() as connection:
        total = connection.execute("SELECT COUNT(*) FROM classifications").fetchone()[0]
        reviews = connection.execute(
            "SELECT COUNT(*) FROM classifications WHERE needs_human_review = 1"
        ).fetchone()[0]
        feedback = connection.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
        accepted = connection.execute("SELECT COUNT(*) FROM feedback WHERE accepted = 1").fetchone()[0]
    return {
        "classified_tickets": total,
        "human_review_rate": round(reviews / total, 3) if total else 0,
        "feedback_events": feedback,
        "feedback_acceptance_rate": round(accepted / feedback, 3) if feedback else 0,
    }
