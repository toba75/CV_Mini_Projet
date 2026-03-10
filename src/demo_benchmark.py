"""Demo image benchmarking for ShelfScan.

Measures pipeline execution time on each demo image in ``data/demo/``
and reports results including timing and book count.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from src.pipeline import run_pipeline

logger = logging.getLogger(__name__)

DEMO_DIR = Path(__file__).resolve().parent.parent / "data" / "demo"
EXPECTED_RESULTS_PATH = DEMO_DIR / "expected_results.json"

VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def _load_demo_image_paths() -> list[Path]:
    """Return sorted list of demo image paths from expected_results.json.

    Raises:
        FileNotFoundError: If expected_results.json or a referenced image is missing.
        ValueError: If expected_results.json has invalid structure.
    """
    if not EXPECTED_RESULTS_PATH.is_file():
        raise FileNotFoundError(
            f"expected_results.json not found: {EXPECTED_RESULTS_PATH}"
        )

    data = json.loads(EXPECTED_RESULTS_PATH.read_text(encoding="utf-8"))

    if "images" not in data:
        raise ValueError("expected_results.json missing 'images' key")

    paths: list[Path] = []
    for entry in data["images"]:
        if "image" not in entry:
            raise ValueError(f"Entry missing 'image' key: {entry}")
        img_path = DEMO_DIR / entry["image"]
        if not img_path.is_file():
            raise FileNotFoundError(f"Demo image not found: {img_path}")
        paths.append(img_path)

    return sorted(paths)


def benchmark_demo_images() -> list[dict]:
    """Run pipeline on each demo image and collect timing results.

    Returns:
        List of dicts, one per image, with keys:
        - ``image``: filename
        - ``processing_time_s``: pipeline execution time
        - ``num_books``: number of books detected
        - ``error`` (optional): error message if pipeline failed
    """
    image_paths = _load_demo_image_paths()
    results: list[dict] = []

    for img_path in image_paths:
        try:
            pipeline_result = run_pipeline(img_path)
            results.append({
                "image": img_path.name,
                "processing_time_s": pipeline_result["processing_time_s"],
                "num_books": len(pipeline_result["books"]),
            })
        except Exception as exc:
            logger.exception("Benchmark failed for %s", img_path.name)
            results.append({
                "image": img_path.name,
                "processing_time_s": 0.0,
                "num_books": 0,
                "error": str(exc),
            })

    return results
