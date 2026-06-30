# Nike Agentic Scraping Demo

Local demo of Paperclip coordinating a Claude + Zyte Web Data skill workflow that generates and monitors a Scrapy + Zyte API product-data scraper for public Nike pages.

## Status

- Target: `https://www.nike.com/`
- Robots checked: Nike exposes public sitemap indexes and disallows private/account/checkout-style paths. This demo must avoid disallowed paths including member pages, checkout, PDFs, `/p/`, and restricted gridwall patterns.
- Required credentials: `ANTHROPIC_API_KEY`, `ZYTE_API_KEY`.
- Working Scrapy project: `nike_catalog/`
- Sample output: `outputs/nike-products-sample.jsonl`
- Paperclip seed state: `outputs/paperclip-seed-state.json`

## Quick Start

```sh
export ANTHROPIC_API_KEY="..."
export ZYTE_API_KEY="..."
./scripts/preflight.sh
./scripts/setup-paperclip.sh
./scripts/seed-paperclip.sh
./scripts/run-zyte-skill-pipeline.sh
./scripts/validate-scrapy-output.sh
```

For the already generated local scraper, this is the useful validation loop:

```sh
export ZYTE_API_KEY="..."
./scripts/monitor-nike-crawl.sh
./scripts/run-scrapy-cost-analysis.sh
```

## Demo Architecture

- Paperclip is the control plane: goals, agents, issues, approvals, routines, and repair work.
- Zyte Claude skills are the modular build pipeline: schema discovery, review, spec, project creation, page-object generation, spider wiring.
- Scrapy is the extraction engine.
- Zyte API is the access/rendering layer.
- Spidermon is the runtime quality guardrail.
- Scrapy cost analysis is the optimization lane for browser rendering, retries, duplicate requests, and Zyte API usage.

Full architecture and decision flow: `docs/project-flow.md`.

Component architecture: `docs/architecture.md`.

## Expected Generated Layout

```text
.scrape/nike/
nike_catalog/
outputs/nike-products-sample.jsonl
```

## Build Mode vs Run Mode

Build mode is for first-time sites or structural changes:

```sh
./scripts/run-zyte-skill-pipeline.sh
./scripts/validate-scrapy-output.sh
```

Run mode is for every normal Nike crawl after the spider exists:

```sh
export ZYTE_API_KEY="..."
./scripts/monitor-nike-crawl.sh
```

Run mode does not call the Zyte codegen skills and does not involve
`ScrapyBuilder`. It runs the existing spider, saves timestamped artifacts under
`outputs/nike/runs/`, updates `outputs/nike/latest/`, and writes a
Spidermon-backed health report to `reports/nike/latest-health.json`.

If the health report fails, `Monitor` should create a QA issue. `QAReviewer`
decides whether the failure is data quality, credentials/access, parser drift,
or a structural rebuild that should go back to `ScrapyBuilder`.

To inspect the latest scraped products:

```sh
./scripts/show-latest-items.py
```

To inspect Zyte API cost risks for the current spider:

```sh
./scripts/run-scrapy-cost-analysis.sh
```

The report is written to `reports/nike/latest-cost-analysis.md`.

## Spidermon Demo

The Scrapy project enables the real Spidermon Scrapy extension in
`nike_catalog/nike_catalog/settings.py`. On spider close, Spidermon checks:

- minimum product count
- required field completeness
- duplicate `product_url` values
- Zyte API processed requests
- fatal Zyte API errors

To deliberately break extraction and show the monitor catching it:

```sh
export ZYTE_API_KEY="..."
./scripts/demo-spidermon-break.sh
```

The demo clears `brand` after extraction, keeps the items flowing, and should
fail with a Spidermon required-field error. Artifacts are saved under
`outputs/nike/runs/demo-spidermon-break-*`.

## Implemented Scraper

The current Scrapy spider uses a small, robots-reviewed seed set from Nike's
public Indonesia PDP sitemap (`/id/t/...` URLs). Each request goes through
`scrapy-zyte-api` with rendered HTML enabled, then extracts product fields from
Nike's JSON-LD `ProductGroup` / `Product` data with visible-page fallbacks for
subtitle, price text, size labels, and style/color labels.

The parser intentionally avoids brittle CSS selectors for the core product
fields; JSON-LD is the stable extraction surface found by the Zyte skill
analysis pass.

## Cost Analysis

The intended Claude Code skill invocation is documented in
`docs/cost-analysis-runbook.md`:

```text
/scrapy-cost-analysis nike nike_catalog/nike_catalog/spiders/nike.py nike_catalog/nike_catalog/settings.py outputs/nike/latest/crawl.log https://www.nike.com/id/t/academy-erling-haaland-football-ERATCGJV
```

If the Claude Code skill is not installed yet, use the local fallback:

```sh
./scripts/run-scrapy-cost-analysis.sh
```

## Safety Boundary

Use only public Nike pages allowed by robots and terms. Do not access member areas, cart, checkout, login/account pages, PDFs, or any path blocked by robots. If the chosen Nike public product/listing target is blocked or disallowed, stop and switch to another permitted public Nike sitemap/listing target.
