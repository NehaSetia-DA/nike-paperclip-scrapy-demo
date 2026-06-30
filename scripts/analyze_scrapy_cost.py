#!/usr/bin/env python3
import argparse
import ast
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Finding:
    severity: str
    title: str
    evidence: str
    recommendation: str


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def collect_constants(tree: ast.AST) -> dict[str, object]:
    constants = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    try:
                        constants[target.id] = ast.literal_eval(node.value)
                    except Exception:
                        pass
    return constants


def stat_from_log(log_text: str, name: str) -> int | None:
    patterns = [
        rf"['\"]{re.escape(name)}['\"]\s*:\s*(\d+)",
        rf"{re.escape(name)}\s*[:=]\s*(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, log_text)
        if match:
            return int(match.group(1))
    return None


def analyze(spider_file: Path, settings_file: Path | None, log_file: Path | None, sample_url: str | None) -> dict:
    spider_text = read(spider_file)
    settings_text = read(settings_file) if settings_file and settings_file.exists() else ""
    log_text = read(log_file) if log_file and log_file.exists() else ""
    tree = ast.parse(spider_text)
    constants = collect_constants(tree)
    findings: list[Finding] = []

    has_browser_html_fallback = "browserHtml" in spider_text
    uses_browser_html_by_default = has_browser_html_fallback and not re.search(
        r"getbool\([\"']NIKE_USE_BROWSER[\"']\s*,\s*False\)",
        spider_text,
    )
    uses_automap = "zyte_api_automap" in spider_text
    dont_filter_count = spider_text.count("dont_filter=True")
    retry_times_match = re.search(r"RETRY_TIMES\s*=\s*(\d+)", settings_text)
    retry_times = int(retry_times_match.group(1)) if retry_times_match else None
    start_urls = constants.get("start_urls", [])
    start_url_count = len(start_urls) if isinstance(start_urls, list) else None

    processed = stat_from_log(log_text, "scrapy-zyte-api/processed")
    browser_html = stat_from_log(log_text, "scrapy-zyte-api/request_args/browserHtml")
    item_count = stat_from_log(log_text, "item_scraped_count")
    retry_count = stat_from_log(log_text, "retry/count")
    dupefilter = stat_from_log(log_text, "dupefilter/filtered")

    if uses_browser_html_by_default:
        findings.append(Finding(
            "high",
            "Rendered browser HTML is enabled for every request",
            "Spider passes zyte_api_automap with browserHtml=True.",
            "Keep browser rendering only if static HTML or embedded JSON is insufficient. For Nike, first test whether ProductGroup/Product JSON-LD is available without browserHtml and switch PDP requests to cheaper HTTP extraction when possible.",
        ))
    elif has_browser_html_fallback:
        findings.append(Finding(
            "info",
            "Browser rendering is available as an explicit fallback",
            "Spider supports NIKE_USE_BROWSER=True but defaults to httpResponseBody/httpResponseHeaders.",
            "Keep the fallback for recovery, but leave it disabled for routine runs while static JSON-LD extraction remains healthy.",
        ))

    if uses_automap:
        findings.append(Finding(
            "medium",
            "Zyte API automap is used broadly",
            "Spider sets zyte_api_automap request metadata.",
            "Pin the minimum Zyte API features needed per request type. Avoid carrying browser rendering or extraction features into pages that only need normal HTML.",
        ))

    if dont_filter_count:
        findings.append(Finding(
            "medium",
            "Duplicate filtering is bypassed",
            f"Found dont_filter=True {dont_filter_count} time(s).",
            "Remove dont_filter=True unless each duplicate request is intentional. If retained for seeded PDPs, keep the seed list deduplicated and monitor duplicate product_url counts.",
        ))

    if retry_times is not None and retry_times > 2:
        findings.append(Finding(
            "medium",
            "Retry count can amplify Zyte API spend",
            f"RETRY_TIMES is {retry_times}.",
            "Lower retry count for normal health checks and reserve higher retries for production jobs with strong evidence that retries recover useful products.",
        ))

    if start_url_count is not None and start_url_count > 100:
        findings.append(Finding(
            "medium",
            "Large static seed list",
            f"Spider has {start_url_count} start URLs.",
            "Move large seed discovery into a deduped sitemap/listing stage with clear pagination stop conditions.",
        ))

    if browser_html and processed and browser_html == processed:
        findings.append(Finding(
            "high",
            "All Zyte API requests used browserHtml in the sampled job",
            f"browserHtml requests={browser_html}; processed requests={processed}.",
            "Run an A/B sample without browserHtml. If JSON-LD survives, this is likely the highest-impact cost reduction.",
        ))

    if retry_count and processed and retry_count / processed > 0.1:
        findings.append(Finding(
            "medium",
            "Retry amplification appears in job stats",
            f"retry/count={retry_count}; scrapy-zyte-api/processed={processed}.",
            "Inspect retry reasons and reduce retryable status/error classes where they do not recover products.",
        ))

    if dupefilter and processed and dupefilter > processed:
        findings.append(Finding(
            "low",
            "Many duplicate requests are being filtered",
            f"dupefilter/filtered={dupefilter}; processed={processed}.",
            "Review navigation and pagination to avoid scheduling duplicates before the dupefilter catches them.",
        ))

    if not findings:
        findings.append(Finding(
            "info",
            "No confirmed cost issue found from local files",
            "No broad rendering, duplicate bypass, retry amplification, or job-stat issue was detected.",
            "Validate with a real crawl log or Zyte dashboard job stats before deployment.",
        ))

    priority = {"high": 0, "medium": 1, "low": 2, "info": 3}
    findings.sort(key=lambda finding: priority.get(finding.severity, 99))

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "spider": str(spider_file),
        "settings": str(settings_file) if settings_file else None,
        "log": str(log_file) if log_file else None,
        "sample_url": sample_url,
        "signals": {
            "uses_browser_html": uses_browser_html_by_default,
            "has_browser_html_fallback": has_browser_html_fallback,
            "uses_zyte_api_automap": uses_automap,
            "dont_filter_true_count": dont_filter_count,
            "retry_times": retry_times,
            "start_url_count": start_url_count,
            "stats": {
                "scrapy-zyte-api/processed": processed,
                "scrapy-zyte-api/request_args/browserHtml": browser_html,
                "item_scraped_count": item_count,
                "retry/count": retry_count,
                "dupefilter/filtered": dupefilter,
            },
        },
        "findings": [asdict(finding) for finding in findings],
    }


def write_markdown(report: dict, path: Path) -> None:
    lines = [
        "# Scrapy Cost Analysis",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Spider: `{report['spider']}`",
        "",
        "## Signals",
        "",
    ]
    for key, value in report["signals"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Findings", ""])
    for finding in report["findings"]:
        lines.extend([
            f"### {finding['severity'].upper()}: {finding['title']}",
            "",
            f"Evidence: {finding['evidence']}",
            "",
            f"Recommendation: {finding['recommendation']}",
            "",
        ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Local Scrapy + Zyte API cost analysis helper.")
    parser.add_argument("spider_file", type=Path)
    parser.add_argument("--settings", type=Path)
    parser.add_argument("--log", type=Path)
    parser.add_argument("--sample-url")
    parser.add_argument("--json-report", type=Path, required=True)
    parser.add_argument("--markdown-report", type=Path, required=True)
    args = parser.parse_args()

    report = analyze(args.spider_file, args.settings, args.log, args.sample_url)
    args.json_report.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_report.parent.mkdir(parents=True, exist_ok=True)
    args.json_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report, args.markdown_report)

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
