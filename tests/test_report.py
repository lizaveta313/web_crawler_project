from crawler.models import PageData
from crawler.report import build_report


def make_pages() -> list[PageData]:
    return [
        PageData(
            url="https://example.com/",
            status_code=200,
            title="Home",
            depth=0,
            text="Home text",
            internal_links=["https://example.com/a", "https://example.com/b"],
            external_links=["https://external.test/", "https://files.test/report.pdf"],
        ),
        PageData(
            url="https://example.com/a",
            status_code=200,
            title="A",
            depth=1,
            text="",
            internal_links=["https://example.com/b"],
            external_links=["https://files.test/document.docx"],
        ),
        PageData(
            url="https://example.com/b",
            status_code=500,
            title="",
            depth=1,
            text="",
            internal_links=[],
            external_links=["https://files.test/scan.doc"],
            error="HTTP status 500",
        ),
    ]


def test_report_counts_pages() -> None:
    report = build_report(make_pages())

    assert report["total_pages_processed"] == 3
    assert report["total_pages"] == 3


def test_report_counts_successful_and_error_pages() -> None:
    report = build_report(make_pages())

    assert report["successful_pages"] == 2
    assert report["error_pages"] == 1


def test_report_counts_internal_and_external_links() -> None:
    report = build_report(make_pages())

    assert report["total_links_found"] == 7
    assert report["internal_links_total"] == 3
    assert report["external_links_total"] == 4
    assert report["total_links"] == 7
    assert report["internal_links"] == 3
    assert report["external_links"] == 4
    assert report["unique_internal_links"] == 2
    assert report["unique_external_links"] == 4


def test_report_counts_text_metrics() -> None:
    report = build_report(make_pages())

    assert report["pages_with_text"] == 1
    assert report["total_text_length"] == len("Home text")


def test_report_counts_file_links_and_external_resources() -> None:
    report = build_report(make_pages())

    assert report["unique_file_links_doc_docx_pdf"] == 3
    assert report["unique_external_resources"] == 2


def test_report_builds_top_5_pages() -> None:
    pages = [
        PageData(url=f"https://example.com/{index}", status_code=200, title=str(index), depth=0, internal_links=["x"] * index)
        for index in range(1, 8)
    ]

    report = build_report(pages)
    top_pages = report["top_5_pages_by_links"]

    assert len(top_pages) == 5
    assert top_pages[0]["url"] == "https://example.com/7"
    assert top_pages[0]["total_link_count"] == 7
    assert top_pages[-1]["url"] == "https://example.com/3"
