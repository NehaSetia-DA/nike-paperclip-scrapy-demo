#!/usr/bin/env python3
import json
import sys


REQUIRED = ["name", "brand", "product_url", "price", "currency", "source_url", "fetched_at"]


def main(path):
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))

    print(f"items: {len(items)}")
    if len(items) < 10:
        raise SystemExit("Expected at least 10 product records.")

    missing = {field: 0 for field in REQUIRED}
    for item in items:
        for field in REQUIRED:
            if item.get(field) in (None, "", []):
                missing[field] += 1

    print("required field missing counts:")
    for field, count in missing.items():
        print(f"  {field}: {count}")
        if count:
            raise SystemExit(f"Required field missing: {field}")

    urls = [item["product_url"] for item in items]
    duplicates = len(urls) - len(set(urls))
    print(f"duplicate product_url count: {duplicates}")
    if duplicates:
        raise SystemExit("Duplicate product_url values found.")

    print("sample output passed acceptance checks.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: check_sample_output.py outputs/nike-products-sample.jsonl")
    main(sys.argv[1])
