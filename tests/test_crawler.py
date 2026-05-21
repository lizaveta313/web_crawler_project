from crawler.config import CrawlerConfig
from crawler.crawler import WebCrawler
from crawler.models import FetchResult


class FakeFetcher:
    def __init__(self, pages: dict[str, FetchResult]) -> None:
        self.pages = pages
        self.fetched_urls: list[str] = []

    def fetch(self, url: str) -> FetchResult:
        self.fetched_urls.append(url)
        return self.pages.get(
            url,
            FetchResult(url=url, status_code=404, html=None, error="Not found"),
        )


def make_fake_pages() -> dict[str, FetchResult]:
    return {
        "https://example.com/": FetchResult(
            url="https://example.com/",
            status_code=200,
            html="""
            <title>Home</title>
            <a href="/a">A</a>
            <a href="/b">B</a>
            <a href="https://external.test/">External</a>
            """,
        ),
        "https://example.com/a": FetchResult(
            url="https://example.com/a",
            status_code=200,
            html="""
            <title>A</title>
            <a href="/c">C</a>
            <a href="/b">B duplicate</a>
            """,
        ),
        "https://example.com/b": FetchResult(
            url="https://example.com/b",
            status_code=200,
            html="""
            <title>B</title>
            <a href="/c">C duplicate</a>
            """,
        ),
        "https://example.com/c": FetchResult(
            url="https://example.com/c",
            status_code=200,
            html="<title>C</title>",
        ),
    }


def test_crawler_bfs_order() -> None:
    fake_fetcher = FakeFetcher(make_fake_pages())
    config = CrawlerConfig(start_url="https://example.com", max_pages=10, max_depth=2, delay=0)

    pages = WebCrawler(config, fetcher=fake_fetcher).crawl()

    assert [page.url for page in pages] == [
        "https://example.com/",
        "https://example.com/a",
        "https://example.com/b",
        "https://example.com/c",
    ]


def test_crawler_respects_max_depth() -> None:
    fake_fetcher = FakeFetcher(make_fake_pages())
    config = CrawlerConfig(start_url="https://example.com", max_pages=10, max_depth=1, delay=0)

    pages = WebCrawler(config, fetcher=fake_fetcher).crawl()

    assert [page.url for page in pages] == [
        "https://example.com/",
        "https://example.com/a",
        "https://example.com/b",
    ]


def test_crawler_respects_max_pages() -> None:
    fake_fetcher = FakeFetcher(make_fake_pages())
    config = CrawlerConfig(start_url="https://example.com", max_pages=2, max_depth=5, delay=0)

    pages = WebCrawler(config, fetcher=fake_fetcher).crawl()

    assert [page.url for page in pages] == [
        "https://example.com/",
        "https://example.com/a",
    ]


def test_crawler_does_not_visit_same_url_twice() -> None:
    fake_fetcher = FakeFetcher(make_fake_pages())
    config = CrawlerConfig(start_url="https://example.com", max_pages=10, max_depth=3, delay=0)

    WebCrawler(config, fetcher=fake_fetcher).crawl()

    assert fake_fetcher.fetched_urls.count("https://example.com/b") == 1
    assert fake_fetcher.fetched_urls.count("https://example.com/c") == 1


def test_crawler_handles_error_page() -> None:
    pages = make_fake_pages()
    pages["https://example.com/"] = FetchResult(
        url="https://example.com/",
        status_code=200,
        html="<title>Home</title><a href='/bad'>Bad</a>",
    )
    pages["https://example.com/bad"] = FetchResult(
        url="https://example.com/bad",
        status_code=500,
        html=None,
        error="HTTP status 500",
    )
    fake_fetcher = FakeFetcher(pages)
    config = CrawlerConfig(start_url="https://example.com", max_pages=10, max_depth=2, delay=0)

    result = WebCrawler(config, fetcher=fake_fetcher).crawl()
    bad_page = next(page for page in result if page.url == "https://example.com/bad")

    assert bad_page.status_code == 500
    assert bad_page.error == "HTTP status 500"
    assert bad_page.internal_links == []


def test_crawler_saves_page_depth() -> None:
    fake_fetcher = FakeFetcher(make_fake_pages())
    config = CrawlerConfig(start_url="https://example.com", max_pages=10, max_depth=2, delay=0)

    pages = WebCrawler(config, fetcher=fake_fetcher).crawl()
    depths = {page.url: page.depth for page in pages}

    assert depths["https://example.com/"] == 0
    assert depths["https://example.com/a"] == 1
    assert depths["https://example.com/b"] == 1
    assert depths["https://example.com/c"] == 2

