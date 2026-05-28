"""Prepare crawler pages for module 3 inverted index experiments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_MIN_TEXT_LENGTH = 50


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Convert pages.json to JSONL documents for module 3.")
    parser.add_argument("--input", required=True, help="Path to crawler pages.json.")
    parser.add_argument("--output", required=True, help="Path to output JSONL file.")
    parser.add_argument("--limit", type=int, default=None, help="Optional maximum number of documents.")
    parser.add_argument(
        "--min-text-length",
        type=int,
        default=DEFAULT_MIN_TEXT_LENGTH,
        help="Minimum text length required for indexing.",
    )
    return parser.parse_args()


def is_indexable_page(page: dict[str, Any], min_text_length: int = DEFAULT_MIN_TEXT_LENGTH) -> bool:
    """Return True if a page can be indexed."""
    text = str(page.get("text") or "").strip()
    error = page.get("error")
    return page.get("status_code") == 200 and not error and len(text) >= min_text_length


def page_to_document(page: dict[str, Any], doc_id: int) -> dict[str, Any]:
    """Convert a crawler page object to a module 3 document."""
    return {
        "doc_id": doc_id,
        "url": page.get("url", ""),
        "title": page.get("title", ""),
        "text": str(page.get("text") or "").strip(),
    }


def load_pages(input_path: str | Path) -> list[dict[str, Any]]:
    """Load pages from crawler JSON output."""
    path = Path(input_path)
    with path.open(encoding="utf-8") as input_file:
        pages = json.load(input_file)

    if not isinstance(pages, list):
        raise ValueError("Input file must contain a JSON array of pages.")
    return pages


def prepare_documents(
    pages: list[dict[str, Any]],
    limit: int | None = None,
    min_text_length: int = DEFAULT_MIN_TEXT_LENGTH,
) -> list[dict[str, Any]]:
    """Filter crawler pages and return documents ready for indexing."""
    documents: list[dict[str, Any]] = []
    for page in pages:
        if not is_indexable_page(page, min_text_length):
            continue

        documents.append(page_to_document(page, len(documents) + 1))
        if limit is not None and len(documents) >= limit:
            break

    return documents


def save_jsonl(documents: list[dict[str, Any]], output_path: str | Path) -> Path:
    """Save documents to JSONL and create the output directory if needed."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="\n") as output_file:
        for document in documents:
            output_file.write(json.dumps(document, ensure_ascii=False) + "\n")

    return path


def convert_pages_to_jsonl(
    input_path: str | Path,
    output_path: str | Path,
    limit: int | None = None,
    min_text_length: int = DEFAULT_MIN_TEXT_LENGTH,
) -> dict[str, Any]:
    """Convert crawler pages to module 3 JSONL documents and return conversion stats."""
    pages = load_pages(input_path)
    documents = prepare_documents(pages, limit, min_text_length)
    save_jsonl(documents, output_path)
    return {
        "total_pages_read": len(pages),
        "documents_saved": len(documents),
        "skipped_pages": len(pages) - len(documents),
        "total_text_length": sum(len(document["text"]) for document in documents),
        "output_path": str(output_path),
    }


def main() -> None:
    """Run conversion from CLI."""
    args = parse_args()
    stats = convert_pages_to_jsonl(args.input, args.output, args.limit, args.min_text_length)
    print(f"Pages read: {stats['total_pages_read']}")
    print(f"Documents saved: {stats['documents_saved']}")
    print(f"Pages skipped: {stats['skipped_pages']}")
    print(f"Output: {stats['output_path']}")


if __name__ == "__main__":
    main()
