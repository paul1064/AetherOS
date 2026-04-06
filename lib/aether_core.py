#!/usr/bin/env python3
# MIT License

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import time
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import chromadb
import requests
import yaml


AETHER_ROOT_ENV = "AETHER_ROOT"


def discover_aether_root() -> Path:
    env_root = os.environ.get(AETHER_ROOT_ENV)
    if env_root:
        return Path(env_root).expanduser().resolve()

    for candidate in Path(__file__).resolve().parents:
        if (candidate / "config" / "aether.yaml").exists():
            return candidate

    raise RuntimeError("Unable to determine AetherOS project root")


AETHER_ROOT = discover_aether_root()
CONFIG_PATH = AETHER_ROOT / "config" / "aether.yaml"
POLICY_PATH = AETHER_ROOT / "config" / "policy.yaml"
MODELS_PATH = AETHER_ROOT / "config" / "models.yaml"


def resolve_repo_path(value: str) -> str:
    path = Path(value).expanduser()
    if path.is_absolute():
        return str(path)
    return str((AETHER_ROOT / path).resolve())


def resolve_config_paths(raw: dict[str, Any]) -> dict[str, Any]:
    path_fields = (
        ("system", "root"),
        ("runtime", "socket_dir"),
        ("runtime", "state_dir"),
        ("runtime", "lock_dir"),
        ("runtime", "log_dir"),
        ("ai", "registry_file"),
        ("memory", "sqlite_path"),
        ("memory", "chroma_path"),
        ("memory", "graph_path"),
        ("memory", "graph_file"),
        ("desktop", "hypr_config"),
        ("desktop", "waybar_config"),
        ("desktop", "waybar_style"),
        ("multimodal", "screenshot_dir"),
        ("multimodal", "voice_dir"),
        ("meta_agent", "jobs_dir"),
        ("meta_agent", "runs_dir"),
    )
    for section, key in path_fields:
        section_data = raw.get(section)
        if isinstance(section_data, dict):
            value = section_data.get(key)
            if isinstance(value, str):
                section_data[key] = resolve_repo_path(value)
    return raw


@dataclass
class AetherConfig:
    raw: dict[str, Any]

    @property
    def sqlite_path(self) -> Path:
        return Path(self.raw["memory"]["sqlite_path"])

    @property
    def ollama_host(self) -> str:
        return self.raw["ai"]["host"]

    @property
    def primary_model(self) -> str:
        return self.raw["ai"]["primary_model"]

    @property
    def chroma_path(self) -> Path:
        return Path(self.raw["memory"]["chroma_path"])

    @property
    def self_healing(self) -> dict[str, Any]:
        return self.raw.get("self_healing", {})

    @property
    def resource_intelligence(self) -> dict[str, Any]:
        return self.raw.get("resource_intelligence", {})

    @property
    def memory(self) -> dict[str, Any]:
        return self.raw.get("memory", {})

    @property
    def ai(self) -> dict[str, Any]:
        return self.raw.get("ai", {})


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_config() -> AetherConfig:
    return AetherConfig(resolve_config_paths(load_yaml(CONFIG_PATH)))


def load_policy() -> dict[str, Any]:
    return load_yaml(POLICY_PATH)["policy"]


def seed_governance_profiles() -> None:
    policy = load_policy()
    profiles = policy.get("source_profiles", {})
    if not profiles:
        return

    db = get_db()
    for source_name, capability_profile in profiles.items():
        insert_sql = """
            INSERT INTO governance_profiles(source_name, capability_profile, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(source_name) DO NOTHING
            """
        db.execute(insert_sql, (source_name, capability_profile))
    db.commit()
    db.close()


def load_models_registry() -> dict[str, Any]:
    if MODELS_PATH.exists():
        return load_yaml(MODELS_PATH)
    cfg = load_config()
    registry_file = cfg.ai.get("registry_file")
    if registry_file and Path(registry_file).exists():
        return load_yaml(Path(registry_file))
    return {"models": {}}


def seed_model_registry() -> None:
    registry = load_models_registry().get("models", {})
    if not registry:
        return

    db = get_db()
    for model_name, meta in registry.items():
        insert_sql = """
            INSERT INTO model_registry(model_name, role, enabled, installed,
                                       auto_pull, size_hint, description, updated_at)
            VALUES (?, ?, ?, 0, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(model_name) DO UPDATE SET
                role = excluded.role,
                enabled = excluded.enabled,
                auto_pull = excluded.auto_pull,
                size_hint = excluded.size_hint,
                description = excluded.description,
                updated_at = CURRENT_TIMESTAMP
            """
        db.execute(
            insert_sql,
            (
                model_name,
                str(meta.get("role", "general")),
                1 if bool(meta.get("enabled", True)) else 0,
                1 if bool(meta.get("auto_pull", False)) else 0,
                str(meta.get("size_hint", "")),
                str(meta.get("description", "")),
            ),
        )
    db.commit()
    db.close()


def get_db() -> sqlite3.Connection:
    cfg = load_config()
    db = sqlite3.connect(cfg.sqlite_path)
    db.row_factory = sqlite3.Row
    ensure_db_schema(db)
    return db


def ensure_db_schema(db: sqlite3.Connection) -> None:
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS system_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            source TEXT NOT NULL,
            level TEXT NOT NULL,
            message TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS agent_state (
            agent_name TEXT PRIMARY KEY,
            desired_state TEXT NOT NULL,
            actual_state TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS event_bus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT NOT NULL,
            source TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'new'
        );

        CREATE TABLE IF NOT EXISTS command_proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            source TEXT NOT NULL,
            user_input TEXT NOT NULL,
            proposed_command TEXT NOT NULL,
            reason TEXT NOT NULL,
            needs_confirmation INTEGER NOT NULL DEFAULT 1,
            approved INTEGER NOT NULL DEFAULT 0,
            executed INTEGER NOT NULL DEFAULT 0,
            execution_output TEXT DEFAULT '',
            approval_note TEXT DEFAULT '',
            approved_at DATETIME,
            executed_at DATETIME
        );

        CREATE TABLE IF NOT EXISTS remediation_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            agent TEXT NOT NULL,
            target TEXT NOT NULL,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS resource_samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            cpu_pct REAL NOT NULL,
            memory_pct REAL NOT NULL,
            load_avg_1 REAL NOT NULL,
            load_avg_5 REAL NOT NULL,
            load_avg_15 REAL NOT NULL,
            available_memory_mb REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS meta_agent_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            prompt TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'queued',
            container_name TEXT DEFAULT '',
            image_name TEXT DEFAULT '',
            output_path TEXT DEFAULT '',
            notes TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS memory_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            memory_type TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS long_term_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            category TEXT NOT NULL,
            summary TEXT NOT NULL,
            evidence TEXT NOT NULL,
            source_event_id INTEGER,
            confidence REAL NOT NULL DEFAULT 0.5
        );

        CREATE TABLE IF NOT EXISTS knowledge_entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_name TEXT NOT NULL UNIQUE,
            entity_type TEXT NOT NULL,
            first_seen_ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_seen_ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            mention_count INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS memory_curator_checkpoint (
            stream_name TEXT PRIMARY KEY,
            last_event_id INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            actor TEXT NOT NULL,
            action TEXT NOT NULL,
            target TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS governance_profiles (
            source_name TEXT PRIMARY KEY,
            capability_profile TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS model_registry (
            model_name TEXT PRIMARY KEY,
            role TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1,
            installed INTEGER NOT NULL DEFAULT 0,
            auto_pull INTEGER NOT NULL DEFAULT 0,
            size_hint TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            last_seen_ts DATETIME,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    db.commit()


def init_event_bus() -> None:
    db = get_db()
    db.close()
    seed_governance_profiles()
    seed_model_registry()


def emit_event(event_type: str, source: str, payload: dict[str, Any]) -> None:
    db = get_db()
    db.execute(
        """
        INSERT INTO event_bus(event_type, source, payload_json, status)
        VALUES (?, ?, ?, 'new')
        """,
        (event_type, source, json.dumps(payload)),
    )
    db.commit()
    db.close()


def propose_command(
    source: str,
    user_input: str,
    proposed_command: str,
    reason: str,
    needs_confirmation: bool = True,
) -> int:
    db = get_db()
    insert_sql = """
        INSERT INTO command_proposals(
            source, user_input, proposed_command, reason, needs_confirmation
        )
        VALUES (?, ?, ?, ?, ?)
        """
    cursor = db.execute(
        insert_sql,
        (source, user_input, proposed_command, reason, 1 if needs_confirmation else 0),
    )
    db.commit()
    proposal_id = int(cursor.lastrowid)
    db.close()
    return proposal_id


def record_audit(actor: str, action: str, target: str, status: str, details: str) -> None:
    db = get_db()
    insert_sql = """
        INSERT INTO audit_log(actor, action, target, status, details)
        VALUES (?, ?, ?, ?, ?)
        """
    db.execute(insert_sql, (actor, action, target, status, details))
    db.commit()
    db.close()


def list_models() -> list[sqlite3.Row]:
    db = get_db()
    rows = db.execute(
        """
        SELECT * FROM model_registry
        ORDER BY role ASC, model_name ASC
        """
    ).fetchall()
    db.close()
    return rows


def fetch_model(model_name: str) -> sqlite3.Row | None:
    db = get_db()
    row = db.execute(
        """
        SELECT * FROM model_registry
        WHERE model_name = ?
        """,
        (model_name,),
    ).fetchone()
    db.close()
    return row


def update_model_status(model_name: str, installed: bool, details_seen: bool = True) -> None:
    db = get_db()
    db.execute(
        """
        UPDATE model_registry
        SET installed = ?,
            last_seen_ts = CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE last_seen_ts END,
            updated_at = CURRENT_TIMESTAMP
        WHERE model_name = ?
        """,
        (1 if installed else 0, 1 if details_seen else 0, model_name),
    )
    db.commit()
    db.close()


def recent_audit(limit: int = 30) -> list[sqlite3.Row]:
    db = get_db()
    rows = db.execute(
        """
        SELECT * FROM audit_log
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    db.close()
    return rows


def list_governance_profiles() -> list[sqlite3.Row]:
    db = get_db()
    rows = db.execute(
        """
        SELECT * FROM governance_profiles
        ORDER BY source_name ASC
        """
    ).fetchall()
    db.close()
    return rows


def update_governance_profile(source_name: str, capability_profile: str) -> None:
    db = get_db()
    db.execute(
        """
        INSERT INTO governance_profiles(source_name, capability_profile, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(source_name) DO UPDATE SET
            capability_profile = excluded.capability_profile,
            updated_at = CURRENT_TIMESTAMP
        """,
        (source_name, capability_profile),
    )
    db.commit()
    db.close()


def source_capability_profile(source_name: str) -> str:
    db = get_db()
    row = db.execute(
        """
        SELECT capability_profile FROM governance_profiles
        WHERE source_name = ?
        """,
        (source_name,),
    ).fetchone()
    db.close()
    if row:
        return str(row["capability_profile"])
    return str(load_policy().get("default_capability_profile", "observer"))


def latest_plan() -> dict[str, Any] | None:
    db = get_db()
    row = db.execute(
        """
        SELECT payload_json FROM event_bus
        WHERE event_type = 'orchestrator.plan.created'
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()
    db.close()
    if not row:
        return None
    return json.loads(row["payload_json"])


def latest_proposal() -> sqlite3.Row | None:
    db = get_db()
    row = db.execute(
        """
        SELECT * FROM command_proposals
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()
    db.close()
    return row


def fetch_proposal(proposal_id: int) -> sqlite3.Row | None:
    db = get_db()
    row = db.execute(
        """
        SELECT * FROM command_proposals
        WHERE id = ?
        """,
        (proposal_id,),
    ).fetchone()
    db.close()
    return row


def approve_proposal(proposal_id: int, note: str = "") -> bool:
    db = get_db()
    cursor = db.execute(
        """
        UPDATE command_proposals
        SET approved = 1,
            approval_note = ?,
            approved_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (note, proposal_id),
    )
    db.commit()
    changed = cursor.rowcount > 0
    db.close()
    return changed


def reject_proposal(proposal_id: int, note: str = "") -> bool:
    db = get_db()
    cursor = db.execute(
        """
        UPDATE command_proposals
        SET approved = 0,
            executed = 1,
            approval_note = ?,
            executed_at = CURRENT_TIMESTAMP,
            execution_output = 'Rejected by user'
        WHERE id = ?
        """,
        (note, proposal_id),
    )
    db.commit()
    changed = cursor.rowcount > 0
    db.close()
    return changed


def fetch_ready_proposals(limit: int = 10) -> list[sqlite3.Row]:
    db = get_db()
    rows = db.execute(
        """
        SELECT * FROM command_proposals
        WHERE approved = 1 AND executed = 0
        ORDER BY id ASC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    db.close()
    return rows


def mark_proposal_executed(proposal_id: int, output: str) -> None:
    db = get_db()
    db.execute(
        """
        UPDATE command_proposals
        SET executed = 1,
            execution_output = ?,
            executed_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (output, proposal_id),
    )
    db.commit()
    db.close()


def write_agent_state(agent: str, desired: str, actual: str) -> None:
    db = get_db()
    db.execute(
        """
        INSERT INTO agent_state(agent_name, desired_state, actual_state, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(agent_name) DO UPDATE SET
            desired_state = excluded.desired_state,
            actual_state = excluded.actual_state,
            updated_at = CURRENT_TIMESTAMP
        """,
        (agent, desired, actual),
    )
    db.commit()
    db.close()


def fetch_agent_states() -> list[sqlite3.Row]:
    db = get_db()
    rows = db.execute(
        """
        SELECT * FROM agent_state
        ORDER BY agent_name ASC
        """
    ).fetchall()
    db.close()
    return rows


def record_remediation_action(
    agent: str, target: str, action: str, status: str, details: str
) -> None:
    db = get_db()
    db.execute(
        """
        INSERT INTO remediation_actions(agent, target, action, status, details)
        VALUES (?, ?, ?, ?, ?)
        """,
        (agent, target, action, status, details),
    )
    db.commit()
    db.close()


def recent_remediation_count(target: str, action: str, window_minutes: int = 60) -> int:
    db = get_db()
    row = db.execute(
        """
        SELECT COUNT(*) AS total
        FROM remediation_actions
        WHERE target = ?
          AND action = ?
          AND ts >= datetime('now', ?)
        """,
        (target, action, f"-{window_minutes} minutes"),
    ).fetchone()
    db.close()
    return int(row["total"]) if row else 0


def recent_remediations(limit: int = 10) -> list[sqlite3.Row]:
    db = get_db()
    rows = db.execute(
        """
        SELECT * FROM remediation_actions
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    db.close()
    return rows


def record_resource_sample(
    cpu_pct: float,
    memory_pct: float,
    load_avg_1: float,
    load_avg_5: float,
    load_avg_15: float,
    available_memory_mb: float,
) -> None:
    db = get_db()
    db.execute(
        """
        INSERT INTO resource_samples(
            cpu_pct, memory_pct, load_avg_1, load_avg_5, load_avg_15, available_memory_mb
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (cpu_pct, memory_pct, load_avg_1, load_avg_5, load_avg_15, available_memory_mb),
    )
    db.commit()
    db.close()


def latest_resource_sample() -> sqlite3.Row | None:
    db = get_db()
    row = db.execute(
        """
        SELECT * FROM resource_samples
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()
    db.close()
    return row


def recent_system_events(limit: int = 20) -> list[sqlite3.Row]:
    db = get_db()
    rows = db.execute(
        """
        SELECT * FROM system_events
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    db.close()
    return rows


def recent_events(limit: int = 20) -> list[sqlite3.Row]:
    db = get_db()
    rows = db.execute(
        """
        SELECT * FROM event_bus
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    db.close()
    return rows


def insert_long_term_memory(
    category: str,
    summary: str,
    evidence: str,
    source_event_id: int | None,
    confidence: float,
) -> int:
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO long_term_memory(category, summary, evidence, source_event_id, confidence)
        VALUES (?, ?, ?, ?, ?)
        """,
        (category, summary, evidence, source_event_id, confidence),
    )
    db.commit()
    memory_id = int(cursor.lastrowid)
    db.close()
    return memory_id


def recent_long_term_memories(limit: int = 20) -> list[sqlite3.Row]:
    db = get_db()
    rows = db.execute(
        """
        SELECT * FROM long_term_memory
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    db.close()
    return rows


def search_long_term_memory(query: str, limit: int = 10) -> list[sqlite3.Row]:
    pattern = f"%{query.lower()}%"
    db = get_db()
    rows = db.execute(
        """
        SELECT * FROM long_term_memory
        WHERE lower(summary) LIKE ?
           OR lower(evidence) LIKE ?
           OR lower(category) LIKE ?
        ORDER BY confidence DESC, id DESC
        LIMIT ?
        """,
        (pattern, pattern, pattern, limit),
    ).fetchall()
    db.close()
    return rows


def touch_entity(entity_name: str, entity_type: str = "unknown") -> None:
    db = get_db()
    row = db.execute(
        """
        SELECT id, mention_count FROM knowledge_entities
        WHERE entity_name = ?
        """,
        (entity_name,),
    ).fetchone()
    if row:
        db.execute(
            """
            UPDATE knowledge_entities
            SET last_seen_ts = CURRENT_TIMESTAMP,
                mention_count = mention_count + 1
            WHERE id = ?
            """,
            (int(row["id"]),),
        )
    else:
        db.execute(
            """
            INSERT INTO knowledge_entities(entity_name, entity_type)
            VALUES (?, ?)
            """,
            (entity_name, entity_type),
        )
    db.commit()
    db.close()


def list_entities(limit: int = 30) -> list[sqlite3.Row]:
    db = get_db()
    rows = db.execute(
        """
        SELECT * FROM knowledge_entities
        ORDER BY mention_count DESC, last_seen_ts DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    db.close()
    return rows


def curator_checkpoint(stream_name: str = "event_bus") -> int:
    db = get_db()
    row = db.execute(
        """
        SELECT last_event_id FROM memory_curator_checkpoint
        WHERE stream_name = ?
        """,
        (stream_name,),
    ).fetchone()
    db.close()
    return int(row["last_event_id"]) if row else 0


def update_curator_checkpoint(event_id: int, stream_name: str = "event_bus") -> None:
    db = get_db()
    db.execute(
        """
        INSERT INTO memory_curator_checkpoint(stream_name, last_event_id)
        VALUES (?, ?)
        ON CONFLICT(stream_name) DO UPDATE SET
            last_event_id = excluded.last_event_id
        """,
        (stream_name, event_id),
    )
    db.commit()
    db.close()


def events_since(event_id: int, limit: int = 100) -> list[sqlite3.Row]:
    db = get_db()
    rows = db.execute(
        """
        SELECT * FROM event_bus
        WHERE id > ?
        ORDER BY id ASC
        LIMIT ?
        """,
        (event_id, limit),
    ).fetchall()
    db.close()
    return rows


def fetch_pending_events(limit: int = 20) -> list[sqlite3.Row]:
    db = get_db()
    rows = db.execute(
        """
        SELECT * FROM event_bus
        WHERE status = 'new'
        ORDER BY id ASC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    db.close()
    return rows


def mark_event_done(event_id: int) -> None:
    db = get_db()
    db.execute("UPDATE event_bus SET status = 'done' WHERE id = ?", (event_id,))
    db.commit()
    db.close()


def command_allowed(command: str) -> tuple[bool, str]:
    policy = load_policy()
    for pattern in policy.get("blocked_patterns", []):
        if pattern in command:
            return False, f"Blocked by policy pattern: {pattern}"

    for allowed in policy.get("allowed_read_commands", []):
        if command == allowed or command.startswith(f"{allowed} "):
            return True, "Read command allowed"

    for allowed in policy.get("allowed_write_commands", []):
        if command == allowed or command.startswith(f"{allowed} "):
            return True, "Write command allowed"

    return False, "Command not in allow-list"


def command_allowed_for_source(source_name: str, command: str) -> tuple[bool, str]:
    policy = load_policy()
    for pattern in policy.get("blocked_patterns", []):
        if pattern in command:
            return False, f"Blocked by policy pattern: {pattern}"

    capability_profile = source_capability_profile(source_name)
    profiles = policy.get("capability_profiles", {})
    profile = profiles.get(capability_profile, {})
    allowed_prefixes = profile.get("allowed_prefixes", [])

    for allowed in allowed_prefixes:
        if command == allowed or command.startswith(f"{allowed} "):
            return True, f"Allowed by capability profile: {capability_profile}"

    return False, f"Command not allowed for source profile: {capability_profile}"


def confirmation_required(command: str) -> bool:
    policy = load_policy()
    items = policy.get("require_confirmation_for", [])
    return any(command == item or command.startswith(f"{item} ") for item in items)


def run_command(command: str) -> tuple[int, str]:
    proc = subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True,
        timeout=120,
    )
    output = (proc.stdout + "\n" + proc.stderr).strip()
    return proc.returncode, output


def chroma_client() -> chromadb.PersistentClient:
    cfg = load_config()
    cfg.chroma_path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(cfg.chroma_path))


def simple_embedding(text: str, dimensions: int = 32) -> list[float]:
    vector = [0.0] * dimensions
    for index, byte in enumerate(text.encode("utf-8")):
        vector[index % dimensions] += float(byte) / 255.0
    return vector


def index_memory_document(doc_id: str, text: str, metadata: dict[str, Any]) -> None:
    client = chroma_client()
    collection = client.get_or_create_collection("aether_memory")
    collection.upsert(
        ids=[doc_id],
        documents=[text],
        embeddings=[simple_embedding(text)],
        metadatas=[metadata],
    )


def timestamp_id(prefix: str) -> str:
    return f"{prefix}-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"


def memory_graph_path() -> Path:
    cfg = load_config()
    default_path = str(AETHER_ROOT / "data" / "graph" / "memory_graph.json")
    graph_file = cfg.memory.get("graph_file", default_path)
    path = Path(graph_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def load_memory_graph() -> dict[str, Any]:
    path = memory_graph_path()
    if not path.exists():
        return {"nodes": [], "edges": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_memory_graph(graph: dict[str, Any]) -> None:
    path = memory_graph_path()
    path.write_text(json.dumps(graph, indent=2), encoding="utf-8")


def upsert_graph_entity(entity_name: str, entity_type: str = "unknown") -> None:
    graph = load_memory_graph()
    nodes = graph.setdefault("nodes", [])
    if not any(node.get("id") == entity_name for node in nodes):
        nodes.append({"id": entity_name, "type": entity_type})
        save_memory_graph(graph)


def upsert_graph_edge(source: str, target: str, relation: str) -> None:
    graph = load_memory_graph()
    edges = graph.setdefault("edges", [])
    if not any(
        edge.get("source") == source
        and edge.get("target") == target
        and edge.get("relation") == relation
        for edge in edges
    ):
        edges.append({"source": source, "target": target, "relation": relation})
        save_memory_graph(graph)


def systemctl_is_active(unit_name: str) -> bool:
    proc = subprocess.run(
        ["systemctl", "is-active", unit_name],
        text=True,
        capture_output=True,
        timeout=30,
    )
    return proc.returncode == 0 and proc.stdout.strip() == "active"


def systemctl_restart(unit_name: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["systemctl", "restart", unit_name],
        text=True,
        capture_output=True,
        timeout=60,
    )
    output = (proc.stdout + "\n" + proc.stderr).strip()
    return proc.returncode, output


def create_meta_job(name: str, role: str, prompt: str, image_name: str, notes: str = "") -> int:
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO meta_agent_jobs(name, role, prompt, status, image_name, notes)
        VALUES (?, ?, ?, 'queued', ?, ?)
        """,
        (name, role, prompt, image_name, notes),
    )
    db.commit()
    job_id = int(cursor.lastrowid)
    db.close()
    return job_id


def fetch_meta_jobs(status: str | None = None, limit: int = 20) -> list[sqlite3.Row]:
    db = get_db()
    if status is None:
        rows = db.execute(
            """
            SELECT * FROM meta_agent_jobs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    else:
        rows = db.execute(
            """
            SELECT * FROM meta_agent_jobs
            WHERE status = ?
            ORDER BY id ASC
            LIMIT ?
            """,
            (status, limit),
        ).fetchall()
    db.close()
    return rows


def fetch_meta_job(job_id: int) -> sqlite3.Row | None:
    db = get_db()
    row = db.execute(
        """
        SELECT * FROM meta_agent_jobs
        WHERE id = ?
        """,
        (job_id,),
    ).fetchone()
    db.close()
    return row


def update_meta_job(
    job_id: int,
    status: str,
    container_name: str = "",
    output_path: str = "",
    notes: str = "",
) -> None:
    db = get_db()
    db.execute(
        """
        UPDATE meta_agent_jobs
        SET status = ?,
            container_name = CASE WHEN ? = '' THEN container_name ELSE ? END,
            output_path = CASE WHEN ? = '' THEN output_path ELSE ? END,
            notes = CASE WHEN ? = '' THEN notes ELSE ? END
        WHERE id = ?
        """,
        (status, container_name, container_name, output_path, output_path, notes, notes, job_id),
    )
    db.commit()
    db.close()


def ollama_generate(prompt: str) -> str:
    cfg = load_config()
    response = requests.post(
        f"{cfg.ollama_host}/api/generate",
        json={
            "model": cfg.primary_model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=180,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()


def sleep_loop(seconds: int) -> None:
    time.sleep(seconds)


def record_system_event(source: str, level: str, message: str) -> None:
    db = get_db()
    db.execute(
        """
        INSERT INTO system_events(source, level, message)
        VALUES (?, ?, ?)
        """,
        (source, level, message),
    )
    db.commit()
    db.close()
