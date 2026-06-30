# Scrapy Cost Analysis Runbook

Use this when a Nike crawl succeeds but Zyte API spend looks higher than expected,
or before promoting spider changes.

## Claude Code Skill

Preferred Claude Code invocation when the Zyte skill is installed:

```text
/scrapy-cost-analysis nike nike_catalog/nike_catalog/spiders/nike.py nike_catalog/nike_catalog/settings.py outputs/nike/latest/crawl.log https://www.nike.com/id/t/academy-erling-haaland-football-ERATCGJV
```

If the command is unavailable, install or refresh the Zyte skills/plugin from
`zytedata/claude-skills`, then link the cost-analysis skill into
`~/.claude/skills/` according to your Claude Code setup.

## Local Fallback

This repository also includes a local analyzer that checks the same cost-risk
categories for the generated Nike spider:

```sh
./scripts/run-scrapy-cost-analysis.sh
```

It writes:

- `reports/nike/latest-cost-analysis.md`
- `reports/nike/latest-cost-analysis.json`

## What To Review

1. Browser rendering and Zyte API automation usage.
2. Retry amplification from `RETRY_TIMES` and retry stats.
3. Duplicate crawling from `dont_filter=True`, weak pagination stops, or repeated seed URLs.
4. Request volume against item count.
5. Whether sample job stats confirm the cost issue.

## Current Nike Cost Hypothesis

The Nike spider currently requests every PDP through Zyte API with
`browserHtml=True`. That is intentionally reliable for the demo, but likely the
highest-impact cost lever is to test whether the JSON-LD product data is present
without browser rendering. If it is, PDP requests can move to a cheaper access
mode while preserving the same parser and Spidermon checks.

`dont_filter=True` is also present on seeded PDP requests. It is acceptable for a
small fixed demo seed, but a production crawl should deduplicate seed URLs and
avoid bypassing Scrapy's request filter unless there is a specific reason.
