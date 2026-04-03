#!/usr/bin/env bash
# MIT License

set -euo pipefail

PROJECT_ROOT="/home/miqua/Desktop/pcfAI"

echo "[INFO] Running AetherOS smoke verification"
"${PROJECT_ROOT}/bin/aether-verify"

echo "[INFO] Exporting diagnostic report"
"${PROJECT_ROOT}/bin/aether-report"
