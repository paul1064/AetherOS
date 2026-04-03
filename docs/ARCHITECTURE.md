# AetherOS Architecture

```mermaid
flowchart TD
    U[User] --> OP[Operator Console / API / NL Shell]
    OP --> ORCH[Orchestrator]
    OP --> GOV[Governance]
    ORCH --> EXE[Executor]
    ORCH --> META[Meta Agent]
    ORCH --> MEM[Memory Curator + Vector Memory]
    ORCH --> OLLAMA[Ollama Local Models]

    EXE --> HOST[Host Commands]
    META --> POD[Rootless Podman Subagents]
    MEM --> SQL[SQLite]
    MEM --> CHROMA[ChromaDB]
    MEM --> GRAPH[Knowledge Graph JSON]

    HOST --> SYS[systemd / journals / Btrfs / Wayland]
    GOV --> AUDIT[Audit Log + Capability Profiles]
    SYS --> HEAL[Self-Heal Agent]
    SYS --> RES[Resource Agent]
    HEAL --> ORCH
    RES --> ORCH
```

## Layers

- Host layer: `systemd`, Ollama, Podman, Btrfs, Hyprland
- Control layer: orchestrator, executor, governance, self-heal, resource, API
- Memory layer: SQLite, Chroma, JSON graph, curator
- Meta layer: subagent job queue plus Podman subagent containers
- Interface layer: operator console, status CLI, API, shell, Wayland session

## Primary entrypoints

- `install.sh`
- `bin/aether`
- `bin/aether-up`
- `bin/aether-status`
- `bin/aether-operator`
