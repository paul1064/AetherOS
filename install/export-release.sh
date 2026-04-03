#!/usr/bin/env bash
# MIT License

set -euo pipefail

PROJECT_ROOT="/home/miqua/Desktop/pcfAI"
OUTPUT_DIR="${1:-${PROJECT_ROOT}/dist}"
VERSION="$(cat "${PROJECT_ROOT}/VERSION")"
ARCHIVE_NAME="aetheros-${VERSION}.tar.gz"

mkdir -p "${OUTPUT_DIR}"

tar \
  --exclude=".venv" \
  --exclude="data/reports/*" \
  --exclude="runtime/logs/*" \
  -czf "${OUTPUT_DIR}/${ARCHIVE_NAME}" \
  -C "${PROJECT_ROOT}" \
  .

cat > "${OUTPUT_DIR}/SHA256SUMS" <<EOF
$(sha256sum "${OUTPUT_DIR}/${ARCHIVE_NAME}")
EOF

echo "${OUTPUT_DIR}/${ARCHIVE_NAME}"
