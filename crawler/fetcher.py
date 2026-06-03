"""HTTP loading layer for the crawler."""

from threading import Lock, local
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests

from crawler.models import FetchResult


HTML_CONTENT_TYPES = {"text/html", "application/xhtml+xml"}


class Fetcher:
    """Download pages and optionally check robots.txt rules."""

    def __init__(
        self,
        timeout: float = 10.0,
        user_agent: str = "EducationalWebCrawler/1.0",
        respect_robots: bool = False,
    ) -> None:
        self.timeout = timeout
        self.user_agent = user_agent
        self.respect_robots = respect_robots
        self._session_local = local()
        self._robots_cache: dict[str, RobotFileParser] = {}
        self._robots_lock = Lock()

    def fetch(self, url: str) -> FetchResult:
        """Fetch one URL and return an object that never raises network errors."""
        if self.respect_robots and not self._is_allowed_by_robots(url):
            return FetchResult(url=url, status_code=None, html=None, error="Blocked by robots.txt")

        try:
            response = self._get_session().get(url, timeout=self.timeout)
        except requests.RequestException as exc:
            return FetchResult(url=url, status_code=None, html=None, error=str(exc))

        error = None if 200 <= response.status_code < 300 else f"HTTP status {response.status_code}"
        if error is None and not self._is_html_response(response.headers.get("Content-Type", "")):
            content_type = response.headers.get("Content-Type") or "unknown"
            error = f"Unsupported content type: {content_type}"

        if error is None:
            response.encoding = response.encoding or response.apparent_encoding

        html = response.text if error is None else None
        return FetchResult(url=url, status_code=response.status_code, html=html, error=error)

    def _get_session(self) -> requests.Session:
        session = getattr(self._session_local, "session", None)
        if session is None:
            session = requests.Session()
            session.headers.update({"User-Agent": self.user_agent})
            self._session_local.session = session

        return session

    @staticmethod
    def _is_html_response(content_type: str) -> bool:
        if not content_type:
            return True

        media_type = content_type.split(";", 1)[0].strip().lower()
        return media_type in HTML_CONTENT_TYPES

    def _is_allowed_by_robots(self, url: str) -> bool:
        with self._robots_lock:
            origin = self._origin(url)
            parser = self._robots_cache.get(origin)
            if parser is None:
                parser = RobotFileParser()
                parser.set_url(urljoin(origin, "/robots.txt"))
                try:
                    parser.read()
                except OSError:
                    return True
                self._robots_cache[origin] = parser

            return parser.can_fetch(self.user_agent, url)

    @staticmethod
    def _origin(url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
