#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PAPERCLIP_HOME="${PAPERCLIP_HOME:-$ROOT/.paperclip}"
export PAPERCLIP_INSTANCE_ID="${PAPERCLIP_INSTANCE_ID:-nike-demo}"

echo "Starting Paperclip with:"
echo "  PAPERCLIP_HOME=$PAPERCLIP_HOME"
echo "  PAPERCLIP_INSTANCE_ID=$PAPERCLIP_INSTANCE_ID"
echo

npx paperclipai onboard --yes
