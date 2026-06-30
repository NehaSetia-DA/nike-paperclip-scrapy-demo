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

The Nike spider now defaults to Zyte API `httpResponseBody` and
`httpResponseHeaders`, which keeps the JSON-LD extraction path working without
browser rendering in routine runs.

Browser rendering is still available as an explicit recovery fallback:

```sh
NIKE_USE_BROWSER=true ./scripts/monitor-nike-crawl.sh
```

Use that fallback only when static JSON-LD extraction fails and QA confirms the
extra Zyte API cost is justified.

The spider also deduplicates seed URLs before scheduling requests and no longer
bypasses Scrapy's duplicate request filter with `dont_filter=True`.
