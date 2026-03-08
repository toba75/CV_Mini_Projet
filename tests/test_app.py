"""Tests pour l'interface Streamlit ShelfScan complète (src/app.py)."""

from pathlib import Path

import pandas as pd
import pytest

APP_PATH = Path(__file__).resolve().parent.parent / "src" / "app.py"


# ---------------------------------------------------------------------------
# Structural tests (source-level)
# ---------------------------------------------------------------------------
class TestAppFileExists:
    """Vérifie que le fichier src/app.py existe."""

    def test_app_file_exists(self):
        assert APP_PATH.is_file(), "src/app.py n'existe pas"


class TestAppImports:
    """Vérifie les imports du fichier app.py."""

    @pytest.fixture()
    def source(self):
        return APP_PATH.read_text(encoding="utf-8")

    def test_imports_streamlit(self, source):
        assert "import streamlit" in source, "app.py doit importer streamlit"

    def test_no_cv2_import(self, source):
        lines = source.splitlines()
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            assert "import cv2" not in stripped, (
                "app.py ne doit pas importer cv2 (logique de traitement)"
            )

    def test_no_numpy_import(self, source):
        lines = source.splitlines()
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            assert "import numpy" not in stripped, (
                "app.py ne doit pas importer numpy (logique de traitement)"
            )


class TestAppContent:
    """Vérifie le contenu structurel de app.py."""

    @pytest.fixture()
    def source(self):
        return APP_PATH.read_text(encoding="utf-8")

    def test_contains_title_shelfscan(self, source):
        assert "ShelfScan" in source, "app.py doit contenir le titre ShelfScan"

    def test_contains_file_uploader(self, source):
        assert "file_uploader" in source, "app.py doit contenir un file_uploader"

    def test_contains_st_image(self, source):
        assert "st.image" in source, "app.py doit contenir st.image"

    def test_accepts_jpeg(self, source):
        assert "jpeg" in source.lower(), "app.py doit accepter le format jpeg"

    def test_accepts_png(self, source):
        assert "png" in source.lower(), "app.py doit accepter le format png"

    def test_contains_tabs(self, source):
        assert "st.tabs" in source, "app.py doit contenir st.tabs pour les onglets"

    def test_contains_five_tab_names(self, source):
        for tab_name in ["Original", "Prétraitement", "Segmentation", "OCR", "Inventaire"]:
            assert tab_name in source, f"app.py doit contenir l'onglet '{tab_name}'"

    def test_contains_progress(self, source):
        assert "st.progress" in source, "app.py doit contenir st.progress"

    def test_contains_dataframe(self, source):
        assert "st.dataframe" in source, "app.py doit contenir st.dataframe"

    def test_contains_download_button(self, source):
        assert "download_button" in source, (
            "app.py doit contenir un bouton de téléchargement CSV"
        )


class TestAppFrenchLabels:
    """Vérifie que les labels de l'interface sont en français."""

    @pytest.fixture()
    def source(self):
        return APP_PATH.read_text(encoding="utf-8")

    def test_french_labels_present(self, source):
        french_words = ["image", "Choisir", "Résultats", "Inventaire"]
        found = [w for w in french_words if w in source]
        assert len(found) >= 3, (
            f"app.py doit contenir des labels en français, trouvés : {found}"
        )


class TestAppNoPrint:
    """Vérifie qu'il n'y a pas de print() de debug."""

    @pytest.fixture()
    def source(self):
        return APP_PATH.read_text(encoding="utf-8")

    def test_no_print_statements(self, source):
        lines = source.splitlines()
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            assert not stripped.startswith("print("), (
                f"Ligne {i}: print() interdit dans app.py (utiliser logging)"
            )


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------
class TestPrepareOcrDisplayData:
    """Tests pour prepare_ocr_display_data."""

    def test_import(self):
        from src.app import prepare_ocr_display_data
        assert callable(prepare_ocr_display_data)

    def test_returns_list(self):
        from src.app import prepare_ocr_display_data
        result = {
            "books": [
                {
                    "spine_id": 1,
                    "raw_text": "Le Petit Prince",
                    "title": "Le Petit Prince",
                    "author": "Saint-Exupéry",
                    "isbn": "978-2070612758",
                    "confidence": 0.95,
                },
            ],
        }
        data = prepare_ocr_display_data(result)
        assert isinstance(data, list)

    def test_contains_spine_id_and_text(self):
        from src.app import prepare_ocr_display_data
        result = {
            "books": [
                {
                    "spine_id": 1,
                    "raw_text": "Le Petit Prince",
                    "title": "Le Petit Prince",
                    "author": "Saint-Exupéry",
                    "isbn": None,
                    "confidence": 0.85,
                },
                {
                    "spine_id": 2,
                    "raw_text": "Les Misérables",
                    "title": "Les Misérables",
                    "author": "Victor Hugo",
                    "isbn": None,
                    "confidence": 0.72,
                },
            ],
        }
        data = prepare_ocr_display_data(result)
        assert len(data) == 2
        assert data[0]["spine_id"] == 1
        assert data[0]["raw_text"] == "Le Petit Prince"
        assert data[0]["confidence"] == 0.85
        assert data[1]["spine_id"] == 2

    def test_empty_books(self):
        from src.app import prepare_ocr_display_data
        result = {"books": []}
        data = prepare_ocr_display_data(result)
        assert data == []

    def test_missing_books_key_raises(self):
        from src.app import prepare_ocr_display_data
        with pytest.raises(KeyError):
            prepare_ocr_display_data({})


class TestPrepareInventoryDataframe:
    """Tests pour prepare_inventory_dataframe."""

    def test_import(self):
        from src.app import prepare_inventory_dataframe
        assert callable(prepare_inventory_dataframe)

    def test_returns_dataframe(self):
        from src.app import prepare_inventory_dataframe
        result = {
            "books": [
                {
                    "spine_id": 1,
                    "raw_text": "Le Petit Prince",
                    "title": "Le Petit Prince",
                    "author": "Saint-Exupéry",
                    "isbn": "978-2070612758",
                    "confidence": 0.95,
                },
            ],
        }
        df = prepare_inventory_dataframe(result)
        assert isinstance(df, pd.DataFrame)

    def test_dataframe_columns(self):
        from src.app import prepare_inventory_dataframe
        result = {
            "books": [
                {
                    "spine_id": 1,
                    "raw_text": "text",
                    "title": "Titre",
                    "author": "Auteur",
                    "isbn": "123",
                    "confidence": 0.9,
                },
            ],
        }
        df = prepare_inventory_dataframe(result)
        expected_cols = {"Titre", "Auteur", "ISBN", "Confiance"}
        assert expected_cols.issubset(set(df.columns)), (
            f"Colonnes attendues {expected_cols}, obtenues {set(df.columns)}"
        )

    def test_dataframe_row_count(self):
        from src.app import prepare_inventory_dataframe
        result = {
            "books": [
                {"spine_id": 1, "raw_text": "a", "title": "T1", "author": "A1", "isbn": None, "confidence": 0.5},
                {"spine_id": 2, "raw_text": "b", "title": "T2", "author": "A2", "isbn": None, "confidence": 0.7},
                {"spine_id": 3, "raw_text": "c", "title": "T3", "author": "A3", "isbn": "X", "confidence": 0.9},
            ],
        }
        df = prepare_inventory_dataframe(result)
        assert len(df) == 3

    def test_dataframe_values(self):
        from src.app import prepare_inventory_dataframe
        result = {
            "books": [
                {
                    "spine_id": 1,
                    "raw_text": "raw",
                    "title": "Mon Titre",
                    "author": "Mon Auteur",
                    "isbn": "978-123",
                    "confidence": 0.88,
                },
            ],
        }
        df = prepare_inventory_dataframe(result)
        assert df.iloc[0]["Titre"] == "Mon Titre"
        assert df.iloc[0]["Auteur"] == "Mon Auteur"
        assert df.iloc[0]["ISBN"] == "978-123"
        assert df.iloc[0]["Confiance"] == 0.88

    def test_empty_books(self):
        from src.app import prepare_inventory_dataframe
        result = {"books": []}
        df = prepare_inventory_dataframe(result)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_missing_books_key_raises(self):
        from src.app import prepare_inventory_dataframe
        with pytest.raises(KeyError):
            prepare_inventory_dataframe({})


class TestMainImportable:
    """Vérifie que main() est importable sans erreur."""

    def test_main_importable(self):
        from src.app import main
        assert callable(main)


# ---------------------------------------------------------------------------
# Manual correction helpers tests (task 026)
# ---------------------------------------------------------------------------
def _make_pipeline_result(books=None):
    """Crée un résultat de pipeline minimal pour les tests."""
    if books is None:
        books = [
            {
                "spine_id": 1,
                "raw_text": "Le Ptit Prince",
                "title": "Le Ptit Prince",
                "author": "St-Exupéry",
                "isbn": "978-2070612758",
                "confidence": 0.85,
            },
            {
                "spine_id": 2,
                "raw_text": "Les Misrables",
                "title": "Les Misrables",
                "author": "V. Hugo",
                "isbn": None,
                "confidence": 0.72,
            },
        ]
    return {"books": books}


class TestApplyManualCorrections:
    """Tests pour apply_manual_corrections."""

    def test_apply_manual_corrections_nominal(self):
        from src.app import apply_manual_corrections

        result = _make_pipeline_result()
        corrections = {
            1: {"title": "Le Petit Prince", "author": "Antoine de Saint-Exupéry"},
        }
        corrected = apply_manual_corrections(result, corrections)

        # Le résultat corrigé doit avoir les nouvelles valeurs
        book1 = corrected["books"][0]
        assert book1["title"] == "Le Petit Prince"
        assert book1["author"] == "Antoine de Saint-Exupéry"
        assert book1["manually_corrected"] is True

        # Le livre non corrigé garde ses valeurs d'origine
        book2 = corrected["books"][1]
        assert book2["title"] == "Les Misrables"
        assert book2["author"] == "V. Hugo"
        assert book2.get("manually_corrected") is not True

    def test_apply_manual_corrections_unknown_spine_id(self):
        from src.app import apply_manual_corrections

        result = _make_pipeline_result()
        corrections = {
            999: {"title": "Fantôme"},
        }
        # Les spine_id inconnus sont ignorés silencieusement
        corrected = apply_manual_corrections(result, corrections)
        assert len(corrected["books"]) == 2
        # Aucun livre ne doit être marqué comme corrigé
        for book in corrected["books"]:
            assert book.get("manually_corrected") is not True

    def test_apply_manual_corrections_empty_corrections(self):
        from src.app import apply_manual_corrections

        result = _make_pipeline_result()
        corrected = apply_manual_corrections(result, {})

        # Résultat identique à l'original
        assert len(corrected["books"]) == 2
        for book in corrected["books"]:
            assert book.get("manually_corrected") is not True

    def test_apply_manual_corrections_does_not_mutate_original(self):
        from src.app import apply_manual_corrections

        result = _make_pipeline_result()
        original_title = result["books"][0]["title"]
        corrections = {1: {"title": "Nouveau Titre"}}
        apply_manual_corrections(result, corrections)

        # L'original ne doit pas être modifié
        assert result["books"][0]["title"] == original_title


class TestPrepareEditableDataframe:
    """Tests pour prepare_editable_dataframe."""

    def test_prepare_editable_dataframe(self):
        from src.app import prepare_editable_dataframe

        result = _make_pipeline_result(
            books=[
                {
                    "spine_id": 1,
                    "raw_text": "Le Petit Prince",
                    "title": "Le Petit Prince",
                    "author": "Saint-Exupéry",
                    "isbn": "978-2070612758",
                    "confidence": 0.95,
                    "manually_corrected": True,
                },
                {
                    "spine_id": 2,
                    "raw_text": "Les Misérables",
                    "title": "Les Misérables",
                    "author": "Victor Hugo",
                    "isbn": None,
                    "confidence": 0.72,
                },
            ]
        )
        df = prepare_editable_dataframe(result)

        assert isinstance(df, pd.DataFrame)
        expected_cols = {"Titre", "Auteur", "ISBN", "Confiance", "Modifié"}
        assert expected_cols.issubset(set(df.columns)), (
            f"Colonnes attendues {expected_cols}, obtenues {set(df.columns)}"
        )
        assert len(df) == 2
        # Le premier livre est marqué comme modifié
        assert bool(df.iloc[0]["Modifié"]) is True
        # Le deuxième livre n'est pas modifié
        assert bool(df.iloc[1]["Modifié"]) is False

    def test_prepare_editable_dataframe_empty(self):
        from src.app import prepare_editable_dataframe

        result = {"books": []}
        df = prepare_editable_dataframe(result)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
