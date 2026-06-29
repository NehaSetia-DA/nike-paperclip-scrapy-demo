#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT="$ROOT/nike_catalog"
OUTPUT="$ROOT/outputs/nike-products-sample.jsonl"

if [ ! -d "$PROJECT" ]; then
  echo "Generated Scrapy project missing: $PROJECT"
  echo "Run ./scripts/run-zyte-skill-pipeline.sh first."
  exit 1
fi

cd "$PROJECT"
uv run pytest fixtures/

mkdir -p "$ROOT/outputs"
rm -f "$OUTPUT"
ZYTE_API_LOG_REQUESTS=True uv run scrapy crawl nike \
  -s CLOSESPIDER_ITEMCOUNT=10 \
  -O "$OUTPUT"

python3 "$ROOT/scripts/check_sample_output.py" "$OUTPUT"
