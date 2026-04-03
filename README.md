MIT License

# AetherOS

Project root: repository root `AetherOS/`

This repository contains the current AetherOS bootstrap, runtime, API, self-healing, resource-intelligence, multimodal and installer files, all rooted at the GitHub repository root `AetherOS/`.

## Quick start

1. Review and run:
   `sudo bash bootstrap/prepare-base.sh`
2. Install the project runtime:
   `sudo bash bootstrap/firstboot.sh`
3. Install systemd units from the project directory:
   `sudo cp systemd/*.service /etc/systemd/system/`
4. Reload and enable services:
   `sudo systemctl daemon-reload`
   `sudo systemctl enable aether-bootstrap.service aether-supervisor.service aether-orchestrator.service aether-executor.service aether-vector-memory.service aether-selfheal.service aether-resource.service aether-api.service`
   `sudo systemctl restart aether-bootstrap.service aether-supervisor.service aether-orchestrator.service aether-executor.service aether-vector-memory.service aether-selfheal.service aether-resource.service aether-api.service`
5. Optional full-machine install workflow:
   `sudo bash install/install-aetheros.sh --root-mount /mnt/aether-target`
6. Optional operator console:
   `bin/aether-operator`
7. Governance inspection:
   `bin/aether-governance --profiles`
8. Smoke verification:
   `bin/aether-verify`
9. Report export:
   `bin/aether-report`
10. Model registry:
   `bin/aether-models --list`
11. Start full stack:
   `sudo bin/aether-up`
12. Recover stack:
   `sudo bin/aether-recover`
13. One-command install:
   `sudo bash install.sh`
14. Release export:
   `bash install/export-release.sh`
15. Unified CLI:
   `bin/aether status`
16. Create local env file:
   `bin/aether env`

## Layout

- `bootstrap/`: base provisioning and runtime install
- `bin/`: host-side executables
- `config/`: YAML configuration
- `lib/`: shared Python runtime library
- `systemd/`: unit files to copy into `/etc/systemd/system/`
- `containers/`: container build definitions
- `agents/`: Python agent implementations
- `requirements/`: Python dependency manifests
- `desktop/`: Hyprland and Waybar configuration
- `install/`: disk layout, snapshots and one-command installer
- `bin/aether-operator`: terminal operator console for status, proposals and meta-jobs
- `bin/aether-governance`: governance profiles and audit inspection
- `bin/aether-verify`: smoke verification for services, API and key files
- `bin/aether-report`: JSON diagnostic export bundle
- `config/models.yaml`: local model registry and pull policy
- `bin/aether-models`: local model manager for Ollama roles and pulls
- `bin/aether`: unified control CLI
- `bin/aether-env`: create a local `.env` from `.env.example`
- `docs/ARCHITECTURE.md`: current architecture overview
- `docs/RUNBOOK.md`: install and operations runbook
- `docs/DEPLOYMENT_CHECKLIST.md`: deployment and validation checklist
- `PROJECT_INDEX.md`: project entrypoint index
- `bin/aether-up` / `bin/aether-down`: start and stop the full AetherOS stack
- `bin/aether-recover`: restart and export a recovery report
- `desktop/session/aetheros.desktop`: installable Wayland session entry
- `install.sh`: one-command local installer
- `VERSION`: release version marker
- `RELEASE_MANIFEST.json`: release entrypoint manifest
