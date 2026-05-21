"""Utilities for URL normalization and classification."""

from urllib.parse import ParseResult, urldefrag, urljoin, urlparse, urlunparse


IGNORED_SCHEMES = {"mailto", "tel", "javascript"}
ALLOWED_SCHEMES = {"http", "https"}


def should_ignore_href(href: str | None) -> bool:
    """Return True if an href value must not be crawled."""
    if href is None:
        return True

    href = href.strip()
    if not href or href.startswith("#"):
        return True

    parsed = urlparse(href)
    return parsed.scheme.lower() in IGNORED_SCHEMES


def normalize_url(base_url: str, href: str | None) -> str | None:
    """Convert a possibly relative link to a normalized absolute URL.

    The function removes fragments, keeps query strings, lowercases scheme and
    host, adds a slash to an empty path, and ignores non-HTTP(S) links.
    """
    if should_ignore_href(href):
        return None

    joined = urljoin(base_url, href.strip())
    without_fragment, _fragment = urldefrag(joined)
    parsed = urlparse(without_fragment)

    if parsed.scheme.lower() not in ALLOWED_SCHEMES or not parsed.netloc:
        return None

    normalized = _normalize_parsed_url(parsed)
    return urlunparse(normalized)


def is_internal_url(url: str, start_url: str) -> bool:
    """Return True if a URL belongs to the same host as the start URL."""
    normalized_url = normalize_url(url, url)
    normalized_start = normalize_url(start_url, start_url)
    if normalized_url is None or normalized_start is None:
        return False

    parsed_url = urlparse(normalized_url)
    parsed_start = urlparse(normalized_start)
    return _normalized_netloc(parsed_url) == _normalized_netloc(parsed_start)


def unique_preserve_order(urls: list[str]) -> list[str]:
    """Remove duplicates while preserving the original order."""
    seen: set[str] = set()
    result: list[str] = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            result.append(url)
    return result


def _normalize_parsed_url(parsed: ParseResult) -> ParseResult:
    path = parsed.path or "/"
    scheme = parsed.scheme.lower()
    hostname = (parsed.hostname or "").lower()
    port = parsed.port

    if port is None or (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
        netloc = hostname
    else:
        netloc = f"{hostname}:{port}"

    return parsed._replace(scheme=scheme, netloc=netloc, path=path)


def _normalized_netloc(parsed: ParseResult) -> str:
    return _normalize_parsed_url(parsed).netloc

