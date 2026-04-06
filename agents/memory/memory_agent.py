# MIT License

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

DB_PATH = Path("/data/sqlite/aether.db")
LOG_PATH = Path("/data/logs/memory-agent.log")


def log(message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(f"{message}\n")


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_tables(db: sqlite3.Connection) -> None:
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS memory_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            memory_type TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT NOT NULL
        )
        """
    )
    db.commit()


def ingest_recent_events(db: sqlite3.Connection) -> int:
    rows = db.execute(
        """
        SELECT id, payload_json, source, event_type
        FROM event_bus
        WHERE event_type IN ('user.prompt.received',
                             'orchestrator.plan.created')
        ORDER BY id DESC
        LIMIT 20
        """
    ).fetchall()

    inserted = 0
    for row in rows:
        content = json.dumps(
            {
                "event_type": row["event_type"],
                "source": row["source"],
                "payload": json.loads(row["payload_json"]),
            }
        )
        db.execute(
            """
            INSERT INTO memory_items(memory_type, content, source)
            VALUES (?, ?, ?)
            """,
            ("episodic", content, "memory-agent"),
        )
        inserted += 1

    db.commit()
    return inserted


def main() -> None:
    log("memory_agent_started")
    while True:
        db = connect()
        ensure_tables(db)
        inserted = ingest_recent_events(db)
        db.close()
        log(f"memory_agent_cycle inserted={inserted}")
        time.sleep(20)


if __name__ == "__main__":
    main()
