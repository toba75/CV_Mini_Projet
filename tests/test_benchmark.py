"""Tests for benchmark module — TDD RED phase for task #023."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.benchmark import (
    benchmark_all_engines,
    benchmark_ocr_engine,
    export_benchmark_results,
    generate_comparison_report,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_crop(height: int = 64, width: int = 256) -> np.ndarray:
    """Create a synthetic BGR uint8 crop."""
    rng = np.random.default_rng(42)
    return rng.integers(0, 256, size=(height, width, 3), dtype=np.uint8)


@pytest.fixture()
def crops() -> list[np.ndarray]:
    """Return a list of 3 synthetic crops."""
    return [_make_crop() for _ in range(3)]


@pytest.fixture()
def ground_truths() -> list[str]:
    """Return 3 ground truth strings."""
    return ["Harry Potter", "Le Petit Prince", "Les Misérables"]


# ---------------------------------------------------------------------------
# benchmark_ocr_engine
# ---------------------------------------------------------------------------


class TestBenchmarkOcrEngine:
    """Tests for benchmark_ocr_engine."""

    @patch("src.benchmark.recognize_text")
    @patch("src.benchmark.init_ocr_engine")
    def test_returns_expected_keys(
        self,
        mock_init: MagicMock,
        mock_recognize: MagicMock,
        crops: list[np.ndarray],
        ground_truths: list[str],
    ) -> None:
        mock_engine = MagicMock()
        mock_init.return_value = mock_engine
        mock_recognize.return_value = [{"text": "Harry Potter", "confidence": 0.9}]

        result = benchmark_ocr_engine("paddleocr", crops, ground_truths)

        assert result["engine"] == "paddleocr"
        assert "per_crop" in result
        assert "avg_cer" in result
        assert "total_time_s" in result
        assert "avg_time_s" in result

    @patch("src.benchmark.recognize_text")
    @patch("src.benchmark.init_ocr_engine")
    def test_per_crop_length_matches(
        self,
        mock_init: MagicMock,
        mock_recognize: MagicMock,
        crops: list[np.ndarray],
        ground_truths: list[str],
    ) -> None:
        mock_init.return_value = MagicMock()
        mock_recognize.return_value = [{"text": "text", "confidence": 0.9}]

        result = benchmark_ocr_engine("paddleocr", crops, ground_truths)
        assert len(result["per_crop"]) == len(crops)

    @patch("src.benchmark.recognize_text")
    @patch("src.benchmark.init_ocr_engine")
    def test_per_crop_entry_structure(
        self,
        mock_init: MagicMock,
        mock_recognize: MagicMock,
        crops: list[np.ndarray],
        ground_truths: list[str],
    ) -> None:
        mock_init.return_value = MagicMock()
        mock_recognize.return_value = [{"text": "Harry Potter", "confidence": 0.9}]

        result = benchmark_ocr_engine("paddleocr", crops, ground_truths)
        entry = result["per_crop"][0]
        assert "cer" in entry
        assert "predicted" in entry
        assert "ground_truth" in entry
        assert entry["ground_truth"] == "Harry Potter"

    @patch("src.benchmark.recognize_text")
    @patch("src.benchmark.init_ocr_engine")
    def test_perfect_prediction_cer_zero(
        self,
        mock_init: MagicMock,
        mock_recognize: MagicMock,
        crops: list[np.ndarray],
        ground_truths: list[str],
    ) -> None:
        mock_init.return_value = MagicMock()
        # Return exactly the ground truth text for each crop
        mock_recognize.side_effect = [
            [{"text": gt, "confidence": 0.99}] for gt in ground_truths
        ]

        result = benchmark_ocr_engine("paddleocr", crops, ground_truths)
        assert result["avg_cer"] == pytest.approx(0.0)
        for entry in result["per_crop"]:
            assert entry["cer"] == pytest.approx(0.0)

    @patch("src.benchmark.recognize_text")
    @patch("src.benchmark.init_ocr_engine")
    def test_timing_positive(
        self,
        mock_init: MagicMock,
        mock_recognize: MagicMock,
        crops: list[np.ndarray],
        ground_truths: list[str],
    ) -> None:
        mock_init.return_value = MagicMock()
        mock_recognize.return_value = [{"text": "x", "confidence": 0.5}]

        result = benchmark_ocr_engine("paddleocr", crops, ground_truths)
        assert result["total_time_s"] >= 0.0
        assert result["avg_time_s"] >= 0.0

    @patch("src.benchmark.recognize_text")
    @patch("src.benchmark.init_ocr_engine")
    def test_avg_time_equals_total_over_count(
        self,
        mock_init: MagicMock,
        mock_recognize: MagicMock,
        crops: list[np.ndarray],
        ground_truths: list[str],
    ) -> None:
        mock_init.return_value = MagicMock()
        mock_recognize.return_value = [{"text": "x", "confidence": 0.5}]

        result = benchmark_ocr_engine("paddleocr", crops, ground_truths)
        expected_avg = result["total_time_s"] / len(crops)
        assert result["avg_time_s"] == pytest.approx(expected_avg)

    def test_invalid_engine_raises(
        self, crops: list[np.ndarray], ground_truths: list[str]
    ) -> None:
        with pytest.raises(ValueError, match="Unknown OCR engine"):
            benchmark_ocr_engine("invalid_engine", crops, ground_truths)

    def test_mismatched_lengths_raises(self, crops: list[np.ndarray]) -> None:
        with pytest.raises(ValueError, match="must have the same length"):
            benchmark_ocr_engine("paddleocr", crops, ["only one"])

    def test_empty_crops_raises(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            benchmark_ocr_engine("paddleocr", [], [])

    @patch("src.benchmark.recognize_text")
    @patch("src.benchmark.init_ocr_engine")
    def test_multiple_text_results_concatenated(
        self,
        mock_init: MagicMock,
        mock_recognize: MagicMock,
    ) -> None:
        """When recognize_text returns multiple entries, texts are joined."""
        mock_init.return_value = MagicMock()
        mock_recognize.return_value = [
            {"text": "Harry", "confidence": 0.9},
            {"text": "Potter", "confidence": 0.8},
        ]
        crop = _make_crop()
        result = benchmark_ocr_engine("paddleocr", [crop], ["Harry Potter"])
        assert result["per_crop"][0]["predicted"] == "Harry Potter"
        assert result["per_crop"][0]["cer"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# benchmark_all_engines
# ---------------------------------------------------------------------------


class TestBenchmarkAllEngines:
    """Tests for benchmark_all_engines."""

    @patch("src.benchmark.recognize_text")
    @patch("src.benchmark.init_ocr_engine")
    def test_returns_dict_with_engine_keys(
        self,
        mock_init: MagicMock,
        mock_recognize: MagicMock,
        crops: list[np.ndarray],
        ground_truths: list[str],
    ) -> None:
        mock_init.return_value = MagicMock()
        mock_recognize.return_value = [{"text": "text", "confidence": 0.9}]

        engines = ["paddleocr", "tesseract"]
        result = benchmark_all_engines(engines, crops, ground_truths)
        assert set(result.keys()) == set(engines)

    @patch("src.benchmark.recognize_text")
    @patch("src.benchmark.init_ocr_engine")
    def test_each_value_is_benchmark_result(
        self,
        mock_init: MagicMock,
        mock_recognize: MagicMock,
        crops: list[np.ndarray],
        ground_truths: list[str],
    ) -> None:
        mock_init.return_value = MagicMock()
        mock_recognize.return_value = [{"text": "text", "confidence": 0.9}]

        result = benchmark_all_engines(["paddleocr"], crops, ground_truths)
        assert "engine" in result["paddleocr"]
        assert "avg_cer" in result["paddleocr"]

    def test_empty_engine_list_raises(
        self, crops: list[np.ndarray], ground_truths: list[str]
    ) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            benchmark_all_engines([], crops, ground_truths)


# ---------------------------------------------------------------------------
# generate_comparison_report
# ---------------------------------------------------------------------------


class TestGenerateComparisonReport:
    """Tests for generate_comparison_report."""

    def test_returns_markdown_string(self) -> None:
        results = {
            "paddleocr": {
                "engine": "paddleocr",
                "avg_cer": 0.15,
                "avg_time_s": 0.05,
                "total_time_s": 0.15,
                "per_crop": [],
            },
        }
        report = generate_comparison_report(results)
        assert isinstance(report, str)
        assert "paddleocr" in report

    def test_contains_table_separators(self) -> None:
        results = {
            "paddleocr": {
                "engine": "paddleocr",
                "avg_cer": 0.15,
                "avg_time_s": 0.05,
                "total_time_s": 0.15,
                "per_crop": [],
            },
            "tesseract": {
                "engine": "tesseract",
                "avg_cer": 0.30,
                "avg_time_s": 0.10,
                "total_time_s": 0.30,
                "per_crop": [],
            },
        }
        report = generate_comparison_report(results)
        assert "|" in report
        assert "---" in report

    def test_contains_all_engines(self) -> None:
        results = {
            "paddleocr": {
                "engine": "paddleocr",
                "avg_cer": 0.1,
                "avg_time_s": 0.05,
                "total_time_s": 0.15,
                "per_crop": [],
            },
            "trocr": {
                "engine": "trocr",
                "avg_cer": 0.2,
                "avg_time_s": 0.08,
                "total_time_s": 0.24,
                "per_crop": [],
            },
        }
        report = generate_comparison_report(results)
        assert "paddleocr" in report
        assert "trocr" in report

    def test_empty_results_raises(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            generate_comparison_report({})


# ---------------------------------------------------------------------------
# export_benchmark_results
# ---------------------------------------------------------------------------


class TestExportBenchmarkResults:
    """Tests for export_benchmark_results."""

    def test_creates_json_file(self, tmp_path: Path) -> None:
        results = {
            "paddleocr": {
                "engine": "paddleocr",
                "avg_cer": 0.15,
                "avg_time_s": 0.05,
                "total_time_s": 0.15,
                "per_crop": [
                    {"cer": 0.15, "predicted": "text", "ground_truth": "test"}
                ],
            },
        }
        output = tmp_path / "results.json"
        returned_path = export_benchmark_results(results, output)

        assert returned_path == output
        assert output.exists()

    def test_json_content_matches(self, tmp_path: Path) -> None:
        results = {
            "paddleocr": {
                "engine": "paddleocr",
                "avg_cer": 0.15,
                "avg_time_s": 0.05,
                "total_time_s": 0.15,
                "per_crop": [],
            },
        }
        output = tmp_path / "results.json"
        export_benchmark_results(results, output)

        loaded = json.loads(output.read_text(encoding="utf-8"))
        assert loaded == results

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        results = {
            "paddleocr": {
                "engine": "paddleocr",
                "avg_cer": 0.1,
                "avg_time_s": 0.05,
                "total_time_s": 0.15,
                "per_crop": [],
            },
        }
        output = tmp_path / "sub" / "dir" / "results.json"
        returned_path = export_benchmark_results(results, output)

        assert returned_path == output
        assert output.exists()

    def test_returns_path_object(self, tmp_path: Path) -> None:
        results = {
            "paddleocr": {
                "engine": "paddleocr",
                "avg_cer": 0.1,
                "avg_time_s": 0.05,
                "total_time_s": 0.15,
                "per_crop": [],
            },
        }
        output = tmp_path / "results.json"
        returned = export_benchmark_results(results, output)
        assert isinstance(returned, Path)

    def test_accepts_string_path(self, tmp_path: Path) -> None:
        results = {
            "paddleocr": {
                "engine": "paddleocr",
                "avg_cer": 0.1,
                "avg_time_s": 0.05,
                "total_time_s": 0.15,
                "per_crop": [],
            },
        }
        output = str(tmp_path / "results.json")
        returned = export_benchmark_results(results, output)
        assert isinstance(returned, Path)
        assert returned.exists()
