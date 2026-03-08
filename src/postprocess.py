"""Post-processing and result formatting for the ShelfScan pipeline.

Provides functions to query bibliographic APIs (Open Library, Google Books)
for book metadata enrichment of OCR results.
"""

import logging

import requests

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10
SUPPORTED_PROVIDERS = ("openlibrary", "googlebooks")

_OPENLIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"
_OPENLIBRARY_ISBN_URL = "https://openlibrary.org/isbn/{isbn}.json"
_GOOGLEBOOKS_SEARCH_URL = "https://www.googleapis.com/books/v1/volumes"
_GOOGLEBOOKS_ISBN_URL = "https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"


def _validate_query(query: str) -> None:
    """Raise ValueError if query is None or empty."""
    if query is None:
        raise ValueError("query must not be None")
    if not isinstance(query, str) or query.strip() == "":
        raise ValueError("query must be a non-empty string")


def _validate_provider(provider: str) -> None:
    """Raise ValueError if provider is not supported."""
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Unknown provider '{provider}'. "
            f"Supported providers: {SUPPORTED_PROVIDERS}"
        )


def _parse_openlibrary_docs(docs: list[dict]) -> list[dict]:
    """Parse Open Library search docs into standardised book dicts."""
    results: list[dict] = []
    for doc in docs:
        title = doc.get("title")
        if title is None:
            logger.debug("Skipping Open Library doc without title: %s", doc)
            continue
        authors = doc.get("author_name")
        author = authors[0] if authors else None
        isbns = doc.get("isbn")
        isbn = isbns[0] if isbns else None
        results.append({
            "title": title,
            "author": author,
            "isbn": isbn,
            "provider": "openlibrary",
        })
    return results


def _parse_googlebooks_items(items: list[dict]) -> list[dict]:
    """Parse Google Books volume items into standardised book dicts."""
    results: list[dict] = []
    for item in items:
        info = item.get("volumeInfo", {})
        title = info.get("title")
        if title is None:
            logger.debug("Skipping Google Books item without title: %s", item)
            continue
        authors = info.get("authors")
        author = authors[0] if authors else None
        identifiers = info.get("industryIdentifiers", [])
        isbn = None
        for ident in identifiers:
            if ident.get("type") in ("ISBN_13", "ISBN_10"):
                isbn = ident["identifier"]
                break
        results.append({
            "title": title,
            "author": author,
            "isbn": isbn,
            "provider": "googlebooks",
        })
    return results


def search_book(
    query: str,
    provider: str = "openlibrary",
    timeout: int = DEFAULT_TIMEOUT,
) -> list[dict]:
    """Search for a book by title/text via a bibliographic API.

    Args:
        query: Search terms (title, author, etc.).
        provider: API provider -- one of ``SUPPORTED_PROVIDERS``.
        timeout: HTTP request timeout in seconds.

    Returns:
        List of dicts, each containing keys: ``title``, ``author``,
        ``isbn``, ``provider``.

    Raises:
        ValueError: If *query* is empty/None or *provider* is
            unsupported.
        TimeoutError: On request timeout.
        ConnectionError: On HTTP errors (4xx/5xx).
    """
    _validate_query(query)
    _validate_provider(provider)

    try:
        if provider == "openlibrary":
            resp = requests.get(
                _OPENLIBRARY_SEARCH_URL,
                params={"q": query, "limit": 5},
                timeout=timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            docs = data.get("docs", [])
            if not docs:
                logger.debug("Open Library returned no docs for query=%r", query)
            return _parse_openlibrary_docs(docs)

        # provider == "googlebooks"
        resp = requests.get(
            _GOOGLEBOOKS_SEARCH_URL,
            params={"q": query, "maxResults": 5},
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        if not items:
            logger.debug("Google Books returned no items for query=%r", query)
        return _parse_googlebooks_items(items)

    except requests.exceptions.Timeout as exc:
        raise TimeoutError(str(exc)) from exc
    except requests.exceptions.HTTPError as exc:
        raise ConnectionError(str(exc)) from exc


def get_book_metadata(
    isbn: str,
    provider: str = "openlibrary",
    timeout: int = DEFAULT_TIMEOUT,
) -> dict | None:
    """Retrieve book metadata by ISBN.

    Args:
        isbn: The ISBN (10 or 13) to look up.
        provider: API provider -- one of ``SUPPORTED_PROVIDERS``.
        timeout: HTTP request timeout in seconds.

    Returns:
        Book metadata dict, or ``None`` if not found.

    Raises:
        ValueError: If *isbn* is empty/None.
        TimeoutError: On request timeout.
        ConnectionError: On HTTP errors other than 404.
    """
    if isbn is None:
        raise ValueError("isbn must not be None")
    if not isinstance(isbn, str) or isbn.strip() == "":
        raise ValueError("isbn must be a non-empty string")

    _validate_provider(provider)

    try:
        if provider == "openlibrary":
            url = _OPENLIBRARY_ISBN_URL.format(isbn=isbn)
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp.json()

        # provider == "googlebooks"
        url = _GOOGLEBOOKS_ISBN_URL.format(isbn=isbn)
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        if not items:
            logger.debug("Google Books returned no items for isbn=%r", isbn)
            return None
        return _parse_googlebooks_items(items)[0]

    except requests.exceptions.HTTPError as exc:
        if resp.status_code == 404:
            return None
        raise ConnectionError(str(exc)) from exc
    except requests.exceptions.Timeout as exc:
        raise TimeoutError(str(exc)) from exc
