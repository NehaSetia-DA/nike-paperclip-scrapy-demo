from spidermon import Monitor, MonitorSuite, monitors

from nike_catalog.pipelines import REQUIRED_FIELDS


def _stat(stats, name, default=0):
    if hasattr(stats, "get"):
        return stats.get(name, default)
    return getattr(stats, name, default)


@monitors.name("Nike catalog health")
class NikeCatalogHealthMonitor(Monitor):
    @monitors.name("Minimum product records")
    def test_minimum_product_records(self):
        expected = int(self.data.crawler.settings.get("NIKE_MIN_ITEMS", 10))
        scraped = _stat(self.data.stats, "item_scraped_count", 0)
        self.assertGreaterEqual(scraped, expected, f"Scraped {scraped} items, expected at least {expected}")

    @monitors.name("Required fields complete")
    def test_required_fields_complete(self):
        missing = {
            field: _stat(self.data.stats, f"nike/missing_required/{field}", 0)
            for field in REQUIRED_FIELDS
        }
        missing = {field: count for field, count in missing.items() if count}
        self.assertFalse(missing, f"Missing required fields: {missing}")

    @monitors.name("No duplicate product URLs")
    def test_no_duplicate_product_urls(self):
        duplicates = _stat(self.data.stats, "nike/duplicate_product_urls", 0)
        self.assertEqual(duplicates, 0, f"Found {duplicates} duplicate product URLs")

    @monitors.name("Zyte API processed requests")
    def test_zyte_api_processed_requests(self):
        processed = _stat(self.data.stats, "scrapy-zyte-api/processed", 0)
        self.assertGreater(processed, 0, "Zyte API did not process any requests")

    @monitors.name("No fatal Zyte API errors")
    def test_no_fatal_zyte_api_errors(self):
        fatal_errors = _stat(self.data.stats, "scrapy-zyte-api/fatal_errors", 0)
        self.assertEqual(fatal_errors, 0, f"Zyte API fatal errors: {fatal_errors}")


class NikeSpiderCloseMonitorSuite(MonitorSuite):
    monitors = [NikeCatalogHealthMonitor]
