"""Tests pour le scaffold Streamlit ShelfScan (src/app.py)."""

from pathlib import Path

import pytest

APP_PATH = Path(__file__).resolve().parent.parent / "src" / "app.py"


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
