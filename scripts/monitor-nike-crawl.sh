#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_ID="${RUN_ID:-$(date -u +"%Y%m%dT%H%M%SZ")}"
ITEM_LIMIT="${ITEM_LIMIT:-10}"
OUT_DIR="$ROOT/outputs/nike/runs/$RUN_ID"
LATEST_DIR="$ROOT/outputs/nike/latest"
REPORTS_DIR="$ROOT/reports/nike"
REPORT="$OUT_DIR/health.json"

mkdir -p "$OUT_DIR" "$LATEST_DIR" "$REPORTS_DIR"

echo "== Nike run mode =="
echo "run_id=$RUN_ID"
echo "item_limit=$ITEM_LIMIT"
echo

OUTPUT="$(RUN_ID="$RUN_ID" ITEM_LIMIT="$ITEM_LIMIT" "$ROOT/scripts/run-nike-crawl.sh" | tail -n 1)"
LOG="$OUT_DIR/crawl.log"

python3 "$ROOT/scripts/monitor_nike_crawl.py" \
  --items "$OUTPUT" \
  --log "$LOG" \
  --report "$REPORT" \
  --min-items "$ITEM_LIMIT"

cp "$REPORT" "$LATEST_DIR/health.json"
cp "$REPORT" "$REPORTS_DIR/latest-health.json"

echo
echo "Nike crawl health report: $REPORT"
