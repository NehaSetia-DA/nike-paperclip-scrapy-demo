#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT="$ROOT/nike_catalog"

if [ -f "$ROOT/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi

RUN_ID="${RUN_ID:-$(date -u +"%Y%m%dT%H%M%SZ")}"
ITEM_LIMIT="${ITEM_LIMIT:-10}"
NIKE_DEMO_BREAK_FIELD="${NIKE_DEMO_BREAK_FIELD:-}"
OUT_DIR="$ROOT/outputs/nike/runs/$RUN_ID"
OUTPUT="$OUT_DIR/products.jsonl"
LOG="$OUT_DIR/crawl.log"
LATEST_DIR="$ROOT/outputs/nike/latest"

if [ ! -d "$PROJECT" ]; then
  echo "Generated Scrapy project missing: $PROJECT" >&2
  echo "Run build mode first: ./scripts/run-zyte-skill-pipeline.sh" >&2
  exit 1
fi

if [ -z "${ZYTE_API_KEY:-}" ]; then
  echo "ZYTE_API_KEY is required to run the Nike crawl through Zyte API." >&2
  exit 1
fi

mkdir -p "$OUT_DIR" "$LATEST_DIR"

cd "$PROJECT"
SCRAPY_ARGS=(
  crawl nike
  -s CLOSESPIDER_ITEMCOUNT="$ITEM_LIMIT"
  -s NIKE_MIN_ITEMS="$ITEM_LIMIT"
  -L INFO
  -O "$OUTPUT"
)

if [ -n "$NIKE_DEMO_BREAK_FIELD" ]; then
  SCRAPY_ARGS+=(-s "NIKE_DEMO_BREAK_FIELD=$NIKE_DEMO_BREAK_FIELD")
fi

set +e
ZYTE_API_LOG_REQUESTS=True uv run scrapy "${SCRAPY_ARGS[@]}" 2>&1 | tee "$LOG"
CRAWL_STATUS=${PIPESTATUS[0]}
set -e

if [ -f "$OUTPUT" ]; then
  cp "$OUTPUT" "$LATEST_DIR/products.jsonl"
fi
cp "$LOG" "$LATEST_DIR/crawl.log"

printf "%s\n" "$RUN_ID" > "$LATEST_DIR/run-id.txt"
printf "%s\n" "$OUTPUT"
exit "$CRAWL_STATUS"
