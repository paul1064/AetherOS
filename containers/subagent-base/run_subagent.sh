#!/usr/bin/env bash
# MIT License

set -euo pipefail

INPUT_FILE="${1:-}"
OUTPUT_FILE="${2:-}"

if [[ -z "${INPUT_FILE}" || -z "${OUTPUT_FILE}" ]]; then
  echo '{"status":"failed","reason":"usage: run_subagent.sh <input> <output>"}'
  exit 1
fi

JOB_ID="$(jq -r '.job_id' "${INPUT_FILE}")"
NAME="$(jq -r '.name' "${INPUT_FILE}")"
ROLE="$(jq -r '.role' "${INPUT_FILE}")"
PROMPT="$(jq -r '.prompt' "${INPUT_FILE}")"

cat > "${OUTPUT_FILE}" <<EOF
{
  "job_id": ${JOB_ID},
  "name": "${NAME}",
  "role": "${ROLE}",
  "status": "completed",
  "summary": "Subagent scaffold executed",
  "prompt": $(jq -Rs . <<<"${PROMPT}"),
  "result": "This is the base subagent container result placeholder."
}
EOF
