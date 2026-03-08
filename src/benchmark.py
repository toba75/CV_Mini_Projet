"""Quantitative OCR benchmark utilities for ShelfScan.

Provides functions to benchmark OCR engines on annotated crops,
compute per-crop and average CER, measure inference time, and
export results as JSON or markdown reports.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from src.eval_utils import compute_cer
from src.ocr import SUPPORTED_ENGINES, init_ocr_engine, recognize_text


def benchmark_ocr_engine(
    engine_name: str,
    crops: list[np.ndarray],
    ground_truths: list[str],
) -> dict:
    """Benchmark a single OCR engine on a list of crops.

    Args:
        engine_name: One of :data:`src.ocr.SUPPORTED_ENGINES`.
        crops: List of BGR uint8 image crops.
        ground_truths: List of ground truth strings (same length as *crops*).

    Returns:
        Dict with keys ``engine``, ``per_crop``, ``avg_cer``,
        ``total_time_s``, ``avg_time_s``.

    Raises:
        ValueError: If *engine_name* is unsupported, lists are empty,
            or lengths mismatch.
    """
    if engine_name not in SUPPORTED_ENGINES:
        raise ValueError(
            f"Unknown OCR engine '{engine_name}'. "
            f"Supported: {SUPPORTED_ENGINES}"
        )
    if len(crops) == 0:
        raise ValueError("crops and ground_truths must not be empty")
    if len(crops) != len(ground_truths):
        raise ValueError(
            f"crops and ground_truths must have the same length, "
            f"got {len(crops)} and {len(ground_truths)}"
        )

    engine = init_ocr_engine(engine_name)
    per_crop: list[dict] = []

    t_start = time.perf_counter()
    for crop, gt in zip(crops, ground_truths):
        ocr_results = recognize_text(crop, engine)
        predicted = " ".join(str(r["text"]) for r in ocr_results)
        cer = compute_cer(predicted, gt)
        per_crop.append({
            "cer": cer,
            "predicted": predicted,
            "ground_truth": gt,
        })
    t_end = time.perf_counter()

    total_time = t_end - t_start
    avg_cer = sum(entry["cer"] for entry in per_crop) / len(per_crop)

    return {
        "engine": engine_name,
        "per_crop": per_crop,
        "avg_cer": avg_cer,
        "total_time_s": total_time,
        "avg_time_s": total_time / len(crops),
    }


def benchmark_all_engines(
    engine_names: list[str],
    crops: list[np.ndarray],
    ground_truths: list[str],
) -> dict:
    """Benchmark multiple OCR engines and return combined results.

    Args:
        engine_names: List of engine names to benchmark.
        crops: List of BGR uint8 image crops.
        ground_truths: List of ground truth strings.

    Returns:
        Dict ``{engine_name: benchmark_result}``.

    Raises:
        ValueError: If *engine_names* is empty.
    """
    if not engine_names:
        raise ValueError("engine_names must not be empty")

    results: dict = {}
    for name in engine_names:
        results[name] = benchmark_ocr_engine(name, crops, ground_truths)
    return results


def generate_comparison_report(benchmark_results: dict) -> str:
    """Generate a markdown comparison table from benchmark results.

    Args:
        benchmark_results: Dict ``{engine_name: result_dict}`` as returned
            by :func:`benchmark_all_engines`.

    Returns:
        Markdown-formatted table string.

    Raises:
        ValueError: If *benchmark_results* is empty.
    """
    if not benchmark_results:
        raise ValueError("benchmark_results must not be empty")

    lines: list[str] = []
    lines.append("| Engine | Avg CER | Avg Time (s) |")
    lines.append("|--------|---------|--------------|")
    for engine_name, result in benchmark_results.items():
        avg_cer = result["avg_cer"]
        avg_time = result["avg_time_s"]
        lines.append(f"| {engine_name} | {avg_cer:.4f} | {avg_time:.4f} |")

    return "\n".join(lines)


def export_benchmark_results(
    benchmark_results: dict,
    output_path: str | Path,
) -> Path:
    """Export benchmark results to a JSON file.

    Args:
        benchmark_results: Dict of benchmark results.
        output_path: Destination file path.

    Returns:
        The output path as a :class:`~pathlib.Path`.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(benchmark_results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return path
