#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -z "${ZYTE_API_KEY:-}" ]; then
  echo "ZYTE_API_KEY is required. Run /scrape-zyte-login in Claude or export the key before continuing."
  exit 1
fi

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo "ANTHROPIC_API_KEY is required for Claude Code non-interactive generation."
  exit 1
fi

if ! claude plugin list | grep -q "zyte-web-data@zyte-ai"; then
  echo "Zyte Web Data plugin is not installed. Run ./scripts/install-zyte-plugin.sh"
  exit 1
fi

cd "$ROOT"
claude -p "$(cat "$ROOT/prompts/zyte-skill-pipeline.md")" \
  --permission-mode default \
  --add-dir "$ROOT"
