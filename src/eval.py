"""Full evaluation of the ShelfScan pipeline on an annotated dataset."""

import json
import statistics
import time
from pathlib import Path

from src.eval_utils import (
    compute_cer,
    compute_detection_rate,
    compute_identification_rate,
    load_ground_truth,
)
from src.pipeline import run_pipeline

# Target thresholds from specification §6
TARGET_DETECTION_RATE = 0.80
TARGET_CER = 0.20
TARGET_IDENTIFICATION_RATE = 0.60
TARGET_TIME_S = 30.0


def run_full_evaluation(
    data_dir: str | Path,
    ground_truth_csv: str | Path,
    output_dir: str | Path,
    ocr_engine: str = "paddleocr",
) -> dict:
    """Run the full pipeline evaluation on the annotated dataset.

    Args:
        data_dir: Directory containing the input images.
        ground_truth_csv: Path to the ground truth CSV file.
        output_dir: Directory for evaluation outputs.
        ocr_engine: OCR engine to use (forwarded to the pipeline).

    Returns:
        Dict with ``per_image`` (list of per-image metrics) and
        ``summary`` (means and standard deviations).

    Raises:
        ValueError: If data_dir does not exist or ground_truth_csv is invalid.
    """
    data_dir = Path(data_dir)
    ground_truth_csv = Path(ground_truth_csv)
    output_dir = Path(output_dir)

    if not data_dir.is_dir():
        raise ValueError(f"Data directory not found: {data_dir}")

    # load_ground_truth raises ValueError on invalid CSV
    df = load_ground_truth(str(ground_truth_csv))

    output_dir.mkdir(parents=True, exist_ok=True)

    # Group ground truth by image
    gt_by_image: dict[str, dict] = {}
    for image_name, group in df.groupby("image_filename"):
        gt_by_image[image_name] = {
            "titles": group["title"].tolist(),
            "count": len(group),
        }

    per_image: list[dict] = []

    for image_name, gt_info in sorted(gt_by_image.items()):
        image_path = data_dir / image_name

        start = time.perf_counter()
        pipeline_result = run_pipeline(image_path, ocr_engine=ocr_engine)
        elapsed = time.perf_counter() - start

        books = pipeline_result.get("books", [])
        predicted_count = len(books)
        gt_count = gt_info["count"]
        gt_titles = gt_info["titles"]

        detection_rate = compute_detection_rate(predicted_count, gt_count)

        predicted_titles = [b.get("title", "") for b in books]
        identification_rate = compute_identification_rate(predicted_titles, gt_titles)

        predicted_texts = [b.get("raw_text", "") for b in books]
        pairs = list(zip(predicted_texts, gt_titles))
        if pairs:
            cer = sum(compute_cer(p, g) for p, g in pairs) / len(pairs)
        else:
            cer = 0.0

        per_image.append({
            "image": image_name,
            "detection_rate": detection_rate,
            "cer": cer,
            "identification_rate": identification_rate,
            "time_s": elapsed,
        })

    # Compute summary statistics
    summary = _compute_summary(per_image)

    return {"per_image": per_image, "summary": summary}


def _compute_summary(per_image: list[dict]) -> dict:
    """Compute mean and std for all metrics.

    Args:
        per_image: List of per-image metric dicts.

    Returns:
        Dict with mean_* and std_* keys for each metric.
    """
    if not per_image:
        return {
            "mean_detection_rate": 0.0,
            "mean_cer": 0.0,
            "mean_identification_rate": 0.0,
            "mean_time_s": 0.0,
            "std_detection_rate": 0.0,
            "std_cer": 0.0,
            "std_identification_rate": 0.0,
            "std_time_s": 0.0,
        }

    metrics = ["detection_rate", "cer", "identification_rate", "time_s"]
    summary: dict = {}

    for metric in metrics:
        values = [entry[metric] for entry in per_image]
        summary[f"mean_{metric}"] = statistics.mean(values)
        if len(values) >= 2:
            summary[f"std_{metric}"] = statistics.stdev(values)
        else:
            summary[f"std_{metric}"] = 0.0

    return summary


def generate_evaluation_report(eval_results: dict) -> str:
    """Generate a markdown evaluation report.

    Args:
        eval_results: Dict with ``per_image`` and ``summary`` keys.

    Returns:
        Markdown-formatted report string.

    Raises:
        ValueError: If eval_results has no per-image data.
    """
    per_image = eval_results.get("per_image", [])
    summary = eval_results.get("summary", {})

    if not per_image:
        raise ValueError("No per-image results to generate report from")

    lines: list[str] = []
    lines.append("# ShelfScan Evaluation Report")
    lines.append("")

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| Métrique | Résultat | Cible | Atteint |")
    lines.append("|----------|----------|-------|---------|")

    def _check(value: float, target: float, lower_is_better: bool = False) -> str:
        if lower_is_better:
            return "✓" if value <= target else "✗"
        return "✓" if value >= target else "✗"

    mean_dr = summary.get("mean_detection_rate", 0.0)
    mean_cer = summary.get("mean_cer", 0.0)
    mean_ir = summary.get("mean_identification_rate", 0.0)
    mean_time = summary.get("mean_time_s", 0.0)

    lines.append(
        f"| Taux de détection | {mean_dr:.1%} | ≥ 80% "
        f"| {_check(mean_dr, TARGET_DETECTION_RATE)} |"
    )
    lines.append(
        f"| CER moyen | {mean_cer:.1%} | ≤ 20% "
        f"| {_check(mean_cer, TARGET_CER, lower_is_better=True)} |"
    )
    lines.append(
        f"| Taux d'identification | {mean_ir:.1%} | ≥ 60% "
        f"| {_check(mean_ir, TARGET_IDENTIFICATION_RATE)} |"
    )
    lines.append(
        f"| Temps moyen | {mean_time:.1f}s | < 30s "
        f"| {_check(mean_time, TARGET_TIME_S, lower_is_better=True)} |"
    )

    lines.append("")

    # Per-image results
    lines.append("## Per-image Results")
    lines.append("")
    lines.append("| Image | Détection | CER | Identification | Temps |")
    lines.append("|-------|-----------|-----|----------------|-------|")

    for entry in per_image:
        lines.append(
            f"| {entry['image']} "
            f"| {entry['detection_rate']:.1%} "
            f"| {entry['cer']:.1%} "
            f"| {entry['identification_rate']:.1%} "
            f"| {entry['time_s']:.2f}s |"
        )

    lines.append("")
    return "\n".join(lines)


def export_evaluation_results(eval_results: dict, output_path: str | Path) -> Path:
    """Export evaluation results to a JSON file.

    Args:
        eval_results: Dict with ``per_image`` and ``summary`` keys.
        output_path: Destination file path.

    Returns:
        The output Path.

    Raises:
        ValueError: If eval_results has no per-image data.
    """
    if not eval_results.get("per_image"):
        raise ValueError("No per-image results to export")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2, ensure_ascii=False)

    return output_path


def identify_worst_images(eval_results: dict, n: int = 5) -> list[dict]:
    """Identify the n images with the worst CER.

    Args:
        eval_results: Dict with ``per_image`` and ``summary`` keys.
        n: Number of worst images to return.

    Returns:
        List of dicts sorted by CER descending (worst first).

    Raises:
        ValueError: If eval_results has no per-image data.
    """
    per_image = eval_results.get("per_image", [])

    if not per_image:
        raise ValueError("No per-image results to identify worst images from")

    sorted_images = sorted(per_image, key=lambda x: x["cer"], reverse=True)
    return sorted_images[:n]
