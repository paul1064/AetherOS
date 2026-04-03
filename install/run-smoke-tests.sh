#!/usr/bin/env bash
# MIT License

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

echo "[INFO] Running AetherOS smoke verification"
"${PROJECT_ROOT}/bin/aether-verify"

echo "[INFO] Exporting diagnostic report"
"${PROJECT_ROOT}/bin/aether-report"
