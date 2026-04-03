#!/usr/bin/env bash
# MIT License

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
AETHER_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
AETHER_USER="${SUDO_USER:-miqua}"
AETHER_GROUP="${AETHER_USER}"
LOG_FILE="/var/log/aetheros-bootstrap.log"

exec > >(tee -a "${LOG_FILE}") 2>&1

require_root() {
  if [[ "${EUID}" -ne 0 ]]; then
    echo "[ERROR] Run this script as root."
    exit 1
  fi
}

detect_os() {
  if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS_ID="${ID}"
    OS_VERSION="${VERSION_ID}"
  else
    echo "[ERROR] Cannot detect operating system."
    exit 1
  fi

  case "${OS_ID}" in
    ubuntu|debian)
      echo "[INFO] Detected supported OS: ${OS_ID} ${OS_VERSION}"
      ;;
    *)
      echo "[ERROR] Unsupported OS: ${OS_ID}"
      exit 1
      ;;
  esac
}

install_packages() {
  export DEBIAN_FRONTEND=noninteractive

  apt-get update
  apt-get install -y \
    curl wget git jq sqlite3 btrfs-progs acl \
    podman uidmap slirp4netns fuse-overlayfs \
    python3 python3-venv python3-pip \
    build-essential pkg-config \
    rustc cargo \
    systemd-container dbus-user-session \
    pipewire wireplumber wl-clipboard \
    hyprland waybar foot fuzzel \
    network-manager avahi-daemon \
    smartmontools lm-sensors \
    rsync unzip tar

  systemctl enable NetworkManager
  systemctl enable avahi-daemon
}

create_user_mappings() {
  if ! id -u "${AETHER_USER}" >/dev/null 2>&1; then
    echo "[ERROR] User ${AETHER_USER} does not exist."
    exit 1
  fi

  usermod -aG sudo,video,audio,render,netdev "${AETHER_USER}" || true

  if ! grep -q "^${AETHER_USER}:" /etc/subuid; then
    echo "${AETHER_USER}:100000:65536" >> /etc/subuid
  fi

  if ! grep -q "^${AETHER_USER}:" /etc/subgid; then
    echo "${AETHER_USER}:100000:65536" >> /etc/subgid
  fi
}

install_ollama() {
  if command -v ollama >/dev/null 2>&1; then
    echo "[INFO] Ollama already installed."
    return
  fi

  curl -fsSL https://ollama.com/install.sh | sh
  systemctl enable ollama
  systemctl start ollama
}

prepare_directories() {
  mkdir -p \
    "${AETHER_ROOT}/bootstrap" \
    "${AETHER_ROOT}/config" \
    "${AETHER_ROOT}/bin" \
    "${AETHER_ROOT}/lib" \
    "${AETHER_ROOT}/requirements" \
    "${AETHER_ROOT}/runtime/sockets" \
    "${AETHER_ROOT}/runtime/state" \
    "${AETHER_ROOT}/runtime/locks" \
    "${AETHER_ROOT}/runtime/logs" \
    "${AETHER_ROOT}/data/sqlite" \
    "${AETHER_ROOT}/data/chroma" \
    "${AETHER_ROOT}/data/graph" \
    "${AETHER_ROOT}/data/models" \
    "${AETHER_ROOT}/data/snapshots" \
    "${AETHER_ROOT}/agents/memory" \
    "${AETHER_ROOT}/containers/memory-service" \
    "${AETHER_ROOT}/systemd" \
    "${AETHER_ROOT}/install" \
    "${AETHER_ROOT}/desktop/hypr" \
    "${AETHER_ROOT}/desktop/waybar"

  chown -R "${AETHER_USER}:${AETHER_GROUP}" "${AETHER_ROOT}"
  chmod -R 0755 "${AETHER_ROOT}"
}

write_sysctl() {
  cat >/etc/sysctl.d/99-aetheros.conf <<'EOF'
vm.swappiness=10
fs.inotify.max_user_instances=8192
fs.inotify.max_user_watches=1048576
kernel.unprivileged_userns_clone=1
EOF
  sysctl --system
}

enable_linger() {
  loginctl enable-linger "${AETHER_USER}"
}

seed_models() {
  if systemctl is-active --quiet ollama; then
    echo "[INFO] Seeding configured models. This may take time."
    if [[ -x "${AETHER_ROOT}/bin/aether-models" && -f "${AETHER_ROOT}/config/models.yaml" ]]; then
      sudo -u "${AETHER_USER}" "${AETHER_ROOT}/bin/aether-models" --seed-defaults || true
    else
      sudo -u "${AETHER_USER}" ollama pull qwen3-coder || true
    fi
  else
    echo "[WARN] Ollama is not active yet. Model pull skipped."
  fi
}

main() {
  require_root
  detect_os
  install_packages
  create_user_mappings
  install_ollama
  prepare_directories
  write_sysctl
  enable_linger
  seed_models

  echo "[INFO] Base preparation complete for ${AETHER_ROOT}."
}

main "$@"
