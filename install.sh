#!/usr/bin/env bash
# MIT License

set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${EUID}" -ne 0 ]]; then
  echo "[ERROR] Run as root"
  exit 1
fi

bash "${PROJECT_ROOT}/bootstrap/prepare-base.sh"
bash "${PROJECT_ROOT}/bootstrap/firstboot.sh"

echo "[INFO] AetherOS install completed from ${PROJECT_ROOT}"
