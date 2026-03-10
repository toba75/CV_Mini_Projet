"""Tests pour les diapositives de soutenance ShelfScan (#033)."""

import pathlib

SLIDES_DIR = pathlib.Path("docs/slides")
SOUTENANCE_FILE = SLIDES_DIR / "soutenance.md"
NOTES_FILE = SLIDES_DIR / "notes_orateur.md"


class TestSlidesDirectoryExists:
    """#033 — Le répertoire docs/slides/ existe."""

    def test_slides_directory_exists(self):
        assert SLIDES_DIR.is_dir(), f"{SLIDES_DIR} n'existe pas"


class TestSoutenanceFile:
    """#033 — Fichier soutenance.md."""

    def test_soutenance_file_exists(self):
        assert SOUTENANCE_FILE.is_file(), f"{SOUTENANCE_FILE} n'existe pas"

    def test_soutenance_has_marp_frontmatter(self):
        content = SOUTENANCE_FILE.read_text(encoding="utf-8")
        assert "marp: true" in content, "Le fichier doit contenir la directive Marp"

    def test_soutenance_has_approximately_10_slides(self):
        content = SOUTENANCE_FILE.read_text(encoding="utf-8")
        # Count slide separators (---) that are on their own line
        # The frontmatter uses --- too, so we count separators after the frontmatter
        lines = content.split("\n")
        # Skip frontmatter block (first --- to second ---)
        separator_count = 0
        in_frontmatter = False
        frontmatter_ended = False
        for line in lines:
            stripped = line.strip()
            if stripped == "---":
                if not in_frontmatter and not frontmatter_ended:
                    in_frontmatter = True
                elif in_frontmatter:
                    in_frontmatter = False
                    frontmatter_ended = True
                else:
                    separator_count += 1
        # ~10 slides means ~9 separators between them (slide 1 | --- | slide 2 | ... )
        assert separator_count >= 8, (
            f"Attendu au moins 8 séparateurs (≈9-10 diapositives), trouvé {separator_count}"
        )
        assert separator_count <= 12, (
            f"Trop de séparateurs ({separator_count}), attendu ~9-10"
        )

    def test_soutenance_contains_keyword_architecture(self):
        content = SOUTENANCE_FILE.read_text(encoding="utf-8").lower()
        assert "architecture" in content

    def test_soutenance_contains_keyword_pipeline(self):
        content = SOUTENANCE_FILE.read_text(encoding="utf-8").lower()
        assert "pipeline" in content

    def test_soutenance_contains_keyword_ocr(self):
        content = SOUTENANCE_FILE.read_text(encoding="utf-8").upper()
        assert "OCR" in content

    def test_soutenance_contains_keyword_resultats(self):
        content = SOUTENANCE_FILE.read_text(encoding="utf-8").lower()
        assert "résultats" in content or "resultats" in content

    def test_soutenance_contains_keyword_limites(self):
        content = SOUTENANCE_FILE.read_text(encoding="utf-8").lower()
        assert "limites" in content

    def test_soutenance_contains_metrics_table(self):
        """Les résultats quantitatifs doivent inclure un tableau de métriques."""
        content = SOUTENANCE_FILE.read_text(encoding="utf-8")
        assert "CER" in content, "Le tableau doit mentionner le CER"
        assert "détection" in content.lower() or "detection" in content.lower(), (
            "Le tableau doit mentionner le taux de détection"
        )
        assert "identification" in content.lower(), (
            "Le tableau doit mentionner le taux d'identification"
        )

    def test_soutenance_contains_pipeline_steps(self):
        """Toutes les étapes du pipeline doivent être mentionnées."""
        content = SOUTENANCE_FILE.read_text(encoding="utf-8").lower()
        assert "prétraitement" in content or "pretraitement" in content
        assert "segmentation" in content
        assert "détection" in content or "detection" in content
        assert "post-traitement" in content or "posttraitement" in content

    def test_soutenance_mentions_ocr_models(self):
        """La comparaison des modèles OCR doit être présente."""
        content = SOUTENANCE_FILE.read_text(encoding="utf-8")
        assert "PaddleOCR" in content
        assert "TrOCR" in content
        assert "Tesseract" in content

    def test_soutenance_in_french(self):
        """Le contenu doit être en français."""
        content = SOUTENANCE_FILE.read_text(encoding="utf-8").lower()
        # Check for common French words that would appear in a presentation
        french_markers = ["problématique", "conclusion", "perspectives", "résultats"]
        found = sum(1 for m in french_markers if m in content)
        assert found >= 3, f"Contenu insuffisamment en français (trouvé {found}/4 marqueurs)"


class TestNotesOrateurFile:
    """#033 — Fichier notes_orateur.md."""

    def test_notes_file_exists(self):
        assert NOTES_FILE.is_file(), f"{NOTES_FILE} n'existe pas"

    def test_notes_contains_question_ocr_model(self):
        content = NOTES_FILE.read_text(encoding="utf-8")
        assert "pourquoi" in content.lower() and "ocr" in content.upper(), (
            "Doit contenir la question sur le choix du modèle OCR"
        )

    def test_notes_contains_question_vertical_text(self):
        content = NOTES_FILE.read_text(encoding="utf-8").lower()
        assert "vertical" in content, (
            "Doit contenir la question sur le texte vertical"
        )

    def test_notes_contains_question_limits(self):
        content = NOTES_FILE.read_text(encoding="utf-8").lower()
        assert "limites" in content, (
            "Doit contenir la question sur les limites"
        )

    def test_notes_contains_question_improvements(self):
        content = NOTES_FILE.read_text(encoding="utf-8").lower()
        assert "améliorer" in content or "ameliorer" in content, (
            "Doit contenir la question sur l'amélioration des résultats"
        )

    def test_notes_has_substantive_answers(self):
        """Les réponses doivent être substantielles (pas juste les questions)."""
        content = NOTES_FILE.read_text(encoding="utf-8")
        # Each answer should have some substance — at least 500 chars total
        assert len(content) >= 500, (
            f"Notes trop courtes ({len(content)} chars), attendu au moins 500"
        )


class TestCoherenceWithReadme:
    """#033 — Cohérence entre slides et README."""

    def test_slides_mention_same_stack(self):
        """Les technologies mentionnées dans les slides doivent être cohérentes."""
        content = SOUTENANCE_FILE.read_text(encoding="utf-8")
        assert "OpenCV" in content or "opencv" in content.lower()
        assert "Streamlit" in content or "streamlit" in content.lower()

    def test_slides_metrics_plausible(self):
        """Les métriques dans les slides doivent être dans des ranges plausibles."""
        content = SOUTENANCE_FILE.read_text(encoding="utf-8")
        # Check that percentage values are mentioned (at least some numbers with %)
        import re

        percentages = re.findall(r"(\d+)\s*%", content)
        assert len(percentages) >= 2, (
            f"Attendu au moins 2 valeurs en pourcentage, trouvé {len(percentages)}"
        )
