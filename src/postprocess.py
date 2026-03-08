"""Post-processing and result formatting for the ShelfScan pipeline.

Provides functions to query bibliographic APIs (Open Library, Google Books)
for book metadata enrichment of OCR results.
"""

import logging
import re
import unicodedata

import requests
from rapidfuzz import fuzz

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


def clean_text(raw_text: str) -> str:
    """Clean raw OCR text.

    Removes control characters, normalizes multiple spaces to a single
    space, applies Unicode NFC normalization, and strips leading/trailing
    whitespace.

    Args:
        raw_text: Raw text string from OCR.

    Returns:
        Cleaned text string.
    """
    if not raw_text:
        return ""
    # Remove control characters (category Cc) except common whitespace
    cleaned = "".join(
        ch if unicodedata.category(ch) != "Cc" or ch in ("\n", "\t") else ""
        for ch in raw_text
    )
    # Normalize multiple spaces to single space
    cleaned = re.sub(r" {2,}", " ", cleaned)
    # Apply NFC normalization
    cleaned = unicodedata.normalize("NFC", cleaned)
    # Strip leading/trailing whitespace
    return cleaned.strip()


def merge_fragments(fragments: list[str]) -> str:
    """Merge text fragments from the same spine into a single string.

    Handles word breaks at end of lines (hyphen followed by next fragment).

    Args:
        fragments: List of text strings from OCR on the same spine.

    Returns:
        Merged text string, or empty string for empty list.
    """
    if not fragments:
        return ""
    result = fragments[0]
    for frag in fragments[1:]:
        if result.endswith("-"):
            # Join hyphenated word break
            result = result[:-1] + frag
        else:
            result = result + " " + frag
    return result


def split_title_author(text: str) -> dict[str, str | None]:
    """Split a spine text into title and author using heuristics.

    Heuristics:
    - If text contains a newline, the first part is the title and the
      second part is the author.
    - If single line, title is the full text and author is None.

    Args:
        text: Cleaned spine text.

    Returns:
        Dict with keys ``"title"`` (str) and ``"author"`` (str | None).
    """
    if not text:
        return {"title": "", "author": None}
    if "\n" in text:
        parts = text.split("\n", 1)
        title = parts[0].strip()
        author = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
        return {"title": title, "author": author}
    return {"title": text, "author": None}


def postprocess_spine(raw_texts: list[str]) -> dict[str, str | None]:
    """Orchestrate the full post-processing pipeline for a spine.

    Pipeline: merge_fragments -> clean_text -> split_title_author.

    Args:
        raw_texts: List of raw OCR text fragments from one spine.

    Returns:
        Dict with keys ``"raw_text"``, ``"clean_text"``, ``"title"``,
        ``"author"``.
    """
    raw_text = merge_fragments(raw_texts)
    cleaned = clean_text(raw_text)
    split = split_title_author(cleaned)
    return {
        "raw_text": raw_text,
        "clean_text": cleaned,
        "title": split["title"],
        "author": split["author"],
    }


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


def fuzzy_match_title(
    ocr_text: str,
    candidates: list[dict],
    threshold: float = 60.0,
) -> dict | None:
    """Find the best fuzzy match for OCR text among API candidates.

    Args:
        ocr_text: Text extracted by OCR.
        candidates: List of book dicts with at least a ``"title"`` key.
        threshold: Minimum ``rapidfuzz.fuzz.ratio`` score to accept.

    Returns:
        Best matching candidate dict with an added ``"match_score"`` key,
        or ``None`` if no candidate meets the threshold.
    """
    if not ocr_text or not candidates:
        return None

    best_score = 0.0
    best_candidate = None

    for candidate in candidates:
        score = fuzz.ratio(ocr_text, candidate["title"])
        if score > best_score:
            best_score = score
            best_candidate = candidate

    if best_score < threshold or best_candidate is None:
        return None

    result = {**best_candidate, "match_score": best_score}
    return result


def identify_book(
    ocr_text: str,
    provider: str = "openlibrary",
    threshold: float = 60.0,
) -> dict | None:
    """Identify a book from OCR text using API search and fuzzy matching.

    Orchestrates :func:`search_book` and :func:`fuzzy_match_title`.

    Args:
        ocr_text: Text extracted by OCR from a spine.
        provider: Bibliographic API provider.
        threshold: Minimum fuzzy match score.

    Returns:
        Dict with keys ``title``, ``author``, ``isbn``, ``confidence``,
        ``provider``, or ``None`` if no match found.
    """
    if not ocr_text:
        return None

    candidates = search_book(ocr_text, provider=provider)
    match = fuzzy_match_title(ocr_text, candidates, threshold=threshold)

    if match is None:
        return None

    return {
        "title": match["title"],
        "author": match.get("author"),
        "isbn": match.get("isbn"),
        "confidence": match["match_score"] / 100.0,
        "provider": match.get("provider", provider),
    }


def identify_books(
    spine_results: list[dict],
    provider: str = "openlibrary",
    threshold: float = 60.0,
) -> list[dict]:
    """Identify books for a list of spine post-processing results.

    Calls :func:`identify_book` for each spine result's ``"title"``
    field and merges identification data back into the spine dict.

    Args:
        spine_results: List of dicts from :func:`postprocess_spine`.
        provider: Bibliographic API provider.
        threshold: Minimum fuzzy match score.

    Returns:
        Enriched list of spine result dicts.
    """
    enriched: list[dict] = []
    for spine in spine_results:
        result = {**spine}
        title = spine.get("title", "")
        identification = identify_book(title, provider=provider, threshold=threshold)
        if identification is not None:
            result.update(identification)
        enriched.append(result)
    return enriched
