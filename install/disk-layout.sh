#!/usr/bin/env bash
# MIT License

set -euo pipefail

TARGET_DISK=""
BOOT_PART_SIZE_MIB="${BOOT_PART_SIZE_MIB:-1024}"
SWAP_SIZE_GIB="${SWAP_SIZE_GIB:-8}"

usage() {
  cat <<'EOF'
usage: disk-layout.sh --disk /dev/nvme0n1

Creates a GPT disk layout suitable for AetherOS:
- EFI system partition
- swap partition
- Btrfs root partition
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --disk)
      TARGET_DISK="$2"
      shift 2
      ;;
    *)
      usage
      exit 1
      ;;
  esac
done

if [[ -z "${TARGET_DISK}" ]]; then
  usage
  exit 1
fi

if [[ ! -b "${TARGET_DISK}" ]]; then
  echo "[ERROR] Disk not found: ${TARGET_DISK}"
  exit 1
fi

echo "[INFO] Partitioning ${TARGET_DISK}"
parted -s "${TARGET_DISK}" mklabel gpt
parted -s "${TARGET_DISK}" mkpart ESP fat32 1MiB "${BOOT_PART_SIZE_MIB}MiB"
parted -s "${TARGET_DISK}" set 1 esp on
parted -s "${TARGET_DISK}" mkpart swap linux-swap "${BOOT_PART_SIZE_MIB}MiB" "$((BOOT_PART_SIZE_MIB + SWAP_SIZE_GIB * 1024))MiB"
parted -s "${TARGET_DISK}" mkpart root btrfs "$((BOOT_PART_SIZE_MIB + SWAP_SIZE_GIB * 1024))MiB" 100%

if [[ "${TARGET_DISK}" =~ nvme ]]; then
  BOOT_PART="${TARGET_DISK}p1"
  SWAP_PART="${TARGET_DISK}p2"
  ROOT_PART="${TARGET_DISK}p3"
else
  BOOT_PART="${TARGET_DISK}1"
  SWAP_PART="${TARGET_DISK}2"
  ROOT_PART="${TARGET_DISK}3"
fi

mkfs.vfat -F 32 "${BOOT_PART}"
mkswap "${SWAP_PART}"
swapon "${SWAP_PART}"
mkfs.btrfs -f "${ROOT_PART}"

echo "[INFO] Layout complete"
echo "BOOT_PART=${BOOT_PART}"
echo "SWAP_PART=${SWAP_PART}"
echo "ROOT_PART=${ROOT_PART}"
