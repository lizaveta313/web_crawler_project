"""HTML parsing logic based on BeautifulSoup."""

from bs4 import BeautifulSoup

from crawler.models import ParsedPage
from crawler.url_utils import is_internal_url, normalize_url, unique_preserve_order


class HtmlParser:
    """Extract page title and classified links from HTML."""

    def parse(self, html: str, page_url: str, start_url: str) -> ParsedPage:
        """Parse HTML and return title, internal links, and external links."""
        soup = BeautifulSoup(html, "html.parser")
        title = self._extract_title(soup)

        internal_links: list[str] = []
        external_links: list[str] = []

        for tag in soup.find_all("a", href=True):
            normalized = normalize_url(page_url, tag.get("href"))
            if normalized is None:
                continue

            if is_internal_url(normalized, start_url):
                internal_links.append(normalized)
            else:
                external_links.append(normalized)

        return ParsedPage(
            title=title,
            internal_links=unique_preserve_order(internal_links),
            external_links=unique_preserve_order(external_links),
        )

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> str:
        if soup.title is None or soup.title.string is None:
            return ""
        return soup.title.string.strip()

