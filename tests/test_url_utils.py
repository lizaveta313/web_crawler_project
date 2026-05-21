from crawler.url_utils import is_internal_url, normalize_url


def test_normalize_relative_url() -> None:
    result = normalize_url("https://example.com/docs/page.html", "../about")

    assert result == "https://example.com/about"


def test_normalize_removes_fragment() -> None:
    result = normalize_url("https://example.com/index.html", "/news#section")

    assert result == "https://example.com/news"


def test_normalize_ignores_invalid_href_schemes() -> None:
    base_url = "https://example.com/"

    assert normalize_url(base_url, "mailto:test@example.com") is None
    assert normalize_url(base_url, "tel:+10000000000") is None
    assert normalize_url(base_url, "javascript:void(0)") is None
    assert normalize_url(base_url, "#content") is None
    assert normalize_url(base_url, "") is None


def test_internal_and_external_links() -> None:
    start_url = "https://example.com"

    assert is_internal_url("https://example.com/about", start_url)
    assert not is_internal_url("https://other.example/about", start_url)


def test_url_with_and_without_slash_normalizes_equally() -> None:
    without_slash = normalize_url("https://example.com", "https://example.com")
    with_slash = normalize_url("https://example.com/", "https://example.com/")

    assert without_slash == "https://example.com/"
    assert with_slash == "https://example.com/"
    assert without_slash == with_slash

