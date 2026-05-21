"""Educational Web 1.0 crawler package."""

from crawler.config import CrawlerConfig
from crawler.crawler import WebCrawler
from crawler.models import FetchResult, PageData, ParsedPage

__all__ = [
    "CrawlerConfig",
    "FetchResult",
    "PageData",
    "ParsedPage",
    "WebCrawler",
]

