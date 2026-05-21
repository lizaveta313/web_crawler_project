"""Configuration objects for the web crawler."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CrawlerConfig:
    """Runtime settings for a crawler run."""

    start_url: str
    max_pages: int = 20
    max_depth: int = 2
    delay: float = 0.5
    output_dir: Path = Path("data")
    timeout: float = 10.0
    user_agent: str = "EducationalWebCrawler/1.0"
    respect_robots: bool = False

    def __post_init__(self) -> None:
        """Validate values and normalize path-like fields."""
        if self.max_pages < 1:
            raise ValueError("max_pages must be at least 1")
        if self.max_depth < 0:
            raise ValueError("max_depth must be 0 or greater")
        if self.delay < 0:
            raise ValueError("delay must be 0 or greater")
        if self.timeout <= 0:
            raise ValueError("timeout must be greater than 0")
        object.__setattr__(self, "output_dir", Path(self.output_dir))

