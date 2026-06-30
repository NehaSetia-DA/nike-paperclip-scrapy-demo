REQUIRED_FIELDS = ["name", "brand", "product_url", "price", "currency", "source_url", "fetched_at"]


class NikeStatsPipeline:
    def open_spider(self, spider):
        self.seen_product_urls = set()

    def process_item(self, item, spider):
        stats = spider.crawler.stats
        stats.inc_value("nike/items_seen")

        for field in REQUIRED_FIELDS:
            if item.get(field) in (None, "", []):
                stats.inc_value(f"nike/missing_required/{field}")

        product_url = item.get("product_url")
        if product_url:
            if product_url in self.seen_product_urls:
                stats.inc_value("nike/duplicate_product_urls")
            self.seen_product_urls.add(product_url)

        return item
