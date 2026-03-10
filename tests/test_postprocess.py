"""Tests for postprocess module — API bibliographique (search_book, get_book_metadata)."""

import inspect
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.postprocess import (
    clean_text,
    fuzzy_match_title,
    get_book_metadata,
    identify_book,
    identify_books,
    merge_fragments,
    postprocess_spine,
    search_book,
    split_title_author,
)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _mock_openlibrary_response(docs: list[dict]) -> MagicMock:
    """Build a mock requests.Response for Open Library search endpoint."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"docs": docs}
    mock_resp.raise_for_status.return_value = None
    return mock_resp


def _mock_googlebooks_response(items: list[dict]) -> MagicMock:
    """Build a mock requests.Response for Google Books volumes endpoint."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"totalItems": len(items), "items": items}
    mock_resp.raise_for_status.return_value = None
    return mock_resp


# ---------------------------------------------------------------------------
# search_book — return type
# ---------------------------------------------------------------------------

class TestSearchBookReturnType:
    """search_book retourne list[dict] avec clés title, author, isbn, provider."""

    @patch("src.postprocess.requests.get")
    def test_returns_list_of_dicts_with_expected_keys(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_openlibrary_response([
            {
                "title": "Le Petit Prince",
                "author_name": ["Antoine de Saint-Exupéry"],
                "isbn": ["9782070612758"],
            },
        ])

        results = search_book("Le Petit Prince")

        assert isinstance(results, list)
        assert len(results) >= 1
        for item in results:
            assert isinstance(item, dict)
            assert "title" in item
            assert "author" in item
            assert "isbn" in item
            assert "provider" in item


# ---------------------------------------------------------------------------
# search_book — nominal "Le Petit Prince"
# ---------------------------------------------------------------------------

class TestSearchBookNominal:
    """search_book("Le Petit Prince") avec mock retourne au moins 1 résultat."""

    @patch("src.postprocess.requests.get")
    def test_le_petit_prince_returns_results(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_openlibrary_response([
            {
                "title": "Le Petit Prince",
                "author_name": ["Antoine de Saint-Exupéry"],
                "isbn": ["9782070612758"],
            },
        ])

        results = search_book("Le Petit Prince")

        assert len(results) >= 1
        assert results[0]["title"] == "Le Petit Prince"
        assert results[0]["provider"] == "openlibrary"


# ---------------------------------------------------------------------------
# search_book — empty response
# ---------------------------------------------------------------------------

class TestSearchBookEmptyResponse:
    """search_book avec réponse vide retourne liste vide, pas d'exception."""

    @patch("src.postprocess.requests.get")
    def test_empty_response_returns_empty_list(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_openlibrary_response([])

        results = search_book("xyznonexistent")

        assert results == []


# ---------------------------------------------------------------------------
# search_book — timeout
# ---------------------------------------------------------------------------

class TestSearchBookTimeout:
    """Timeout réseau lève TimeoutError ou requests.exceptions.Timeout."""

    @patch("src.postprocess.requests.get")
    def test_timeout_raises(self, mock_get: MagicMock) -> None:
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        with pytest.raises((TimeoutError, requests.exceptions.Timeout)):
            search_book("Le Petit Prince")


# ---------------------------------------------------------------------------
# search_book — HTTP 5xx
# ---------------------------------------------------------------------------

class TestSearchBookHTTPError:
    """Erreur HTTP 5xx lève ConnectionError ou requests.exceptions.HTTPError."""

    @patch("src.postprocess.requests.get")
    def test_5xx_raises(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "500 Server Error"
        )
        mock_get.return_value = mock_resp

        with pytest.raises((ConnectionError, requests.exceptions.HTTPError)):
            search_book("Le Petit Prince")


# ---------------------------------------------------------------------------
# search_book — validation
# ---------------------------------------------------------------------------

class TestSearchBookValidation:
    """ValueError si query vide/None ou provider inconnu."""

    def test_empty_query_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            search_book("")

    def test_none_query_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            search_book(None)  # type: ignore[arg-type]

    def test_unknown_provider_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            search_book("Le Petit Prince", provider="amazon")


# ---------------------------------------------------------------------------
# search_book — Google Books provider
# ---------------------------------------------------------------------------

class TestSearchBookGoogleBooks:
    """search_book fonctionne avec le provider googlebooks."""

    @patch("src.postprocess.requests.get")
    def test_googlebooks_returns_results(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_googlebooks_response([
            {
                "volumeInfo": {
                    "title": "Le Petit Prince",
                    "authors": ["Antoine de Saint-Exupéry"],
                    "industryIdentifiers": [
                        {"type": "ISBN_13", "identifier": "9782070612758"},
                    ],
                },
            },
        ])

        results = search_book("Le Petit Prince", provider="googlebooks")

        assert len(results) >= 1
        assert results[0]["title"] == "Le Petit Prince"
        assert results[0]["provider"] == "googlebooks"


# ---------------------------------------------------------------------------
# get_book_metadata — return type
# ---------------------------------------------------------------------------

class TestGetBookMetadata:
    """get_book_metadata retourne dict ou None."""

    @patch("src.postprocess.requests.get")
    def test_returns_dict_for_valid_isbn(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "title": "Le Petit Prince",
            "authors": [{"name": "Antoine de Saint-Exupéry"}],
            "isbn_13": ["9782070612758"],
        }
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        result = get_book_metadata("9782070612758")

        assert isinstance(result, dict)

    @patch("src.postprocess.requests.get")
    def test_returns_none_for_not_found(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Not Found"
        )
        mock_get.return_value = mock_resp

        result = get_book_metadata("0000000000000")

        assert result is None

    def test_empty_isbn_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            get_book_metadata("")

    def test_none_isbn_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            get_book_metadata(None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# get_book_metadata — Google Books provider
# ---------------------------------------------------------------------------

class TestGetBookMetadataGoogleBooks:
    """get_book_metadata fonctionne avec le provider googlebooks."""

    @patch("src.postprocess.requests.get")
    def test_googlebooks_returns_dict_for_valid_isbn(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "totalItems": 1,
            "items": [
                {
                    "volumeInfo": {
                        "title": "Le Petit Prince",
                        "authors": ["Antoine de Saint-Exupéry"],
                        "industryIdentifiers": [
                            {"type": "ISBN_13", "identifier": "9782070612758"},
                        ],
                    },
                },
            ],
        }
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        result = get_book_metadata("9782070612758", provider="googlebooks")

        assert isinstance(result, dict)
        assert result["title"] == "Le Petit Prince"
        assert result["provider"] == "googlebooks"
        assert result["isbn"] == "9782070612758"

    @patch("src.postprocess.requests.get")
    def test_googlebooks_returns_none_for_no_items(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"totalItems": 0, "items": []}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        result = get_book_metadata("0000000000000", provider="googlebooks")

        assert result is None

    @patch("src.postprocess.requests.get")
    def test_googlebooks_uses_correct_url(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "totalItems": 1,
            "items": [
                {
                    "volumeInfo": {
                        "title": "Test Book",
                        "authors": ["Author"],
                        "industryIdentifiers": [
                            {"type": "ISBN_13", "identifier": "9781234567890"},
                        ],
                    },
                },
            ],
        }
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        get_book_metadata("9781234567890", provider="googlebooks")

        called_url = mock_get.call_args[0][0]
        assert "googleapis.com" in called_url
        assert "9781234567890" in called_url

    @patch("src.postprocess.requests.get")
    def test_openlibrary_uses_correct_url(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"title": "Test"}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        get_book_metadata("9781234567890", provider="openlibrary")

        called_url = mock_get.call_args[0][0]
        assert "openlibrary.org" in called_url
        assert "9781234567890" in called_url


# ---------------------------------------------------------------------------
# search_book — title filtering
# ---------------------------------------------------------------------------

class TestSearchBookTitleFiltering:
    """search_book filtre les résultats sans titre."""

    @patch("src.postprocess.requests.get")
    def test_openlibrary_skips_docs_without_title(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_openlibrary_response([
            {"title": "Le Petit Prince", "author_name": ["Saint-Ex"], "isbn": ["123"]},
            {"author_name": ["Unknown"], "isbn": ["456"]},
        ])

        results = search_book("Le Petit Prince")

        assert len(results) == 1
        assert results[0]["title"] == "Le Petit Prince"

    @patch("src.postprocess.requests.get")
    def test_googlebooks_skips_items_without_title(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_googlebooks_response([
            {
                "volumeInfo": {
                    "title": "Le Petit Prince",
                    "authors": ["Saint-Ex"],
                    "industryIdentifiers": [{"type": "ISBN_13", "identifier": "123"}],
                },
            },
            {
                "volumeInfo": {
                    "authors": ["Unknown"],
                },
            },
        ])

        results = search_book("Le Petit Prince", provider="googlebooks")

        assert len(results) == 1
        assert results[0]["title"] == "Le Petit Prince"


# ---------------------------------------------------------------------------
# No hardcoded API keys
# ---------------------------------------------------------------------------

class TestNoHardcodedAPIKeys:
    """Aucune clé API hardcodée dans le source postprocess.py."""

    def test_no_api_key_in_source(self) -> None:
        source = inspect.getsource(__import__("src.postprocess", fromlist=["postprocess"]))
        # Check for common API key patterns
        assert "AIza" not in source, "Google API key pattern found in source"
        assert "api_key=" not in source.lower().replace(" ", ""), "api_key assignment found"
        assert "apikey=" not in source.lower().replace(" ", ""), "apikey assignment found"


# ---------------------------------------------------------------------------
# clean_text
# ---------------------------------------------------------------------------


class TestCleanText:
    """Tests for clean_text — nettoyage du texte brut OCR."""

    def test_removes_control_characters(self) -> None:
        result = clean_text("hello\x00world\x01!")
        assert "\x00" not in result
        assert "\x01" not in result
        assert "helloworld!" in result

    def test_normalizes_multiple_spaces(self) -> None:
        result = clean_text("hello   world")
        assert result == "hello world"

    def test_applies_nfc_normalization(self) -> None:
        import unicodedata

        # e + combining accent (NFD) should become single char (NFC)
        nfd_text = unicodedata.normalize("NFD", "\u00e9")  # e + combining accent
        result = clean_text(nfd_text)
        assert result == unicodedata.normalize("NFC", nfd_text)

    def test_empty_string_returns_empty(self) -> None:
        result = clean_text("")
        assert result == ""

    def test_strips_whitespace(self) -> None:
        result = clean_text("  hello  ")
        assert result == "hello"

    def test_removes_pipe_characters(self) -> None:
        """Pipe characters (common OCR artefact) are removed."""
        result = clean_text("|Le Petit| Prince|")
        assert result == "Le Petit Prince"


# ---------------------------------------------------------------------------
# merge_fragments
# ---------------------------------------------------------------------------


class TestMergeFragments:
    """Tests for merge_fragments — fusion de fragments de texte."""

    def test_joins_fragments_with_spaces(self) -> None:
        result = merge_fragments(["hello", "world"])
        assert result == "hello world"

    def test_handles_hyphen_word_break(self) -> None:
        result = merge_fragments(["pro-", "gramming"])
        assert result == "programming"

    def test_empty_list_returns_empty(self) -> None:
        result = merge_fragments([])
        assert result == ""

    def test_single_fragment(self) -> None:
        result = merge_fragments(["hello"])
        assert result == "hello"


# ---------------------------------------------------------------------------
# split_title_author
# ---------------------------------------------------------------------------


class TestSplitTitleAuthor:
    """Tests for split_title_author — separation titre/auteur."""

    def test_multiline_split(self) -> None:
        result = split_title_author("LE PETIT PRINCE\nAntoine de Saint-Exupéry")
        assert isinstance(result, dict)
        assert result["title"] == "LE PETIT PRINCE"
        assert result["author"] == "Antoine de Saint-Exupéry"

    def test_single_line_returns_author_none(self) -> None:
        result = split_title_author("LE PETIT PRINCE")
        assert result["title"] == "LE PETIT PRINCE"
        assert result["author"] is None

    def test_empty_string(self) -> None:
        result = split_title_author("")
        assert result["title"] == ""
        assert result["author"] is None

    def test_returns_dict_with_expected_keys(self) -> None:
        result = split_title_author("Title")
        assert "title" in result
        assert "author" in result


# ---------------------------------------------------------------------------
# postprocess_spine
# ---------------------------------------------------------------------------


class TestPostprocessSpine:
    """Tests for postprocess_spine — pipeline orchestration."""

    def test_full_pipeline(self) -> None:
        result = postprocess_spine(["LE PETIT", "PRINCE\nSaint-Exupéry"])
        assert isinstance(result, dict)
        assert "raw_text" in result
        assert "clean_text" in result
        assert "title" in result
        assert "author" in result

    def test_empty_fragments(self) -> None:
        result = postprocess_spine([])
        assert result["raw_text"] == ""
        assert result["clean_text"] == ""
        assert result["title"] == ""
        assert result["author"] is None

    def test_single_fragment_no_author(self) -> None:
        result = postprocess_spine(["LE PETIT PRINCE"])
        assert result["title"] == "LE PETIT PRINCE"
        assert result["author"] is None


# ---------------------------------------------------------------------------
# fuzzy_match_title
# ---------------------------------------------------------------------------


class TestFuzzyMatchTitle:
    """Tests for fuzzy_match_title — matching OCR text to API candidates."""

    def test_best_match_returned(self) -> None:
        candidates = [
            {
                "title": "Le Petit Prince", "author": "Saint-Exupéry",
                "isbn": "123", "provider": "openlibrary",
            },
            {
                "title": "Le Grand Meaulnes", "author": "Alain-Fournier",
                "isbn": "456", "provider": "openlibrary",
            },
        ]
        result = fuzzy_match_title("Le Petit Prince", candidates)
        assert result is not None
        assert result["title"] == "Le Petit Prince"
        assert "match_score" in result
        assert result["match_score"] >= 60.0

    def test_returns_none_when_below_threshold(self) -> None:
        candidates = [
            {
                "title": "Completely Different Book",
                "author": "Author", "isbn": "789",
                "provider": "openlibrary",
            },
        ]
        result = fuzzy_match_title("Le Petit Prince", candidates, threshold=95.0)
        assert result is None

    def test_empty_candidates_returns_none(self) -> None:
        result = fuzzy_match_title("Le Petit Prince", [])
        assert result is None

    def test_empty_text_returns_none(self) -> None:
        candidates = [
            {
                "title": "Le Petit Prince", "author": "Saint-Exupéry",
                "isbn": "123", "provider": "openlibrary",
            },
        ]
        result = fuzzy_match_title("", candidates)
        assert result is None


# ---------------------------------------------------------------------------
# identify_book
# ---------------------------------------------------------------------------


class TestIdentifyBook:
    """Tests for identify_book — orchestration search_book + fuzzy_match."""

    @patch("src.postprocess.search_book")
    def test_orchestration_returns_enriched_dict(self, mock_search: MagicMock) -> None:
        mock_search.return_value = [
            {
                "title": "Le Petit Prince",
                "author": "Saint-Exupéry",
                "isbn": "9782070612758",
                "provider": "openlibrary",
            },
        ]
        result = identify_book("Le Petit Prince")
        assert result is not None
        assert "title" in result
        assert "author" in result
        assert "isbn" in result
        assert "confidence" in result
        assert "provider" in result
        assert 0.0 <= result["confidence"] <= 1.0
        mock_search.assert_called_once()

    @patch("src.postprocess.search_book")
    def test_returns_none_when_no_results(self, mock_search: MagicMock) -> None:
        mock_search.return_value = []
        result = identify_book("xyznonexistent")
        assert result is None

    def test_returns_none_for_empty_text(self) -> None:
        result = identify_book("")
        assert result is None


# ---------------------------------------------------------------------------
# identify_books
# ---------------------------------------------------------------------------


class TestIdentifyBooks:
    """Tests for identify_books — batch identification."""

    @patch("src.postprocess.search_book")
    def test_processes_list_correctly(self, mock_search: MagicMock) -> None:
        mock_search.return_value = [
            {
                "title": "Le Petit Prince", "author": "Saint-Exupéry",
                "isbn": "123", "provider": "openlibrary",
            },
        ]
        spine_results = [
            {
                "raw_text": "Le Petit Prince",
                "clean_text": "Le Petit Prince",
                "title": "Le Petit Prince", "author": None,
            },
            {
                "raw_text": "Les Misérables",
                "clean_text": "Les Misérables",
                "title": "Les Misérables", "author": None,
            },
        ]
        results = identify_books(spine_results)
        assert isinstance(results, list)
        assert len(results) == 2
