#!/usr/bin/env python3
# MIT License

from __future__ import annotations

import sqlite3
import sys
import time
from pathlib import Path

from aether_core import index_memory_document, timestamp_id


def discover_project_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "config" / "aether.yaml").exists():
            return candidate
    raise RuntimeError("Unable to determine AetherOS project root")


PROJECT_ROOT = discover_project_root()
sys.path.insert(0, str(PROJECT_ROOT / "lib"))

DB_PATH = PROJECT_ROOT / "data" / "sqlite" / "aether.db"
LOG_PATH = PROJECT_ROOT / "runtime" / "logs" / "vector-memory-agent.log"


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
        CREATE TABLE IF NOT EXISTS vector_memory_checkpoint (
            stream_name TEXT PRIMARY KEY,
            last_event_id INTEGER NOT NULL
        )
        """
    )
    db.commit()


def last_checkpoint(db: sqlite3.Connection) -> int:
    row = db.execute(
        """
        SELECT last_event_id FROM vector_memory_checkpoint
        WHERE stream_name = 'event_bus'
        """
    ).fetchone()
    return int(row["last_event_id"]) if row else 0


def update_checkpoint(db: sqlite3.Connection, event_id: int) -> None:
    db.execute(
        """
        INSERT INTO vector_memory_checkpoint(stream_name, last_event_id)
        VALUES ('event_bus', ?)
        ON CONFLICT(stream_name) DO UPDATE SET
            last_event_id = excluded.last_event_id
        """,
        (event_id,),
    )
    db.commit()


def index_new_events(db: sqlite3.Connection) -> int:
    checkpoint = last_checkpoint(db)
    rows = db.execute(
        """
        SELECT id, event_type, source, payload_json, ts
        FROM event_bus
        WHERE id > ?
        ORDER BY id ASC
        LIMIT 100
        """,
        (checkpoint,),
    ).fetchall()

    if not rows:
        return 0

    last_id = checkpoint
    for row in rows:
        event_id = int(row["id"])
        doc_id = timestamp_id(f"event-{event_id}")
        text = f"{row['event_type']} {row['source']} {row['payload_json']}"
        index_memory_document(
            doc_id=doc_id,
            text=text,
            metadata={
                "event_id": event_id,
                "event_type": row["event_type"],
                "source": row["source"],
                "ts": row["ts"],
            },
        )
        last_id = event_id

    update_checkpoint(db, last_id)
    return len(rows)


def main() -> None:
    log("vector_memory_agent_started")
    while True:
        db = connect()
        ensure_tables(db)
        indexed = index_new_events(db)
        db.close()
        log(f"vector_memory_agent_cycle indexed={indexed}")
        time.sleep(10)


if __name__ == "__main__":
    main()
