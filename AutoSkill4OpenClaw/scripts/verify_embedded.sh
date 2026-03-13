#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADAPTER_DIR="$(cd "${SCRIPT_DIR}/../adapter" && pwd)"

echo "[verify-embedded] adapter_dir=${ADAPTER_DIR}"
cd "${ADAPTER_DIR}"

if [[ ! -d node_modules ]]; then
  echo "[verify-embedded] node_modules missing, installing deps..."
  npm install
fi

echo "[verify-embedded] running embedded runtime tests..."
node --test ./embedded_runtime.test.mjs

echo "[verify-embedded] running adapter integration tests..."
node --test ./index.test.mjs

echo "[verify-embedded] done"
