#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LATEST = ROOT / "outputs" / "nike" / "latest" / "products.jsonl"
LEGACY = ROOT / "outputs" / "nike-products-sample.jsonl"


def main() -> None:
    path = LATEST if LATEST.exists() else LEGACY
    if not path.exists():
        raise SystemExit("No Nike product output found. Run ./scripts/monitor-nike-crawl.sh first.")

    print(f"items_file: {path}")
    with path.open("r", encoding="utf-8") as f:
        for index, line in enumerate(f, 1):
            item = json.loads(line)
            print(
                f"{index:02d}. {item.get('name')} | "
                f"{item.get('price')} {item.get('currency')} | "
                f"{item.get('product_url')}"
            )


if __name__ == "__main__":
    main()
