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
./scripts/validate-scrapy-output.sh
```

## Demo Architecture

- Paperclip is the control plane: goals, agents, issues, approvals, routines, and repair work.
- Zyte Claude skills are the modular build pipeline: schema discovery, review, spec, project creation, page-object generation, spider wiring.
- Scrapy is the extraction engine.
- Zyte API is the access/rendering layer.

## Expected Generated Layout

```text
.scrape/nike/
nike_catalog/
outputs/nike-products-sample.jsonl
```

## Implemented Scraper

The current Scrapy spider uses a small, robots-reviewed seed set from Nike's
public Indonesia PDP sitemap (`/id/t/...` URLs). Each request goes through
`scrapy-zyte-api` with rendered HTML enabled, then extracts product fields from
Nike's JSON-LD `ProductGroup` / `Product` data with visible-page fallbacks for
subtitle, price text, size labels, and style/color labels.

The parser intentionally avoids brittle CSS selectors for the core product
fields; JSON-LD is the stable extraction surface found by the Zyte skill
analysis pass.

## Safety Boundary

Use only public Nike pages allowed by robots and terms. Do not access member areas, cart, checkout, login/account pages, PDFs, or any path blocked by robots. If the chosen Nike public product/listing target is blocked or disallowed, stop and switch to another permitted public Nike sitemap/listing target.
