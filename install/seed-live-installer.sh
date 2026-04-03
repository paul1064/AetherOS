#!/usr/bin/env bash
# MIT License

set -euo pipefail

PROJECT_ROOT="/home/miqua/Desktop/pcfAI"

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
