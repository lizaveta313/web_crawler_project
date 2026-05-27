"""Report generation for crawler results."""

from typing import Any
from urllib.parse import urlparse

from crawler.models import PageData


def build_report(pages: list[PageData]) -> dict[str, Any]:
    """Build aggregate statistics for processed pages."""
    successful_pages = sum(1 for page in pages if page.is_successful)
    error_pages = len(pages) - successful_pages
    internal_links = [link for page in pages for link in page.internal_links]
    external_links = [link for page in pages for link in page.external_links]
    all_links = internal_links + external_links
    unique_external_resources = {
        parsed.netloc.lower()
        for link in external_links
        if (parsed := urlparse(link)).netloc
    }
    unique_file_links = {
        link
        for link in all_links
        if urlparse(link).path.lower().endswith((".doc", ".docx", ".pdf"))
    }
    pages_with_text = sum(1 for page in pages if page.text.strip())
    total_text_length = sum(len(page.text) for page in pages)

    return {
        "total_pages_processed": len(pages),
        "successful_pages": successful_pages,
        "error_pages": error_pages,
        "total_links_found": len(all_links),
        "internal_links_total": len(internal_links),
        "external_links_total": len(external_links),
        "unique_internal_links": len(set(internal_links)),
        "unique_external_links": len(set(external_links)),
        "unique_external_resources": len(unique_external_resources),
        "unique_file_links_doc_docx_pdf": len(unique_file_links),
        "pages_with_text": pages_with_text,
        "total_text_length": total_text_length,
        "total_pages": len(pages),
        "total_links": len(all_links),
        "internal_links": len(internal_links),
        "external_links": len(external_links),
        "top_5_pages_by_links": _top_pages_by_links(pages),
    }


def _top_pages_by_links(pages: list[PageData]) -> list[dict[str, Any]]:
    sorted_pages = sorted(
        pages,
        key=lambda page: (page.total_link_count, page.url),
        reverse=True,
    )
    return [
        {
            "url": page.url,
            "title": page.title,
            "depth": page.depth,
            "total_link_count": page.total_link_count,
            "internal_link_count": page.internal_link_count,
            "external_link_count": page.external_link_count,
        }
        for page in sorted_pages[:5]
    ]
