"""Post-processing and result formatting for the ShelfScan pipeline.

Provides functions to query bibliographic APIs (Open Library, Google Books)
for book metadata enrichment of OCR results.
"""

import requests

DEFAULT_TIMEOUT = 10
SUPPORTED_PROVIDERS = ("openlibrary", "googlebooks")

_OPENLIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"
_OPENLIBRARY_ISBN_URL = "https://openlibrary.org/isbn/{isbn}.json"
_GOOGLEBOOKS_SEARCH_URL = "https://www.googleapis.com/books/v1/volumes"


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
        authors = doc.get("author_name")
        author = authors[0] if authors else None
        isbns = doc.get("isbn")
        isbn = isbns[0] if isbns else None
        results.append({
            "title": doc.get("title"),
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
        authors = info.get("authors")
        author = authors[0] if authors else None
        identifiers = info.get("industryIdentifiers", [])
        isbn = None
        for ident in identifiers:
            if ident.get("type") in ("ISBN_13", "ISBN_10"):
                isbn = ident["identifier"]
                break
        results.append({
            "title": info.get("title"),
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

    Parameters
    ----------
    query : str
        Search terms (title, author, etc.).
    provider : str
        API provider — one of ``SUPPORTED_PROVIDERS``.
    timeout : int
        HTTP request timeout in seconds.

    Returns
    -------
    list[dict]
        Each dict contains keys: ``title``, ``author``, ``isbn``, ``provider``.

    Raises
    ------
    ValueError
        If *query* is empty/None or *provider* is unsupported.
    TimeoutError
        On request timeout.
    ConnectionError
        On HTTP errors (4xx/5xx).
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
            return _parse_openlibrary_docs(data.get("docs", []))

        # provider == "googlebooks"
        resp = requests.get(
            _GOOGLEBOOKS_SEARCH_URL,
            params={"q": query, "maxResults": 5},
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return _parse_googlebooks_items(data.get("items", []))

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

    Parameters
    ----------
    isbn : str
        The ISBN (10 or 13) to look up.
    provider : str
        API provider (currently only ``"openlibrary"`` is implemented).
    timeout : int
        HTTP request timeout in seconds.

    Returns
    -------
    dict | None
        Book metadata dict, or ``None`` if not found.

    Raises
    ------
    ValueError
        If *isbn* is empty/None.
    TimeoutError
        On request timeout.
    ConnectionError
        On HTTP errors other than 404.
    """
    if isbn is None:
        raise ValueError("isbn must not be None")
    if not isinstance(isbn, str) or isbn.strip() == "":
        raise ValueError("isbn must be a non-empty string")

    _validate_provider(provider)

    url = _OPENLIBRARY_ISBN_URL.format(isbn=isbn)

    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as exc:
        if resp.status_code == 404:
            return None
        raise ConnectionError(str(exc)) from exc
    except requests.exceptions.Timeout as exc:
        raise TimeoutError(str(exc)) from exc
