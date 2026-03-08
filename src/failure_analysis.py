"""Failure analysis module for ShelfScan pipeline evaluation."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Failure thresholds
SEGMENTATION_THRESHOLD = 0.5  # detection_rate < this => segmentation failure
OCR_CER_THRESHOLD = 0.5  # cer > this => OCR failure
IDENTIFICATION_THRESHOLD = 0.3  # identification_rate < this => identification failure

_REQUIRED_METRICS = ("detection_rate", "cer", "identification_rate")

# Improvement suggestions per category
_IMPROVEMENT_SUGGESTIONS: dict[str, list[str]] = {
    "segmentation": [
        "Améliorer le prétraitement (CLAHE, correction de perspective)",
        "Ajuster les paramètres de détection de lignes (Hough)",
        "Augmenter la résolution minimale des images en entrée",
    ],
    "ocr": [
        "Améliorer la binarisation avant OCR",
        "Tester un autre moteur OCR (Tesseract vs PaddleOCR)",
        "Appliquer une correction de rotation plus fine sur les tranches",
    ],
    "identification": [
        "Abaisser le seuil de fuzzy matching",
        "Normaliser davantage le texte avant comparaison (accents, casse)",
        "Enrichir la base de référence bibliographique",
    ],
    "multiple": [
        "Analyser les images concernées pour identifier la cause racine",
        "Vérifier la qualité des images en entrée (flou, éclairage)",
        "Envisager un pipeline de fallback pour les cas difficiles",
    ],
}


def categorize_failure(image_metrics: dict) -> str:
    """Categorize the type of failure for a single image based on its metrics.

    Args:
        image_metrics: Dict with keys 'detection_rate', 'cer', 'identification_rate'.

    Returns:
        One of: 'segmentation', 'ocr', 'identification', 'multiple', 'acceptable'.

    Raises:
        ValueError: If any required metric key is missing from image_metrics.
    """
    for key in _REQUIRED_METRICS:
        if key not in image_metrics:
            raise ValueError(f"Missing required metric key: {key}")

    detection_rate = image_metrics["detection_rate"]
    cer = image_metrics["cer"]
    identification_rate = image_metrics["identification_rate"]

    failures: list[str] = []

    if detection_rate < SEGMENTATION_THRESHOLD:
        failures.append("segmentation")
    if cer > OCR_CER_THRESHOLD:
        failures.append("ocr")
    if identification_rate < IDENTIFICATION_THRESHOLD:
        failures.append("identification")

    if len(failures) > 1:
        return "multiple"
    if len(failures) == 1:
        return failures[0]
    return "acceptable"


def analyze_failures(eval_results: dict) -> dict:
    """Analyze evaluation results and categorize failures per image.

    Args:
        eval_results: Dict with 'per_image' key containing list of per-image metric dicts.
            Each dict must have keys: 'image', 'detection_rate', 'cer', 'identification_rate'.

    Returns:
        Dict with:
            - 'categories': {category_name: count}
            - 'worst_per_category': {category_name: worst_image_name}
            - 'total_failures': int (count of non-acceptable images)

    Raises:
        ValueError: If eval_results has no 'per_image' key or it is empty.
    """
    if "per_image" not in eval_results:
        raise ValueError("eval_results must contain 'per_image' key")

    per_image = eval_results["per_image"]
    if not per_image:
        raise ValueError("per_image list is empty — nothing to analyze")

    categories: dict[str, int] = {}
    images_by_category: dict[str, list[dict]] = {}

    for entry in per_image:
        category = categorize_failure(entry)
        categories[category] = categories.get(category, 0) + 1

        if category not in images_by_category:
            images_by_category[category] = []
        images_by_category[category].append(entry)

    # Find worst image per failure category
    worst_per_category: dict[str, str] = {}

    # Scoring: for each category, pick the image with the worst relevant metric
    _worst_key_map = {
        "segmentation": ("detection_rate", False),  # (key, higher_is_worse)
        "ocr": ("cer", True),
        "identification": ("identification_rate", False),
        "multiple": ("detection_rate", False),
    }

    for cat, entries in images_by_category.items():
        if cat == "acceptable":
            continue
        metric_key, higher_is_worse = _worst_key_map.get(cat, ("detection_rate", False))
        sorted_entries = sorted(
            entries,
            key=lambda e: e[metric_key],
            reverse=higher_is_worse,
        )
        worst_per_category[cat] = sorted_entries[0]["image"]

    total_failures = sum(
        count for cat, count in categories.items() if cat != "acceptable"
    )

    return {
        "categories": categories,
        "worst_per_category": worst_per_category,
        "total_failures": total_failures,
    }


def generate_failure_report(analysis: dict) -> str:
    """Generate a markdown failure analysis report.

    Args:
        analysis: Dict from analyze_failures with 'categories', 'worst_per_category',
            'total_failures'.

    Returns:
        Markdown-formatted report string.

    Raises:
        ValueError: If analysis has no failure categories to report on.
    """
    categories = analysis.get("categories", {})
    worst = analysis.get("worst_per_category", {})
    total = analysis.get("total_failures", 0)

    if not categories:
        raise ValueError("No failure categories to report — analysis is empty")

    lines: list[str] = []
    lines.append("# Analyse des cas d'échec — ShelfScan")
    lines.append("")

    # Summary
    lines.append("## Résumé")
    lines.append("")
    lines.append(f"- **Total d'images en échec** : {total}")
    lines.append(f"- **Total d'images analysées** : {sum(categories.values())}")
    lines.append("")

    lines.append("| Catégorie | Nombre |")
    lines.append("|-----------|--------|")
    for cat, count in sorted(categories.items()):
        lines.append(f"| {cat} | {count} |")
    lines.append("")

    # Detail per failure category
    failure_cats = {k: v for k, v in categories.items() if k != "acceptable"}
    if failure_cats:
        lines.append("## Détail par catégorie d'échec")
        lines.append("")

        for cat in sorted(failure_cats):
            lines.append(f"### {cat.capitalize()}")
            lines.append("")
            lines.append(f"- **Fréquence** : {failure_cats[cat]} image(s)")
            if cat in worst:
                lines.append(f"- **Pire image** : `{worst[cat]}`")

            suggestions = _IMPROVEMENT_SUGGESTIONS.get(cat, [])
            if suggestions:
                lines.append("")
                lines.append("**Pistes d'amélioration** :")
                lines.append("")
                for suggestion in suggestions:
                    lines.append(f"- {suggestion}")
            lines.append("")

    return "\n".join(lines)


def export_failure_report(analysis: dict, output_path: str | Path) -> Path:
    """Export the failure analysis report as a markdown file.

    Args:
        analysis: Dict from analyze_failures.
        output_path: Destination file path.

    Returns:
        The output Path.

    Raises:
        ValueError: If analysis is invalid (propagated from generate_failure_report).
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = generate_failure_report(analysis)
    output_path.write_text(report, encoding="utf-8")

    return output_path
