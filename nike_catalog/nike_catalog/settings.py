BOT_NAME = "nike_catalog"

SPIDER_MODULES = ["nike_catalog.spiders"]
NEWSPIDER_MODULE = "nike_catalog.spiders"

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 2
CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_TIMEOUT = 60
RETRY_TIMES = 2
LOG_LEVEL = "INFO"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

ADDONS = {
    "scrapy_zyte_api.Addon": 500,
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

FEED_EXPORT_ENCODING = "utf-8"
