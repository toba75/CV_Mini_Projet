"""Tests pour le README final du projet ShelfScan.

Tâche #032 — Vérification de l'existence et de la structure du README.md.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
README_PATH = ROOT / "README.md"


@pytest.fixture()
def readme_content():
    """Charge le contenu du README.md."""
    if not README_PATH.is_file():
        pytest.fail("README.md introuvable à la racine du projet")
    return README_PATH.read_text(encoding="utf-8")


class TestReadmeExists:
    """#032 — Le fichier README.md existe à la racine."""

    def test_readme_file_exists(self):
        assert README_PATH.is_file(), "README.md doit exister à la racine du projet"

    def test_readme_not_empty(self, readme_content):
        assert len(readme_content.strip()) > 0, "README.md ne doit pas être vide"


class TestReadmeSectionsPresent:
    """#032 — Les sections obligatoires sont présentes."""

    def test_has_installation_section(self, readme_content):
        lower = readme_content.lower()
        assert "installation" in lower, "Section 'Installation' manquante"

    def test_has_architecture_section(self, readme_content):
        lower = readme_content.lower()
        assert "architecture" in lower, "Section 'Architecture' manquante"

    def test_has_stack_technique_section(self, readme_content):
        lower = readme_content.lower()
        assert "stack" in lower or "technique" in lower, (
            "Section 'Stack technique' manquante"
        )

    def test_has_utilisation_section(self, readme_content):
        lower = readme_content.lower()
        assert "utilisation" in lower, "Section 'Utilisation' manquante"

    def test_has_resultats_section(self, readme_content):
        lower = readme_content.lower()
        assert "résultat" in lower or "resultat" in lower, (
            "Section 'Résultats' manquante"
        )

    def test_has_limites_section(self, readme_content):
        lower = readme_content.lower()
        assert "limite" in lower, "Section 'Limites' manquante"

    def test_has_structure_depot_section(self, readme_content):
        lower = readme_content.lower()
        assert "structure" in lower, "Section 'Structure du dépôt' manquante"


class TestInstallationSection:
    """#032 — La section installation contient les commandes nécessaires."""

    def test_contains_pip_install(self, readme_content):
        assert "pip install" in readme_content, (
            "La section installation doit contenir 'pip install'"
        )

    def test_contains_requirements(self, readme_content):
        assert "requirements.txt" in readme_content, (
            "La section installation doit référencer requirements.txt"
        )


class TestArchitectureSection:
    """#032 — La section architecture contient un schéma du pipeline."""

    def test_pipeline_schema_has_pretraitement(self, readme_content):
        lower = readme_content.lower()
        assert "prétraitement" in lower or "pretraitement" in lower, (
            "Le schéma du pipeline doit mentionner le prétraitement"
        )

    def test_pipeline_schema_has_segmentation(self, readme_content):
        lower = readme_content.lower()
        assert "segmentation" in lower, (
            "Le schéma du pipeline doit mentionner la segmentation"
        )

    def test_pipeline_schema_has_detection_texte(self, readme_content):
        lower = readme_content.lower()
        assert "détection" in lower or "detection" in lower, (
            "Le schéma du pipeline doit mentionner la détection de texte"
        )

    def test_pipeline_schema_has_orientation(self, readme_content):
        lower = readme_content.lower()
        assert "orientation" in lower, (
            "Le schéma du pipeline doit mentionner la correction d'orientation"
        )

    def test_pipeline_schema_has_ocr(self, readme_content):
        assert "OCR" in readme_content, (
            "Le schéma du pipeline doit mentionner l'OCR"
        )

    def test_pipeline_schema_has_posttraitement(self, readme_content):
        lower = readme_content.lower()
        assert "post-traitement" in lower or "posttraitement" in lower, (
            "Le schéma du pipeline doit mentionner le post-traitement"
        )

    def test_pipeline_schema_visual(self, readme_content):
        """Le schéma du pipeline doit contenir des éléments visuels (flèches, box, etc.)."""
        has_arrows = "→" in readme_content or "-->" in readme_content or "==>" in readme_content
        has_ascii_box = "+" in readme_content and "-" in readme_content and "|" in readme_content
        has_mermaid = "```mermaid" in readme_content
        assert has_arrows or has_ascii_box or has_mermaid, (
            "Le schéma du pipeline doit contenir des éléments visuels (flèches ou boxes)"
        )


class TestResultatsSection:
    """#032 — La section résultats contient un tableau de métriques."""

    def test_has_metrics_table(self, readme_content):
        """Le README doit contenir un tableau Markdown (lignes avec |)."""
        lines = readme_content.split("\n")
        table_lines = [line for line in lines if "|" in line and "---" not in line]
        assert len(table_lines) >= 3, (
            "La section résultats doit contenir un tableau Markdown (au moins 3 lignes avec |)"
        )

    def test_mentions_taux_detection(self, readme_content):
        lower = readme_content.lower()
        assert "détection" in lower or "detection" in lower, (
            "Les résultats doivent mentionner le taux de détection"
        )

    def test_mentions_cer(self, readme_content):
        assert "CER" in readme_content, (
            "Les résultats doivent mentionner le CER (Character Error Rate)"
        )

    def test_mentions_identification(self, readme_content):
        lower = readme_content.lower()
        assert "identification" in lower, (
            "Les résultats doivent mentionner le taux d'identification"
        )

    def test_mentions_temps(self, readme_content):
        lower = readme_content.lower()
        assert "temps" in lower or "secondes" in lower or "/image" in lower, (
            "Les résultats doivent mentionner le temps de traitement"
        )


class TestLimitesSection:
    """#032 — La section limites contient au moins 3 items."""

    def test_at_least_3_limites(self, readme_content):
        """Vérifier qu'il y a au moins 3 items de limites (puces Markdown)."""
        lower = readme_content.lower()
        limites_start = lower.find("limite")
        assert limites_start != -1, "Section 'Limites' introuvable"

        # Extraire le texte après "limites" jusqu'à la prochaine section (##)
        after_limites = readme_content[limites_start:]
        lines = after_limites.split("\n")[1:]  # skip the header line

        bullet_count = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("## "):
                break
            if stripped.startswith("- ") or stripped.startswith("* "):
                bullet_count += 1

        assert bullet_count >= 3, (
            f"La section limites doit contenir au moins 3 items (trouvé : {bullet_count})"
        )


class TestUtilisationSection:
    """#032 — La section utilisation contient les commandes CLI et Streamlit."""

    def test_mentions_pipeline_cli(self, readme_content):
        assert "pipeline" in readme_content.lower(), (
            "La section utilisation doit mentionner le pipeline CLI"
        )

    def test_mentions_streamlit(self, readme_content):
        lower = readme_content.lower()
        assert "streamlit" in lower, (
            "La section utilisation doit mentionner Streamlit"
        )

    def test_mentions_app(self, readme_content):
        assert "app.py" in readme_content or "src.app" in readme_content, (
            "La section utilisation doit référencer app.py"
        )
