from crawler.parser import HtmlParser


def test_extracts_title() -> None:
    html = "<html><head><title> Test page </title></head><body></body></html>"

    parsed = HtmlParser().parse(html, "https://example.com/", "https://example.com/")

    assert parsed.title == "Test page"


def test_extracts_internal_and_external_links() -> None:
    html = """
    <html>
      <head><title>Links</title></head>
      <body>
        <a href="/about">About</a>
        <a href="https://example.com/contact#team">Contact</a>
        <a href="https://external.test/news">External</a>
      </body>
    </html>
    """

    parsed = HtmlParser().parse(html, "https://example.com/", "https://example.com/")

    assert parsed.internal_links == [
        "https://example.com/about",
        "https://example.com/contact",
    ]
    assert parsed.external_links == ["https://external.test/news"]


def test_ignores_invalid_links() -> None:
    html = """
    <a href="mailto:test@example.com">Email</a>
    <a href="tel:+10000000000">Phone</a>
    <a href="javascript:void(0)">JS</a>
    <a href="#top">Top</a>
    <a>No href</a>
    """

    parsed = HtmlParser().parse(html, "https://example.com/", "https://example.com/")

    assert parsed.internal_links == []
    assert parsed.external_links == []


def test_handles_html_without_title() -> None:
    html = "<html><body><a href='/about'>About</a></body></html>"

    parsed = HtmlParser().parse(html, "https://example.com/", "https://example.com/")

    assert parsed.title == ""
    assert parsed.internal_links == ["https://example.com/about"]

