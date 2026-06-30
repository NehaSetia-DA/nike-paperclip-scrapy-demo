# Daily Nike Catalog Health Check Runbook

The Paperclip `Monitor` agent should run this routine daily.

1. Ensure `ZYTE_API_KEY` is present.
2. Run:

   ```sh
   ./scripts/monitor-nike-crawl.sh
   ```

3. Report:

   - Item count.
   - Missing required-field counts.
   - Duplicate `product_url` count.
   - Whether `ZYTE_API_LOG_REQUESTS=True` produced request evidence in the crawl log.
   - Any fixture or crawl exception.
   - Health report path: `reports/nike/latest-health.json`.
   - Product output path: `outputs/nike/latest/products.jsonl`.

4. If validation fails, create a Paperclip repair issue assigned to `QAReviewer` with:

   - failing command
   - error excerpt
   - latest output path
   - whether this looks like site drift, credential failure, access challenge, or generated-code bug

5. Assign `ScrapyBuilder` only when QA determines the existing parser/spider needs a structural rebuild. Routine runs should never call the Zyte codegen pipeline.
