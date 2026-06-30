#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT="$ROOT/nike_catalog"
LATEST="$ROOT/outputs/nike/latest"

if [ ! -d "$PROJECT" ]; then
  echo "Generated Scrapy project missing: $PROJECT"
  echo "Run ./scripts/run-zyte-skill-pipeline.sh first."
  exit 1
fi

cd "$PROJECT"
uv run pytest fixtures/

cd "$ROOT"
"$ROOT/scripts/monitor-nike-crawl.sh"

python3 "$ROOT/scripts/check_sample_output.py" "$LATEST/products.jsonl"
