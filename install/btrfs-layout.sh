#!/usr/bin/env bash
# MIT License

set -euo pipefail

ROOT_PART=""
TARGET_MOUNT=""

usage() {
  cat <<'EOF'
usage: btrfs-layout.sh --root-part /dev/nvme0n1p3 --mount /mnt/aether-target
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root-part)
      ROOT_PART="$2"
      shift 2
      ;;
    --mount)
      TARGET_MOUNT="$2"
      shift 2
      ;;
    *)
      usage
      exit 1
      ;;
  esac
done

if [[ -z "${ROOT_PART}" || -z "${TARGET_MOUNT}" ]]; then
  usage
  exit 1
fi

mkdir -p "${TARGET_MOUNT}"
mount "${ROOT_PART}" "${TARGET_MOUNT}"

btrfs subvolume create "${TARGET_MOUNT}/@"
btrfs subvolume create "${TARGET_MOUNT}/@home"
btrfs subvolume create "${TARGET_MOUNT}/@var"
btrfs subvolume create "${TARGET_MOUNT}/@snapshots"

umount "${TARGET_MOUNT}"

mount -o subvol=@,compress=zstd,noatime "${ROOT_PART}" "${TARGET_MOUNT}"
mkdir -p "${TARGET_MOUNT}/home" "${TARGET_MOUNT}/var" "${TARGET_MOUNT}/.snapshots"
mount -o subvol=@home,compress=zstd,noatime "${ROOT_PART}" "${TARGET_MOUNT}/home"
mount -o subvol=@var,compress=zstd,noatime "${ROOT_PART}" "${TARGET_MOUNT}/var"
mount -o subvol=@snapshots,compress=zstd,noatime "${ROOT_PART}" "${TARGET_MOUNT}/.snapshots"

echo "[INFO] Btrfs subvolumes mounted under ${TARGET_MOUNT}"
