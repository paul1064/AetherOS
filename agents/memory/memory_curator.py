#!/usr/bin/env python3
# MIT License

from __future__ import annotations

import re
import sys
from pathlib import Path

from aether_core import (
    emit_event,
    events_since,
    index_memory_document,
    init_event_bus,
    insert_long_term_memory,
    load_config,
    record_system_event,
    sleep_loop,
    timestamp_id,
    touch_entity,
    update_curator_checkpoint,
    upsert_graph_edge,
    upsert_graph_entity,
    write_agent_state,
)


def discover_project_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "config" / "aether.yaml").exists():
            return candidate
    raise RuntimeError("Unable to determine AetherOS project root")


PROJECT_ROOT = discover_project_root()
sys.path.insert(0, str(PROJECT_ROOT / "lib"))

LOG_PATH = PROJECT_ROOT / "runtime" / "logs" / "memory-curator.log"
ENTITY_PATTERN = re.compile(r"\b[A-Z][A-Za-z0-9._-]{2,}\b")


def log(message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(f"{message}\n")


def extract_entities(text: str) -> list[str]:
    seen: list[str] = []
    for match in ENTITY_PATTERN.findall(text):
        if match not in seen:
            seen.append(match)
    return seen[:10]


def curate_event(event: dict) -> None:
    event_id = int(event["id"])
    event_type = str(event["event_type"])
    source = str(event["source"])
    payload_json = str(event["payload_json"])
    summary = f"{event_type} from {source}"
    evidence = payload_json
    confidence = 0.65

    memory_id = insert_long_term_memory(
        category=event_type,
        summary=summary,
        evidence=evidence,
        source_event_id=event_id,
        confidence=confidence,
    )
    index_memory_document(
        doc_id=timestamp_id(f"ltm-{memory_id}"),
        text=f"{summary} {evidence}",
        metadata={
            "memory_id": memory_id,
            "category": event_type,
            "source_event_id": event_id,
            "source": source,
        },
    )

    entities = extract_entities(f"{event_type} {source} {payload_json}")
    upsert_graph_entity(source, "source")
    for entity in entities:
        touch_entity(entity, "symbolic")
        upsert_graph_entity(entity, "symbolic")
        upsert_graph_edge(source, entity, "mentioned")

    emit_event(
        "memory.curated",
        "memory-curator",
        {"event_id": event_id, "memory_id": memory_id, "entities": entities},
    )


def main() -> None:
    init_event_bus()
    write_agent_state("memory-curator", "running", "running")
    log("memory_curator_started")
    while True:
        try:
            from aether_core import curator_checkpoint

            checkpoint = curator_checkpoint()
            rows = events_since(checkpoint, limit=100)
            last_id = checkpoint
            for row in rows:
                curate_event(dict(row))
                last_id = int(row["id"])
            if last_id != checkpoint:
                update_curator_checkpoint(last_id)
            write_agent_state("memory-curator", "running", "running")
            log(f"memory_curator_cycle curated={len(rows)}")
        except Exception as exc:
            message = f"memory_curator_failed: {exc}"
            record_system_event("memory-curator", "error", message)
            write_agent_state("memory-curator", "running", "degraded")
            log(message)
        interval = int(load_config().memory.get("curator_interval_sec", 20))
        sleep_loop(interval)


if __name__ == "__main__":
    main()
