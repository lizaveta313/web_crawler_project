"""Data models used by the crawler."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class FetchResult:
    """Result of a single HTTP fetch attempt."""

    url: str
    status_code: int | None
    html: str | None = None
    error: str | None = None


@dataclass
class ParsedPage:
    """Structured data extracted from an HTML page."""

    title: str
    internal_links: list[str] = field(default_factory=list)
    external_links: list[str] = field(default_factory=list)


@dataclass
class PageData:
    """Full information collected about a processed page."""

    url: str
    status_code: int | None
    title: str
    depth: int
    internal_links: list[str] = field(default_factory=list)
    external_links: list[str] = field(default_factory=list)
    error: str | None = None

    @property
    def internal_link_count(self) -> int:
        """Return the number of internal links found on the page."""
        return len(self.internal_links)

    @property
    def external_link_count(self) -> int:
        """Return the number of external links found on the page."""
        return len(self.external_links)

    @property
    def total_link_count(self) -> int:
        """Return the total number of links found on the page."""
        return self.internal_link_count + self.external_link_count

    @property
    def is_successful(self) -> bool:
        """Return True if the page was fetched without errors."""
        return self.error is None and self.status_code is not None and 200 <= self.status_code < 300

    def to_dict(self) -> dict[str, Any]:
        """Convert page data to a serializable dictionary."""
        data = asdict(self)
        data["internal_link_count"] = self.internal_link_count
        data["external_link_count"] = self.external_link_count
        data["total_link_count"] = self.total_link_count
        return data

