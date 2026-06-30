#!/usr/bin/env python3
import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REQUIRED = ["name", "brand", "product_url", "price", "currency", "source_url", "fetched_at"]


def load_items(path: Path) -> list[dict]:
    items = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def count_log(pattern: str, log_text: str) -> int:
    return len(re.findall(pattern, log_text, re.IGNORECASE))


def build_report(items_path: Path, log_path: Path, min_items: int) -> dict:
    items = load_items(items_path) if items_path.exists() else []
    log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""

    missing = {field: 0 for field in REQUIRED}
    for item in items:
        for field in REQUIRED:
            if item.get(field) in (None, "", []):
                missing[field] += 1

    urls = [item.get("product_url") for item in items if item.get("product_url")]
    duplicate_urls = len(urls) - len(set(urls))
    currencies = Counter(item.get("currency") for item in items if item.get("currency"))
    status_counts = Counter(re.findall(r"response_status_count/(\d+)['\"]?:\s*(\d+)", log_text))

    checks = {
        "minimum_items": len(items) >= min_items,
        "required_fields_complete": all(count == 0 for count in missing.values()),
        "no_duplicate_product_urls": duplicate_urls == 0,
        "zyte_api_evidence": "scrapy-zyte-api" in log_text,
        "no_fatal_zyte_errors": "'scrapy-zyte-api/fatal_errors': 0" in log_text or '"scrapy-zyte-api/fatal_errors": 0' in log_text,
    }

    failures = [name for name, passed in checks.items() if not passed]
    status = "passed" if not failures else "failed"
    recommended_owner = "Monitor"
    if failures:
        recommended_owner = "QAReviewer"
    if not checks["zyte_api_evidence"] or not checks["no_fatal_zyte_errors"]:
        recommended_owner = "Coordinator"

    probable_cause = "healthy"
    if len(items) < min_items:
        probable_cause = "low item count: seed URLs may be stale, access may be degraded, or extraction skipped pages"
    if any(missing.values()):
        probable_cause = "required field completeness dropped: likely schema or parser drift"
    if duplicate_urls:
        probable_cause = "duplicate product URLs: navigation or canonical URL handling needs QA review"
    if not checks["zyte_api_evidence"]:
        probable_cause = "crawl log does not show Zyte API usage"

    return {
        "site": "nike",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "checks": checks,
        "failures": failures,
        "item_count": len(items),
        "expected_min_items": min_items,
        "required_missing_counts": missing,
        "duplicate_product_url_count": duplicate_urls,
        "currency_counts": dict(currencies),
        "zyte_api": {
            "evidence_in_log": checks["zyte_api_evidence"],
            "processed_mentions": count_log(r"scrapy-zyte-api/processed", log_text),
            "fatal_error_zero_seen": checks["no_fatal_zyte_errors"],
        },
        "http_status_counts_from_log": {f"{code}:{count}": hits for (code, count), hits in status_counts.items()},
        "probable_cause": probable_cause,
        "recommended_owner": recommended_owner,
        "artifacts": {
            "items": str(items_path),
            "crawl_log": str(log_path),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Spidermon-style health checks for Nike crawl output.")
    parser.add_argument("--items", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--min-items", type=int, default=10)
    args = parser.parse_args()

    report = build_report(args.items, args.log, args.min_items)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
