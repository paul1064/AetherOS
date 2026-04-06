# AetherOS

**An AI-Native Operating System Layer for Linux**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

AetherOS is an intelligent orchestration layer that transforms your Linux system into an AI-native operating environment. It provides autonomous agents, self-healing capabilities, semantic memory, and governance controls—accessible through a unified CLI, API, or terminal UI.

## 🌟 Key Features

- **🤖 Multi-Agent Architecture**: Orchestrator, Executor, Meta Agent, Memory Curator, Self-Heal, and Resource agents working in concert
- **🧠 Semantic Memory**: SQLite + ChromaDB + Knowledge Graph for persistent contextual awareness
- **🔒 Governance & Audit**: Capability-based profiles with comprehensive audit logging
- **♻️ Self-Healing**: Automatic detection and recovery from system anomalies
- **📊 Resource Intelligence**: Real-time monitoring and optimization recommendations
- **🎯 Local LLM Integration**: Native Ollama support for private, offline AI operations
- **🐳 Container Support**: Rootless Podman subagents for isolated task execution
- **🖥️ Wayland Desktop**: Hyprland integration with custom session management

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Interface Layer                          │
│  Operator Console (TUI) │ Unified CLI │ REST API │ Shell   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Control Layer                            │
│  Orchestrator │ Executor │ Meta Agent │ Governance         │
│  Self-Heal    │ Resource │ API Server                      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Memory Layer                             │
│  SQLite (structured) │ ChromaDB (vectors) │ JSON (graph)   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Host Layer                               │
│  systemd │ Ollama │ Podman │ Btrfs │ Hyprland │ Journal    │
└─────────────────────────────────────────────────────────────┘
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for detailed architecture documentation.

## 🚀 Quick Start

### One-Command Installation

```bash
# Full system installation (recommended)
sudo bash install.sh

# Or step-by-step installation
sudo bash bootstrap/prepare-base.sh
sudo bash bootstrap/firstboot.sh
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now aether-*.service
```

### Starting the Stack

```bash
# Start all services
sudo bin/aether up

# Check status
bin/aether status

# View operator console
bin/aether operator
```

### Essential Commands

| Command | Description |
|---------|-------------|
| `bin/aether status` | System health and service status |
| `bin/aether verify` | Smoke tests for services and API |
| `bin/aether report` | Export JSON diagnostic bundle |
| `bin/aether recover` | Restart stack and generate recovery report |
| `bin/aether models --list` | List available local LLM models |
| `bin/aether models --pull <model>` | Download a model via Ollama |
| `bin/aether governance --profiles` | Inspect capability profiles |
| `bin/aether memory --search "<query>"` | Semantic memory search |
| `bin/aether meta --submit --name <job>` | Submit meta-agent job |

## 📁 Project Structure

```
AetherOS/
├── bin/                    # Unified CLI and executables
├── lib/                    # Core Python runtime (aether_core.py)
├── agents/                 # Agent implementations
│   ├── orchestrator.py
│   ├── executor.py
│   ├── meta_agent.py
│   ├── memory_curator.py
│   ├── self_heal.py
│   └── resource_agent.py
├── config/                 # YAML configurations
│   ├── aether.yaml         # Main configuration
│   ├── policy.yaml         # Governance policies
│   └── models.yaml         # LLM model registry
├── systemd/                # Service unit files
├── bootstrap/              # Base provisioning scripts
├── install/                # Installer and deployment tools
├── containers/             # Podman container definitions
├── desktop/                # Hyprland/Waybar configurations
├── requirements/           # Python dependency manifests
└── docs/                   # Documentation
    ├── ARCHITECTURE.md
    ├── RUNBOOK.md
    └── DEPLOYMENT_CHECKLIST.md
```

## 🔧 Configuration

### Environment Setup

```bash
# Create local environment file
bin/aether env

# Edit configuration
nano config/aether.yaml
```

### Key Configuration Files

- **`config/aether.yaml`**: Core runtime settings, paths, and service parameters
- **`config/policy.yaml`**: Governance rules, capability profiles, and audit settings
- **`config/models.yaml`**: Ollama model registry with role assignments and pull policies

## 🛠️ Operations Runbook

For detailed operational procedures, see [`docs/RUNBOOK.md`](docs/RUNBOOK.md):

```bash
# Health checks
bin/aether verify

# Model management
bin/aether models --refresh
bin/aether models --pull qwen3-coder

# Memory operations
bin/aether memory --entities
bin/aether memory --graph

# Governance audit
bin/aether governance --audit
```

## 🔐 Governance & Security

AetherOS implements a capability-based governance model:

- **Audit Logging**: All actions logged with timestamps and context
- **Capability Profiles**: Define what agents can access and execute
- **Policy Enforcement**: Runtime validation against security policies

```bash
# Inspect active profiles
bin/aether governance --profiles

# Review audit log
bin/aether governance --audit
```

## 🧠 Memory System

AetherOS maintains three complementary memory stores:

1. **SQLite**: Structured facts, entities, and relationships
2. **ChromaDB**: Vector embeddings for semantic search
3. **Knowledge Graph**: JSON-based relationship mapping

```bash
# Search memory semantically
bin/aether memory --search "orchestrator failure recovery"

# List tracked entities
bin/aether memory --entities

# Export knowledge graph
bin/aether memory --graph
```

## 🤖 Meta-Agent System

Submit complex tasks to the meta-agent for decomposition into subagent jobs:

```bash
# Submit a meta-job
bin/aether meta --submit --name planner --role analysis \
  --prompt "Analyze system state and recommend optimizations"

# List pending/completed jobs
bin/aether meta --list
```

## 🖥️ Desktop Integration

AetherOS includes a custom Wayland session:

```bash
# Install desktop session
sudo bash install/install-desktop-session.sh

# Select "AetherOS" session at login screen
```

Configuration located in `desktop/hypr/` and `desktop/waybar/`.

## 📦 Deployment Options

### Full System Install
```bash
sudo bash install/install-aetheros.sh
```

### Targeted Installation
```bash
sudo bash install/install-aetheros.sh --root-mount /mnt/aether-target
```

### Container-Only Mode
```bash
# Build agent containers
cd containers && podman build -t aether-agent .
```

See [`docs/DEPLOYMENT_CHECKLIST.md`](docs/DEPLOYMENT_CHECKLIST.md) for production deployment guidance.

## 🔍 Verification & Diagnostics

```bash
# Comprehensive smoke test
bin/aether verify

# Export diagnostic bundle
bin/aether report > diagnostics.json

# Check individual services
systemctl status aether-orchestrator
journalctl -u aether-executor -f
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System architecture and component interactions |
| [`docs/RUNBOOK.md`](docs/RUNBOOK.md) | Operational procedures and troubleshooting |
| [`docs/DEPLOYMENT_CHECKLIST.md`](docs/DEPLOYMENT_CHECKLIST.md) | Production deployment validation |
| [`PROJECT_INDEX.md`](PROJECT_INDEX.md) | Complete entrypoint reference |

## 🧪 Development

```bash
# Install dependencies
pip install -r requirements/runtime.txt
pip install -r requirements/dev.txt

# Run linting
flake8 lib/ agents/ bin/

# Test imports
python -m py_compile lib/aether_core.py
```

## 📄 License

MIT License — See [`LICENSE`](LICENSE) for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📬 Support

- **Issues**: GitHub Issues tab
- **Documentation**: `docs/` directory
- **Quick Help**: `bin/aether --help`

---

**AetherOS** — Transforming Linux into an intelligent, self-managing operating environment.
