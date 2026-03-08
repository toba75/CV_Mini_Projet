"""Evaluation utilities for ShelfScan pipeline."""

import json
import pathlib

import editdistance
import pandas as pd
from rapidfuzz import fuzz

REQUIRED_COLUMNS = ["image_filename", "spine_index", "title", "author"]


def load_ground_truth(csv_path: str) -> pd.DataFrame:
    """Load and validate ground truth CSV.

    Args:
        csv_path: Path to the ground truth CSV file.

    Returns:
        Validated DataFrame with columns image_filename, spine_index, title, author.

    Raises:
        ValueError: If file doesn't exist, columns are missing, or data is invalid.
    """
    path = pathlib.Path(csv_path)
    if not path.exists():
        raise ValueError(f"Ground truth file not found: {csv_path}")

    df = pd.read_csv(path)

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    title_is_na = df["title"].isna()
    title_is_blank = df["title"].fillna("").str.strip() == ""
    empty_titles = title_is_na | title_is_blank
    if empty_titles.any():
        raise ValueError(f"Found {empty_titles.sum()} rows with empty titles")

    return df


def compute_detection_rate(predicted_count: int, ground_truth_count: int) -> float:
    """Compute detection rate as ratio of predicted / ground truth counts.

    Args:
        predicted_count: Number of predicted spines (>= 0).
        ground_truth_count: Number of ground truth spines (>= 0).

    Returns:
        Ratio capped at 1.0. Returns 0.0 if ground_truth_count is 0.
    """
    if ground_truth_count == 0:
        return 0.0
    return min(predicted_count / ground_truth_count, 1.0)


def compute_cer(predicted_text: str, ground_truth_text: str) -> float:
    """Compute Character Error Rate using Levenshtein distance.

    Args:
        predicted_text: Predicted text from OCR.
        ground_truth_text: Ground truth text.

    Returns:
        CER as edit_distance / len(ground_truth_text).
        Returns 0.0 if both texts are empty.
        Returns 1.0 if ground_truth_text is empty but predicted_text is not.
    """
    if len(ground_truth_text) == 0:
        return 1.0 if len(predicted_text) > 0 else 0.0
    distance = editdistance.eval(predicted_text, ground_truth_text)
    return distance / len(ground_truth_text)


def compute_identification_rate(
    predicted_titles: list[str],
    ground_truth_titles: list[str],
    threshold: float = 60.0,
) -> float:
    """Compute identification rate via fuzzy matching.

    For each ground truth title, check if any predicted title matches
    with rapidfuzz.fuzz.ratio >= threshold.

    Args:
        predicted_titles: List of predicted book titles.
        ground_truth_titles: List of ground truth book titles.
        threshold: Minimum fuzz ratio to consider a match.

    Returns:
        Ratio of matched ground truth titles / total ground truth titles.
        Returns 0.0 if ground_truth_titles is empty.
    """
    if not ground_truth_titles:
        return 0.0
    matched = 0
    for gt_title in ground_truth_titles:
        for pred_title in predicted_titles:
            if fuzz.ratio(pred_title, gt_title) >= threshold:
                matched += 1
                break
    return matched / len(ground_truth_titles)


def evaluate_image(pipeline_result: dict, ground_truth: dict) -> dict:
    """Evaluate a single image by computing all three metrics.

    Args:
        pipeline_result: Dict with key 'books' (list of dicts with 'raw_text', 'title').
        ground_truth: Dict with keys 'titles' (list[str]) and 'count' (int).

    Returns:
        Dict with keys 'detection_rate', 'cer', 'identification_rate'.
    """
    books = pipeline_result.get("books", [])
    gt_titles = ground_truth.get("titles", [])
    gt_count = ground_truth.get("count", 0)

    detection_rate = compute_detection_rate(len(books), gt_count)

    predicted_titles = [b.get("title", "") for b in books]
    identification_rate = compute_identification_rate(predicted_titles, gt_titles)

    # CER: average over matched pairs (zip predicted and gt raw texts)
    predicted_texts = [b.get("raw_text", "") for b in books]
    pairs = list(zip(predicted_texts, gt_titles))
    if pairs:
        cer = sum(compute_cer(p, g) for p, g in pairs) / len(pairs)
    else:
        cer = 0.0

    return {
        "detection_rate": detection_rate,
        "cer": cer,
        "identification_rate": identification_rate,
    }


def evaluate_dataset(
    results_dir: str | pathlib.Path, ground_truth_dir: str | pathlib.Path
) -> dict:
    """Evaluate the full dataset by comparing pipeline results with ground truth.

    Args:
        results_dir: Directory containing JSON result files (one per image).
        ground_truth_dir: Directory containing the ground_truth.csv file.

    Returns:
        Dict with 'per_image' (list of per-image metrics) and 'average' (mean metrics).
    """
    results_path = pathlib.Path(results_dir)
    gt_path = pathlib.Path(ground_truth_dir)

    # Load ground truth CSV via load_ground_truth for consistent validation
    csv_files = list(gt_path.glob("*.csv"))
    if not csv_files:
        return {
            "per_image": [],
            "average": {"detection_rate": 0.0, "cer": 0.0, "identification_rate": 0.0},
        }

    try:
        df = load_ground_truth(str(csv_files[0]))
    except ValueError:
        return {
            "per_image": [],
            "average": {"detection_rate": 0.0, "cer": 0.0, "identification_rate": 0.0},
        }
    if df.empty:
        return {
            "per_image": [],
            "average": {"detection_rate": 0.0, "cer": 0.0, "identification_rate": 0.0},
        }

    # Group ground truth by image
    gt_by_image = {}
    for image_name, group in df.groupby("image_filename"):
        gt_by_image[image_name] = {
            "titles": group["title"].tolist(),
            "count": len(group),
        }

    # Process each JSON result
    per_image = []
    for json_file in sorted(results_path.glob("*.json")):
        with open(json_file, encoding="utf-8") as f:
            pipeline_result = json.load(f)

        image_name = pipeline_result.get("image", json_file.stem + ".jpeg")
        if image_name not in gt_by_image:
            continue

        metrics = evaluate_image(pipeline_result, gt_by_image[image_name])
        metrics["image"] = image_name
        per_image.append(metrics)

    # Compute averages
    if per_image:
        avg = {
            "detection_rate": sum(m["detection_rate"] for m in per_image) / len(per_image),
            "cer": sum(m["cer"] for m in per_image) / len(per_image),
            "identification_rate": sum(m["identification_rate"] for m in per_image)
            / len(per_image),
        }
    else:
        avg = {"detection_rate": 0.0, "cer": 0.0, "identification_rate": 0.0}

    return {"per_image": per_image, "average": avg}
