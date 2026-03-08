"""Tests for postprocess module — API bibliographique (search_book, get_book_metadata)."""

import inspect
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.postprocess import get_book_metadata, search_book


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
