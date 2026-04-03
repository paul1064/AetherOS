# AetherOS Project Index

## Core entrypoints

- `install.sh`: one-command local install
- `bin/aether`: unified CLI
- `bin/aether-up`: start full stack
- `bin/aether-down`: stop full stack
- `bin/aether-recover`: recover and export report
- `bin/aether-status`: local state summary
- `bin/aether-operator`: TUI operator console

## Runtime services

- `systemd/aether-bootstrap.service`
- `systemd/aether-supervisor.service`
- `systemd/aether-orchestrator.service`
- `systemd/aether-executor.service`
- `systemd/aether-vector-memory.service`
- `systemd/aether-memory-curator.service`
- `systemd/aether-selfheal.service`
- `systemd/aether-resource.service`
- `systemd/aether-api.service`
- `systemd/aether-meta.service`
- `systemd/aether-models.service`

## Important configs

- `config/aether.yaml`
- `config/policy.yaml`
- `config/models.yaml`
- `desktop/hypr/hyprland.conf`
- `desktop/session/aetheros.desktop`

## Installer flow

1. `bootstrap/prepare-base.sh`
2. `bootstrap/firstboot.sh`
3. `install/install-aetheros.sh`
4. `install/install-desktop-session.sh`

## Operations

- Health: `bin/aether verify`
- Report: `bin/aether report`
- Models: `bin/aether models --list`
- Governance: `bin/aether governance --profiles`
- Memory: `bin/aether memory --entities`
