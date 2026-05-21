"""Breadth-first web crawler implementation."""

from collections import deque
from time import sleep
from typing import Protocol

from crawler.config import CrawlerConfig
from crawler.fetcher import Fetcher
from crawler.models import FetchResult, PageData
from crawler.parser import HtmlParser
from crawler.url_utils import normalize_url


class FetcherProtocol(Protocol):
    """Small protocol used to make tests independent from real networking."""

    def fetch(self, url: str) -> FetchResult:
        """Fetch a URL and return a structured result."""


class WebCrawler:
    """A simple BFS crawler for educational Web 1.0-style crawling."""

    def __init__(
        self,
        config: CrawlerConfig,
        fetcher: FetcherProtocol | None = None,
        parser: HtmlParser | None = None,
    ) -> None:
        self.config = config
        self.fetcher = fetcher or Fetcher(
            timeout=config.timeout,
            user_agent=config.user_agent,
            respect_robots=config.respect_robots,
        )
        self.parser = parser or HtmlParser()

    def crawl(self) -> list[PageData]:
        """Run BFS from the configured start URL and return collected pages."""
        start_url = normalize_url(self.config.start_url, self.config.start_url)
        if start_url is None:
            raise ValueError(f"Invalid start URL: {self.config.start_url}")

        queue: deque[tuple[str, int]] = deque([(start_url, 0)])
        seen: set[str] = {start_url}
        pages: list[PageData] = []

        while queue and len(pages) < self.config.max_pages:
            current_url, depth = queue.popleft()
            fetch_result = self.fetcher.fetch(current_url)
            page = self._build_page_data(fetch_result, current_url, depth, start_url)
            pages.append(page)

            if page.is_successful and depth < self.config.max_depth:
                for link in page.internal_links:
                    if link not in seen:
                        seen.add(link)
                        queue.append((link, depth + 1))

            if queue and len(pages) < self.config.max_pages and self.config.delay > 0:
                sleep(self.config.delay)

        return pages

    def _build_page_data(
        self,
        fetch_result: FetchResult,
        requested_url: str,
        depth: int,
        start_url: str,
    ) -> PageData:
        if fetch_result.error is not None or fetch_result.html is None:
            return PageData(
                url=requested_url,
                status_code=fetch_result.status_code,
                title="",
                depth=depth,
                internal_links=[],
                external_links=[],
                error=fetch_result.error or "Empty response body",
            )

        parsed = self.parser.parse(fetch_result.html, requested_url, start_url)
        return PageData(
            url=requested_url,
            status_code=fetch_result.status_code,
            title=parsed.title,
            depth=depth,
            internal_links=parsed.internal_links,
            external_links=parsed.external_links,
            error=None,
        )

