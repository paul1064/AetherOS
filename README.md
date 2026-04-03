MIT License

# AetherOS (made with ChatGPT Codex)

Project root: `/home/miqua/Desktop/pcfAI`

This repository contains the current AetherOS bootstrap, runtime, API, self-healing, resource-intelligence, multimodal and installer files, all rooted at `/home/miqua/Desktop/pcfAI`.

## Quick start

1. Review and run:
   `sudo bash /home/miqua/Desktop/pcfAI/bootstrap/prepare-base.sh`
2. Install the project runtime:
   `sudo bash /home/miqua/Desktop/pcfAI/bootstrap/firstboot.sh`
3. Install systemd units from the project directory:
   `sudo cp /home/miqua/Desktop/pcfAI/systemd/*.service /etc/systemd/system/`
4. Reload and enable services:
   `sudo systemctl daemon-reload`
   `sudo systemctl enable aether-bootstrap.service aether-supervisor.service aether-orchestrator.service aether-executor.service aether-vector-memory.service aether-selfheal.service aether-resource.service aether-api.service`
   `sudo systemctl restart aether-bootstrap.service aether-supervisor.service aether-orchestrator.service aether-executor.service aether-vector-memory.service aether-selfheal.service aether-resource.service aether-api.service`
5. Optional full-machine install workflow:
   `sudo bash /home/miqua/Desktop/pcfAI/install/install-aetheros.sh --root-mount /mnt/aether-target`
6. Optional operator console:
   `/home/miqua/Desktop/pcfAI/bin/aether-operator`
7. Governance inspection:
   `/home/miqua/Desktop/pcfAI/bin/aether-governance --profiles`
8. Smoke verification:
   `/home/miqua/Desktop/pcfAI/bin/aether-verify`
9. Report export:
   `/home/miqua/Desktop/pcfAI/bin/aether-report`
10. Model registry:
   `/home/miqua/Desktop/pcfAI/bin/aether-models --list`
11. Start full stack:
   `sudo /home/miqua/Desktop/pcfAI/bin/aether-up`
12. Recover stack:
   `sudo /home/miqua/Desktop/pcfAI/bin/aether-recover`
13. One-command install:
   `sudo bash /home/miqua/Desktop/pcfAI/install.sh`
14. Release export:
   `bash /home/miqua/Desktop/pcfAI/install/export-release.sh`
15. Unified CLI:
   `/home/miqua/Desktop/pcfAI/bin/aether status`
16. Create local env file:
   `/home/miqua/Desktop/pcfAI/bin/aether env`

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
