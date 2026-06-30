import scrapy

from nike_catalog.parsers import parse_product_html


class NikeSpider(scrapy.Spider):
    name = "nike"
    allowed_domains = ["nike.com", "www.nike.com"]

    start_urls = [
        "https://www.nike.com/id/t/academy-erling-haaland-football-ERATCGJV",
        "https://www.nike.com/id/t/academy-vini-jr-football-gymsack-CmQ1CUMA",
        "https://www.nike.com/id/t/acg-older-utility-gilet-QIPc0VLH",
        "https://www.nike.com/id/t/acg-daymax-cross-body-bag-DsTGVz",
        "https://www.nike.com/id/t/acg-daymax-backpack-QkZ05z",
        "https://www.nike.com/id/t/acg-older-skort-KMjDn3vH",
        "https://www.nike.com/id/t/acg-fly-unstructured-cap-14M8kq0S",
        "https://www.nike.com/id/t/acg-pegasus-trail-by-you-trail-running-shoes-FTrNI6vA",
        "https://www.nike.com/id/t/acg-pegasus-trail-by-you-trail-running-shoes-UWhxxfer",
        "https://www.nike.com/id/t/acg-older-max90-t-shirt-mr9Fv8Qe",
        "https://www.nike.com/id/t/air-force-1-07-lv8-denim-shoes-og7aTpf7",
        "https://www.nike.com/id/t/air-force-1-07-lv8-shoes-CeByRzWT",
    ]

    def start_requests(self):
        use_browser = self.crawler.settings.getbool("NIKE_USE_BROWSER", False)
        zyte_api_automap = (
            {"browserHtml": True}
            if use_browser
            else {"httpResponseBody": True, "httpResponseHeaders": True}
        )
        seen = set()
        for url in self.start_urls:
            if url in seen:
                continue
            seen.add(url)
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={"zyte_api_automap": zyte_api_automap},
            )

    def parse(self, response):
        item = parse_product_html(response.text, response.url)
        if item.get("name") and item.get("price") is not None:
            demo_break_field = self.crawler.settings.get("NIKE_DEMO_BREAK_FIELD")
            if demo_break_field:
                item[demo_break_field] = None
                self.logger.warning("Demo break enabled: cleared %s for %s", demo_break_field, response.url)
            yield item
        else:
            self.logger.warning("Skipping page with incomplete required fields: %s", response.url)
