"""Command-line entry point for the educational web crawler."""

from __future__ import annotations

import argparse
from pathlib import Path

from crawler.config import CrawlerConfig
from crawler.crawler import WebCrawler
from crawler.report import build_report
from crawler.storage import ResultStorage


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run a simple BFS web crawler.")
    parser.add_argument("--url", required=True, help="Start URL for crawling.")
    parser.add_argument("--max-pages", type=int, default=20, help="Maximum number of pages to process.")
    parser.add_argument("--max-depth", type=int, default=2, help="Maximum BFS depth.")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between requests in seconds.")
    parser.add_argument("--workers", type=int, default=1, help="Number of parallel page fetch workers.")
    parser.add_argument("--output-dir", default="data", help="Directory for pages.json, pages.csv and report.json.")
    parser.add_argument(
        "--respect-robots",
        action="store_true",
        help="Check robots.txt before fetching pages.",
    )
    return parser.parse_args()


def main() -> None:
    """Run crawler, save files, and print a short report."""
    args = parse_args()
    config = CrawlerConfig(
        start_url=args.url,
        max_pages=args.max_pages,
        max_depth=args.max_depth,
        delay=args.delay,
        workers=args.workers,
        output_dir=Path(args.output_dir),
        respect_robots=args.respect_robots,
    )

    crawler = WebCrawler(config)
    pages = crawler.crawl()
    report = build_report(pages)

    storage = ResultStorage(config.output_dir)
    pages_json = storage.save_pages_json(pages)
    pages_csv = storage.save_pages_csv(pages)
    report_json = storage.save_report_json(report)

    print("Crawl finished")
    print(f"Processed pages: {report['total_pages_processed']}")
    print(f"Successful pages: {report['successful_pages']}")
    print(f"Pages with errors: {report['error_pages']}")
    print(f"Total links found: {report['total_links_found']}")
    print(f"Internal links: {report['internal_links_total']}")
    print(f"External links: {report['external_links_total']}")
    print(f"Pages with text: {report['pages_with_text']}")
    print(f"Saved: {pages_json}")
    print(f"Saved: {pages_csv}")
    print(f"Saved: {report_json}")


if __name__ == "__main__":
    main()
