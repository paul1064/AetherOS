#!/usr/bin/env bash
# MIT License

set -euo pipefail

AETHER_ROOT="/home/miqua/Desktop/pcfAI"
AETHER_USER="${SUDO_USER:-miqua}"
VENV_PATH="${AETHER_ROOT}/.venv"

if [[ "${EUID}" -ne 0 ]]; then
  echo "[ERROR] Run as root"
  exit 1
fi

mkdir -p \
  "${AETHER_ROOT}/requirements" \
  "${AETHER_ROOT}/lib" \
  "${AETHER_ROOT}/agents/memory" \
  "${AETHER_ROOT}/agents/meta" \
  "${AETHER_ROOT}/containers/memory-service" \
  "${AETHER_ROOT}/containers/subagent-base" \
  "${AETHER_ROOT}/systemd" \
  "${AETHER_ROOT}/desktop/hypr" \
  "${AETHER_ROOT}/desktop/waybar" \
  "${AETHER_ROOT}/desktop/session" \
  "${AETHER_ROOT}/data/captures" \
  "${AETHER_ROOT}/data/voice" \
  "${AETHER_ROOT}/data/meta/jobs" \
  "${AETHER_ROOT}/data/meta/runs" \
  "${AETHER_ROOT}/data/reports"

python3 -m venv "${VENV_PATH}"
"${VENV_PATH}/bin/pip" install --upgrade pip setuptools wheel
"${VENV_PATH}/bin/pip" install -r "${AETHER_ROOT}/requirements/core.txt"

cp "${AETHER_ROOT}/systemd/"*.service /etc/systemd/system/
mkdir -p /usr/share/wayland-sessions
cp "${AETHER_ROOT}/desktop/session/aetheros.desktop" /usr/share/wayland-sessions/aetheros.desktop
systemctl daemon-reload
systemctl enable aether-bootstrap.service aether-supervisor.service aether-orchestrator.service aether-executor.service aether-vector-memory.service aether-memory-curator.service aether-selfheal.service aether-resource.service aether-api.service aether-meta.service aether-models.service aether-snapshot.timer
systemctl restart aether-bootstrap.service
systemctl restart aether-supervisor.service
systemctl restart aether-orchestrator.service
systemctl restart aether-executor.service
systemctl restart aether-vector-memory.service
systemctl restart aether-memory-curator.service
systemctl restart aether-selfheal.service
systemctl restart aether-resource.service
systemctl restart aether-api.service
systemctl restart aether-meta.service
systemctl restart aether-models.service
systemctl restart aether-snapshot.timer

chown -R "${AETHER_USER}:${AETHER_USER}" "${AETHER_ROOT}"

echo "[INFO] AetherOS runtime installed from ${AETHER_ROOT}."
