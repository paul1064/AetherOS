#!/usr/bin/env bash
# MIT License

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
TARGET_MOUNT=""
TARGET_DISK=""
TARGET_USER="${SUDO_USER:-miqua}"
DO_PARTITION="false"

usage() {
  cat <<'EOF'
usage: install-aetheros.sh --root-mount /mnt/aether-target [--disk /dev/nvme0n1] [--partition]

Modes:
- existing mounted target root: provide --root-mount only
- fresh disk install skeleton: provide --disk and --partition
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root-mount)
      TARGET_MOUNT="$2"
      shift 2
      ;;
    --disk)
      TARGET_DISK="$2"
      shift 2
      ;;
    --partition)
      DO_PARTITION="true"
      shift 1
      ;;
    --user)
      TARGET_USER="$2"
      shift 2
      ;;
    *)
      usage
      exit 1
      ;;
  esac
done

if [[ -z "${TARGET_MOUNT}" ]]; then
  usage
  exit 1
fi

if [[ "${EUID}" -ne 0 ]]; then
  echo "[ERROR] Run as root"
  exit 1
fi

if [[ "${DO_PARTITION}" == "true" ]]; then
  if [[ -z "${TARGET_DISK}" ]]; then
    echo "[ERROR] --partition requires --disk"
    exit 1
  fi

  bash "${PROJECT_ROOT}/install/disk-layout.sh" --disk "${TARGET_DISK}"

  if [[ "${TARGET_DISK}" =~ nvme ]]; then
    ROOT_PART="${TARGET_DISK}p3"
  else
    ROOT_PART="${TARGET_DISK}3"
  fi

  bash "${PROJECT_ROOT}/install/btrfs-layout.sh" --root-part "${ROOT_PART}" --mount "${TARGET_MOUNT}"
fi

mkdir -p "${TARGET_MOUNT}/home/${TARGET_USER}/Desktop"
rsync -a --delete \
  --exclude '.venv' \
  --exclude 'runtime/logs/*' \
  "${PROJECT_ROOT}/" \
  "${TARGET_MOUNT}/home/${TARGET_USER}/Desktop/AetherOS/"

chroot "${TARGET_MOUNT}" /bin/bash -lc "chown -R ${TARGET_USER}:${TARGET_USER} /home/${TARGET_USER}/Desktop/AetherOS"

cat > "${TARGET_MOUNT}/home/${TARGET_USER}/Desktop/AetherOS/install/POST_INSTALL.txt" <<EOF
AetherOS project copied successfully.

Next steps inside the target system:
1. sudo bash /home/${TARGET_USER}/Desktop/AetherOS/bootstrap/prepare-base.sh
2. sudo bash /home/${TARGET_USER}/Desktop/AetherOS/bootstrap/firstboot.sh
3. sudo cp /home/${TARGET_USER}/Desktop/AetherOS/systemd/*.service /etc/systemd/system/
4. sudo systemctl daemon-reload
5. sudo systemctl enable aether-bootstrap.service aether-supervisor.service aether-orchestrator.service aether-executor.service aether-vector-memory.service aether-selfheal.service aether-resource.service aether-api.service
6. sudo systemctl restart aether-bootstrap.service aether-supervisor.service aether-orchestrator.service aether-executor.service aether-vector-memory.service aether-selfheal.service aether-resource.service aether-api.service
EOF

echo "[INFO] AetherOS payload copied to ${TARGET_MOUNT}/home/${TARGET_USER}/Desktop/AetherOS"
echo "[INFO] Post-install instructions written to install/POST_INSTALL.txt"
