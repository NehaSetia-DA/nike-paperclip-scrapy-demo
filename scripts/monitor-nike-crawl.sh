#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_ID="${RUN_ID:-$(date -u +"%Y%m%dT%H%M%SZ")}"
ITEM_LIMIT="${ITEM_LIMIT:-10}"
OUT_DIR="$ROOT/outputs/nike/runs/$RUN_ID"
LATEST_DIR="$ROOT/outputs/nike/latest"
REPORTS_DIR="$ROOT/reports/nike"
REPORT="$OUT_DIR/health.json"
RUN_COMMAND_LOG="$OUT_DIR/run-command.log"

mkdir -p "$OUT_DIR" "$LATEST_DIR" "$REPORTS_DIR"

echo "== Nike run mode =="
echo "run_id=$RUN_ID"
echo "item_limit=$ITEM_LIMIT"
echo

set +e
RUN_ID="$RUN_ID" ITEM_LIMIT="$ITEM_LIMIT" "$ROOT/scripts/run-nike-crawl.sh" > "$RUN_COMMAND_LOG" 2>&1
CRAWL_STATUS=$?
set -e

cat "$RUN_COMMAND_LOG"
OUTPUT="$OUT_DIR/products.jsonl"
LOG="$OUT_DIR/crawl.log"

set +e
python3 "$ROOT/scripts/monitor_nike_crawl.py" \
  --items "$OUTPUT" \
  --log "$LOG" \
  --report "$REPORT" \
  --min-items "$ITEM_LIMIT"
REPORT_STATUS=$?
set -e

cp "$REPORT" "$LATEST_DIR/health.json"
cp "$REPORT" "$REPORTS_DIR/latest-health.json"

echo
echo "Nike crawl health report: $REPORT"

if [ "$CRAWL_STATUS" -ne 0 ]; then
  echo "Scrapy/Spidermon status: failed ($CRAWL_STATUS)" >&2
fi

if [ "$REPORT_STATUS" -ne 0 ]; then
  echo "Paperclip health report status: failed ($REPORT_STATUS)" >&2
fi

if [ "$CRAWL_STATUS" -ne 0 ]; then
  exit "$CRAWL_STATUS"
fi
exit "$REPORT_STATUS"
