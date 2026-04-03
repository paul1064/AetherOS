#!/usr/bin/env bash
# MIT License

set -euo pipefail

PROJECT_ROOT="/home/miqua/Desktop/pcfAI"

if [[ "${EUID}" -ne 0 ]]; then
  echo "[ERROR] Run as root"
  exit 1
fi

mkdir -p /usr/share/wayland-sessions
cp "${PROJECT_ROOT}/desktop/session/aetheros.desktop" /usr/share/wayland-sessions/aetheros.desktop
chmod 0644 /usr/share/wayland-sessions/aetheros.desktop

echo "[INFO] Installed AetherOS Wayland session entry"
