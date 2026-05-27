"""Saving crawler results to JSON and CSV files."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from crawler.models import PageData


class ResultStorage:
    """Persist pages and reports into an output directory."""

    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)

    def save_pages_json(self, pages: list[PageData], filename: str = "pages.json") -> Path:
        """Save page data as pretty JSON."""
        path = self._ensure_output_dir() / filename
        payload = [page.to_dict() for page in pages]
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def save_pages_csv(self, pages: list[PageData], filename: str = "pages.csv") -> Path:
        """Save page data as CSV."""
        path = self._ensure_output_dir() / filename
        fieldnames = [
            "url",
            "status_code",
            "title",
            "depth",
            "text",
            "internal_links",
            "external_links",
            "internal_link_count",
            "external_link_count",
            "total_link_count",
            "error",
        ]

        with path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for page in pages:
                writer.writerow(
                    {
                        "url": page.url,
                        "status_code": page.status_code,
                        "title": page.title,
                        "depth": page.depth,
                        "text": page.text,
                        "internal_links": "; ".join(page.internal_links),
                        "external_links": "; ".join(page.external_links),
                        "internal_link_count": page.internal_link_count,
                        "external_link_count": page.external_link_count,
                        "total_link_count": page.total_link_count,
                        "error": page.error,
                    }
                )

        return path

    def save_report_json(self, report: dict[str, Any], filename: str = "report.json") -> Path:
        """Save report data as pretty JSON."""
        path = self._ensure_output_dir() / filename
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def _ensure_output_dir(self) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return self.output_dir
