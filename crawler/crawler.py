"""Breadth-first web crawler implementation."""

from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from collections import deque
from time import sleep

from crawler.config import CrawlerConfig
from crawler.fetcher import Fetcher
from crawler.models import FetchResult, PageData
from crawler.parser import HtmlParser
from crawler.url_utils import normalize_url


class WebCrawler:
    """A simple BFS crawler for educational Web 1.0-style crawling."""

    def __init__(
        self,
        config: CrawlerConfig,
        fetcher: Fetcher | None = None,
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

        if self.config.workers > 1:
            return self._crawl_parallel(start_url)

        return self._crawl_sequential(start_url)

    def _crawl_sequential(self, start_url: str) -> list[PageData]:
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

    def _crawl_parallel(self, start_url: str) -> list[PageData]:
        current_level: deque[tuple[str, int]] = deque([(start_url, 0)])
        seen: set[str] = {start_url}
        pages: list[PageData] = []

        with ThreadPoolExecutor(max_workers=self.config.workers) as executor:
            while current_level and len(pages) < self.config.max_pages:
                next_level: deque[tuple[str, int]] = deque()
                active: dict[Future[PageData], tuple[str, int]] = {}

                while (current_level or active) and len(pages) < self.config.max_pages:
                    self._submit_fetches(executor, active, current_level, start_url, pages)
                    if not active:
                        break

                    done, _pending = wait(active, return_when=FIRST_COMPLETED)
                    for future in done:
                        requested_url, depth = active.pop(future)
                        page = self._page_from_future(future, requested_url, depth)
                        pages.append(page)
                        self._enqueue_links(page, next_level, seen)

                        if len(pages) >= self.config.max_pages:
                            break

                current_level = next_level

        return pages

    def _submit_fetches(
        self,
        executor: ThreadPoolExecutor,
        active: dict[Future[PageData], tuple[str, int]],
        queue: deque[tuple[str, int]],
        start_url: str,
        pages: list[PageData],
    ) -> None:
        while (
            queue
            and len(active) < self.config.workers
            and len(pages) + len(active) < self.config.max_pages
        ):
            current_url, depth = queue.popleft()
            future = executor.submit(self._fetch_page, current_url, depth, start_url, True)
            active[future] = (current_url, depth)

    def _fetch_page(
        self,
        current_url: str,
        depth: int,
        start_url: str,
        apply_delay: bool = False,
    ) -> PageData:
        fetch_result = self.fetcher.fetch(current_url)
        page = self._build_page_data(fetch_result, current_url, depth, start_url)

        if apply_delay and self.config.delay > 0:
            sleep(self.config.delay)

        return page

    def _page_from_future(self, future: Future[PageData], requested_url: str, depth: int) -> PageData:
        try:
            return future.result()
        except Exception as exc:
            return PageData(
                url=requested_url,
                status_code=None,
                title="",
                depth=depth,
                text="",
                internal_links=[],
                external_links=[],
                error=f"Crawl error: {exc}",
            )

    def _enqueue_links(
        self,
        page: PageData,
        queue: deque[tuple[str, int]],
        seen: set[str],
    ) -> None:
        if not page.is_successful or page.depth >= self.config.max_depth:
            return

        for link in page.internal_links:
            if link not in seen:
                seen.add(link)
                queue.append((link, page.depth + 1))

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
                text="",
                internal_links=[],
                external_links=[],
                error=fetch_result.error or "Empty response body",
            )

        try:
            parsed = self.parser.parse(fetch_result.html, requested_url, start_url)
        except Exception as exc:
            return PageData(
                url=requested_url,
                status_code=fetch_result.status_code,
                title="",
                depth=depth,
                text="",
                internal_links=[],
                external_links=[],
                error=f"Parse error: {exc}",
            )

        return PageData(
            url=requested_url,
            status_code=fetch_result.status_code,
            title=parsed.title,
            depth=depth,
            text=parsed.text,
            internal_links=parsed.internal_links,
            external_links=parsed.external_links,
            error=None,
        )
