#!/usr/bin/env bash
# MIT License

set -euo pipefail

TARGET_ROOT="${1:-/}"
SNAPSHOT_DIR="${2:-/.snapshots}"
LABEL="${3:-manual}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
SOURCE_SUBVOL="${TARGET_ROOT}"
DESTINATION="${SNAPSHOT_DIR}/${TIMESTAMP}-${LABEL}"

mkdir -p "${SNAPSHOT_DIR}"
btrfs subvolume snapshot -r "${SOURCE_SUBVOL}" "${DESTINATION}"
echo "${DESTINATION}"
