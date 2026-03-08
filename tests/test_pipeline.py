"""Tests for pipeline module — structure JSON sortie pipeline."""

import csv
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.pipeline import export_csv, export_json, run_pipeline


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

FAKE_IMAGE = np.zeros((100, 300, 3), dtype=np.uint8)
FAKE_SPINE = np.zeros((100, 50, 3), dtype=np.uint8)


def _make_pipeline_result() -> dict:
    """Build a minimal pipeline result dict for export tests."""
    return {
        "image": "shelf.jpg",
        "num_spines_detected": 2,
        "processing_time_s": 1.23,
        "books": [
            {
                "spine_id": 1,
                "raw_text": "Le Petit Prince",
                "title": "Le Petit Prince",
                "author": "Saint-Exupéry",
                "isbn": "9782070612758",
                "confidence": 0.92,
            },
            {
                "spine_id": 2,
                "raw_text": "Les Misérables",
                "title": "Les Misérables",
                "author": "Victor Hugo",
                "isbn": None,
                "confidence": 0.85,
            },
        ],
    }


# ---------------------------------------------------------------------------
# TestRunPipeline
# ---------------------------------------------------------------------------


class TestRunPipeline:
    """run_pipeline retourne un dict structuré avec les clés attendues."""

    @patch("src.pipeline.identify_book")
    @patch("src.pipeline.postprocess_spine")
    @patch("src.pipeline._aggregate_ocr_results")
    @patch("src.pipeline.recognize_text")
    @patch("src.pipeline.correct_orientation")
    @patch("src.pipeline.detect_text_regions")
    @patch("src.pipeline.init_ocr_engine")
    @patch("src.pipeline.init_detector")
    @patch("src.pipeline.segment")
    @patch("src.pipeline.preprocess")
    def test_returns_dict_with_expected_keys(
        self,
        mock_preprocess: MagicMock,
        mock_segment: MagicMock,
        mock_init_detector: MagicMock,
        mock_init_ocr: MagicMock,
        mock_detect: MagicMock,
        mock_correct: MagicMock,
        mock_recognize: MagicMock,
        mock_aggregate: MagicMock,
        mock_postprocess: MagicMock,
        mock_identify: MagicMock,
        tmp_path: Path,
    ) -> None:
        # Create a fake image file
        img_path = tmp_path / "shelf.jpg"
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_preprocess.return_value = FAKE_IMAGE
        mock_segment.return_value = [FAKE_SPINE]
        mock_init_detector.return_value = MagicMock()
        mock_init_ocr.return_value = MagicMock()
        mock_detect.return_value = [{"bbox": [[0, 0], [50, 0], [50, 20], [0, 20]], "confidence": 0.9}]
        mock_correct.return_value = FAKE_SPINE
        mock_recognize.return_value = [{"text": "Le Petit Prince", "confidence": 0.9}]
        mock_aggregate.return_value = {"text": "Le Petit Prince", "confidence": 0.9, "engine": "paddleocr"}
        mock_postprocess.return_value = {
            "raw_text": "Le Petit Prince",
            "clean_text": "Le Petit Prince",
            "title": "Le Petit Prince",
            "author": None,
        }
        mock_identify.return_value = {
            "title": "Le Petit Prince",
            "author": "Saint-Exupéry",
            "isbn": "9782070612758",
            "confidence": 0.92,
            "provider": "openlibrary",
        }

        result = run_pipeline(str(img_path))

        assert isinstance(result, dict)
        assert "image" in result
        assert "num_spines_detected" in result
        assert "processing_time_s" in result
        assert "books" in result
        assert isinstance(result["books"], list)
        assert len(result["books"]) == 1
        book = result["books"][0]
        assert "spine_id" in book
        assert "raw_text" in book
        assert "title" in book
        assert "confidence" in book

    def test_file_not_found_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            run_pipeline("/nonexistent/path/shelf.jpg")

    def test_invalid_image_raises_value_error(self, tmp_path: Path) -> None:
        txt_file = tmp_path / "notes.txt"
        txt_file.write_text("not an image")
        with pytest.raises(ValueError):
            run_pipeline(str(txt_file))


# ---------------------------------------------------------------------------
# TestExportJson
# ---------------------------------------------------------------------------


class TestExportJson:
    """export_json écrit un fichier JSON valide."""

    def test_writes_valid_json(self, tmp_path: Path) -> None:
        result = _make_pipeline_result()
        output_path = tmp_path / "output.json"

        returned_path = export_json(result, output_path)

        assert returned_path == output_path
        assert output_path.exists()
        with open(output_path, encoding="utf-8") as f:
            loaded = json.load(f)
        assert loaded["image"] == "shelf.jpg"
        assert len(loaded["books"]) == 2

    def test_creates_parent_dirs(self, tmp_path: Path) -> None:
        result = _make_pipeline_result()
        output_path = tmp_path / "sub" / "dir" / "output.json"

        returned_path = export_json(result, output_path)

        assert returned_path == output_path
        assert output_path.exists()


# ---------------------------------------------------------------------------
# TestExportCsv
# ---------------------------------------------------------------------------


class TestExportCsv:
    """export_csv écrit un CSV avec les colonnes attendues."""

    def test_writes_csv_with_expected_columns(self, tmp_path: Path) -> None:
        result = _make_pipeline_result()
        output_path = tmp_path / "output.csv"

        returned_path = export_csv(result, output_path)

        assert returned_path == output_path
        assert output_path.exists()
        with open(output_path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 2
        expected_columns = {"spine_id", "raw_text", "title", "author", "isbn", "confidence"}
        assert expected_columns.issubset(set(reader.fieldnames or []))
