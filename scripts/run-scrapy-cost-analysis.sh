#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORTS_DIR="$ROOT/reports/nike"
LATEST_LOG="$ROOT/outputs/nike/latest/crawl.log"

mkdir -p "$REPORTS_DIR"

if [ -f "$LATEST_LOG" ]; then
  python3 "$ROOT/scripts/analyze_scrapy_cost.py" \
    "$ROOT/nike_catalog/nike_catalog/spiders/nike.py" \
    --settings "$ROOT/nike_catalog/nike_catalog/settings.py" \
    --log "$LATEST_LOG" \
    --sample-url "https://www.nike.com/id/t/academy-erling-haaland-football-ERATCGJV" \
    --json-report "$REPORTS_DIR/latest-cost-analysis.json" \
    --markdown-report "$REPORTS_DIR/latest-cost-analysis.md"
else
  python3 "$ROOT/scripts/analyze_scrapy_cost.py" \
    "$ROOT/nike_catalog/nike_catalog/spiders/nike.py" \
    --settings "$ROOT/nike_catalog/nike_catalog/settings.py" \
    --sample-url "https://www.nike.com/id/t/academy-erling-haaland-football-ERATCGJV" \
    --json-report "$REPORTS_DIR/latest-cost-analysis.json" \
    --markdown-report "$REPORTS_DIR/latest-cost-analysis.md"
fi

echo
echo "Cost analysis report: $REPORTS_DIR/latest-cost-analysis.md"
