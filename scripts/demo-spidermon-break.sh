#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_ID="${RUN_ID:-demo-spidermon-break-$(date -u +"%Y%m%dT%H%M%SZ")}"
ITEM_LIMIT="${ITEM_LIMIT:-3}"
BREAK_FIELD="${BREAK_FIELD:-brand}"

echo "== Spidermon deliberate break demo =="
echo "run_id=$RUN_ID"
echo "item_limit=$ITEM_LIMIT"
echo "break_field=$BREAK_FIELD"
echo

set +e
RUN_ID="$RUN_ID" ITEM_LIMIT="$ITEM_LIMIT" NIKE_DEMO_BREAK_FIELD="$BREAK_FIELD" \
  "$ROOT/scripts/monitor-nike-crawl.sh"
STATUS=$?
set -e

echo
if [ "$STATUS" -eq 0 ]; then
  echo "Expected Spidermon to fail, but the demo crawl passed." >&2
  exit 1
fi

REPORT="$ROOT/outputs/nike/runs/$RUN_ID/health.json"
if [ ! -f "$REPORT" ]; then
  echo "Demo did not produce a health report. Check credentials and crawl setup first." >&2
  exit "$STATUS"
fi

if ! python3 - "$REPORT" "$BREAK_FIELD" <<'PY'
import json
import sys

report_path, break_field = sys.argv[1:]
report = json.load(open(report_path, encoding="utf-8"))
missing = report.get("required_missing_counts", {})
if "required_fields_complete" in report.get("failures", []) and missing.get(break_field, 0) > 0:
    raise SystemExit(0)

print(json.dumps({
    "status": report.get("status"),
    "failures": report.get("failures"),
    "required_missing_counts": missing,
    "probable_cause": report.get("probable_cause"),
}, indent=2))
raise SystemExit(1)
PY
then
  echo "Demo failed, but not because of the intended $BREAK_FIELD required-field break." >&2
  exit "$STATUS"
fi

echo "Demo succeeded: Spidermon detected the deliberate $BREAK_FIELD break."
echo "Inspect artifacts under: $ROOT/outputs/nike/runs/$RUN_ID"
