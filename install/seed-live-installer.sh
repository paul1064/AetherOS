#!/usr/bin/env bash
# MIT License

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

mkdir -p /usr/local/bin
cp "${PROJECT_ROOT}/install/install-aetheros.sh" /usr/local/bin/aetheros-install
chmod +x /usr/local/bin/aetheros-install

cat <<'EOF'
AetherOS live installer seeded.
Run:
  sudo aetheros-install --root-mount /mnt/aether-target
or
  sudo aetheros-install --disk /dev/nvme0n1 --partition --root-mount /mnt/aether-target
EOF
