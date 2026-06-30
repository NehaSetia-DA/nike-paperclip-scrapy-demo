# Daily Nike Catalog Health Check Runbook

The Paperclip `Monitor` agent should run this routine daily.

1. Ensure `ZYTE_API_KEY` is present.
2. Run:

   ```sh
   ./scripts/monitor-nike-crawl.sh
   ```

3. Confirm the Scrapy log includes the real Spidermon close-monitor suite:

   - `Nike catalog health`
   - `Minimum product records`
   - `Required fields complete`
   - `No duplicate product URLs`
   - `Zyte API processed requests`
   - `No fatal Zyte API errors`

4. Report:

   - Item count.
   - Missing required-field counts.
   - Duplicate `product_url` count.
   - Whether `[Spidermon]` monitor lines appear in the crawl log.
   - Whether `ZYTE_API_LOG_REQUESTS=True` produced request evidence in the crawl log.
   - Any fixture or crawl exception.
   - Health report path: `reports/nike/latest-health.json`.
   - Product output path: `outputs/nike/latest/products.jsonl`.

5. If validation fails, create a Paperclip repair issue assigned to `QAReviewer` with:

   - failing command
   - error excerpt
   - latest output path
   - whether this looks like site drift, credential failure, access challenge, or generated-code bug

6. Assign `ScrapyBuilder` only when QA determines the existing parser/spider needs a structural rebuild. Routine runs should never call the Zyte codegen pipeline.

To demonstrate the feedback loop intentionally:

```sh
./scripts/demo-spidermon-break.sh
```

This clears `brand` after extraction, causing Spidermon to fail the required-field
monitor while still preserving crawl artifacts for QA review.
