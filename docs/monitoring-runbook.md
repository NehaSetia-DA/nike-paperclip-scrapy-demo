# Daily Nike Catalog Health Check Runbook

The Paperclip `Monitor` agent should run this routine daily.

1. Ensure `ZYTE_API_KEY` is present.
2. Run:

   ```sh
   ./scripts/validate-scrapy-output.sh
   ```

3. Report:

   - Item count.
   - Missing required-field counts.
   - Duplicate `product_url` count.
   - Whether `ZYTE_API_LOG_REQUESTS=True` produced request evidence in the crawl log.
   - Any fixture or crawl exception.

4. If validation fails, create a Paperclip repair issue assigned to `ScrapyBuilder` with:

   - failing command
   - error excerpt
   - latest output path
   - whether this looks like site drift, credential failure, access challenge, or generated-code bug
