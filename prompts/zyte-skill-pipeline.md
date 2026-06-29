# Claude Prompt: Generate Nike Scrapy Project With Zyte Skills

Use the installed Zyte Web Data Claude plugin. Build the scraper through the modular skills, not by manually writing selectors from scratch.

Target: https://www.nike.com/

Project directory: ./nike_catalog

Project package name: nike_catalog

Site/spec name: nike

Required constraint: Nike robots.txt has been checked. Stay on public, allowed pages. Do not access member pages, account settings, cart, checkout, PDFs, `/p/`, or any disallowed path. If a candidate public listing/detail target is disallowed by robots.txt or terms, stop and choose another allowed public Nike target.

Goal:

Generate a runnable Scrapy project using scrapy-poet, web-poet, and scrapy-zyte-api that extracts public Nike product/catalog data.

Run this skill flow:

1. `/scrape-zyte-login`
2. `/scrape-define https://www.nike.com/`
3. `/scrape-review-schema .scrape/nike`
4. Pause for schema approval if the skill requests it. Use the schema from `docs/product-schema.md` as the target field contract.
5. `/scrape-spec .scrape/nike`
6. `/scrape-ensure-project ./nike_catalog nike_catalog`
7. `/scrape-codegen .scrape/nike/product ./nike_catalog`
8. `/scrape-codegen .scrape/nike/navigation ./nike_catalog`
9. `/scrape-create-spider ./nike_catalog nike_catalog.pages.nike.ProductPage nike_catalog.pages.nike.NavigationPage`

After generation:

- Run `cd nike_catalog && uv run pytest fixtures/`.
- Run a small sample crawl with `CLOSESPIDER_ITEMCOUNT=10`.
- Save output to `outputs/nike-products-sample.jsonl`.
- Summarize required-field completeness, duplicate URLs, and Zyte API evidence.

If blocked:

- Stop before any workaround.
- Explain whether the blocker is credentials, robots/terms, access challenge, schema ambiguity, or generated-code failure.
- Leave the generated artifacts and exact next command to resume.
