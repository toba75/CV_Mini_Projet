"""Tests for pipeline reproducibility — task #030.

Validates:
- requirements.txt structure (all deps have version bounds)
- CLI execution via `python -m src.pipeline <image_path>`
- End-to-end integration with mocked OCR producing valid JSON
- No undocumented environment variables required
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.pipeline import run_pipeline

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS_TXT = PROJECT_ROOT / "requirements.txt"

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FAKE_IMAGE = np.zeros((200, 400, 3), dtype=np.uint8)
FAKE_SPINE = np.zeros((200, 60, 3), dtype=np.uint8)


def _mock_pipeline_deps() -> dict:
    """Return a dict of patch targets and their return values for full pipeline mocking."""
    return {
        "src.pipeline.preprocess": FAKE_IMAGE,
        "src.pipeline.segment": [FAKE_SPINE],
        "src.pipeline.init_detector": MagicMock(),
        "src.pipeline.init_ocr_engine": MagicMock(),
        "src.pipeline.detect_text_regions": [
            {"bbox": [[0, 0], [50, 0], [50, 20], [0, 20]], "confidence": 0.9}
        ],
        "src.pipeline.correct_orientation": FAKE_SPINE,
        "src.pipeline.recognize_text": [{"text": "Test Book", "confidence": 0.85}],
        "src.pipeline._aggregate_ocr_results": {
            "text": "Test Book",
            "confidence": 0.85,
            "engine": "paddleocr",
        },
        "src.pipeline.postprocess_spine": {
            "raw_text": "Test Book",
            "clean_text": "Test Book",
            "title": "Test Book",
            "author": None,
        },
        "src.pipeline.identify_book": {
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "1234567890",
            "confidence": 0.9,
            "provider": "openlibrary",
        },
    }


# ---------------------------------------------------------------------------
# TestRequirementsTxt — structure du fichier requirements.txt
# ---------------------------------------------------------------------------


class TestRequirementsTxt:
    """requirements.txt contains all dependencies with version bounds."""

    def test_requirements_file_exists(self) -> None:
        assert REQUIREMENTS_TXT.exists(), "requirements.txt must exist at project root"

    def test_all_deps_have_version_bounds(self) -> None:
        """Every non-comment, non-empty line must have a version specifier (>=, ==, ~=, etc.)."""
        lines = REQUIREMENTS_TXT.read_text(encoding="utf-8").splitlines()
        version_pattern = re.compile(r"(>=|<=|==|~=|!=|<|>)")

        for lineno, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            assert version_pattern.search(stripped), (
                f"requirements.txt line {lineno}: '{stripped}' has no version bound"
            )

    def test_no_pinned_exact_without_range(self) -> None:
        """Deps should use ranges (>=X,<Y) rather than exact pins (==X) for flexibility."""
        lines = REQUIREMENTS_TXT.read_text(encoding="utf-8").splitlines()

        for lineno, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            # Exact pin without upper bound is discouraged
            if "==" in stripped and ">=" not in stripped:
                pytest.fail(
                    f"requirements.txt line {lineno}: '{stripped}' uses exact pin "
                    f"without range — prefer >=X,<Y"
                )

    def test_key_dependencies_present(self) -> None:
        """Core dependencies needed by the pipeline must be listed."""
        content = REQUIREMENTS_TXT.read_text(encoding="utf-8").lower()
        required_deps = [
            "opencv-python",
            "numpy",
            "paddleocr",
            "torch",
            "pathlib" not in content or True,  # pathlib is stdlib, skip
        ]
        # Check actual package names
        for dep in ["opencv-python", "paddleocr", "torch", "pytest", "ruff"]:
            assert dep in content, f"Missing required dependency: {dep}"

    def test_numpy_dependency_present(self) -> None:
        """numpy must be listed explicitly even if it's a transitive dependency."""
        content = REQUIREMENTS_TXT.read_text(encoding="utf-8").lower()
        assert "numpy" in content, "numpy must be listed in requirements.txt"


# ---------------------------------------------------------------------------
# TestPipelineCli — exécution en ligne de commande
# ---------------------------------------------------------------------------


class TestPipelineCli:
    """python -m src.pipeline <image_path> produces a JSON file in outputs/."""

    def test_main_module_exists(self) -> None:
        """src/pipeline.py must have a __main__ guard or src/__main__.py must exist."""
        pipeline_py = PROJECT_ROOT / "src" / "pipeline.py"
        main_py = PROJECT_ROOT / "src" / "__main__.py"
        pipeline_content = pipeline_py.read_text(encoding="utf-8")

        has_main_guard = 'if __name__ == "__main__"' in pipeline_content
        has_main_module = main_py.exists()

        assert has_main_guard or has_main_module, (
            "pipeline.py must have an `if __name__ == '__main__'` block "
            "or src/__main__.py must exist for CLI execution"
        )

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
    def test_run_pipeline_writes_json_to_output_dir(
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
        """run_pipeline with output_dir writes a valid JSON file."""
        img_path = tmp_path / "test_shelf.jpg"
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
        output_dir = tmp_path / "outputs"

        mock_preprocess.return_value = FAKE_IMAGE
        mock_segment.return_value = [FAKE_SPINE]
        mock_init_detector.return_value = MagicMock()
        mock_init_ocr.return_value = MagicMock()
        mock_detect.return_value = [
            {"bbox": [[0, 0], [50, 0], [50, 20], [0, 20]], "confidence": 0.9}
        ]
        mock_correct.return_value = FAKE_SPINE
        mock_recognize.return_value = [{"text": "Test Book", "confidence": 0.85}]
        mock_aggregate.return_value = {
            "text": "Test Book",
            "confidence": 0.85,
            "engine": "paddleocr",
        }
        mock_postprocess.return_value = {
            "raw_text": "Test Book",
            "clean_text": "Test Book",
            "title": "Test Book",
            "author": None,
        }
        mock_identify.return_value = {
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "1234567890",
            "confidence": 0.9,
            "provider": "openlibrary",
        }

        result = run_pipeline(str(img_path), output_dir=str(output_dir))

        json_file = output_dir / "test_shelf_result.json"
        assert json_file.exists(), "JSON output file must be created in output_dir"

        with open(json_file, encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded["image"] == "test_shelf.jpg"
        assert isinstance(loaded["books"], list)
        assert len(loaded["books"]) >= 1

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
    def test_output_dir_created_automatically(
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
        """Output directory is created if it does not exist."""
        img_path = tmp_path / "shelf.png"
        img_path.write_bytes(b"\x89PNG" + b"\x00" * 100)
        output_dir = tmp_path / "deep" / "nested" / "outputs"

        mock_preprocess.return_value = FAKE_IMAGE
        mock_segment.return_value = []
        mock_init_detector.return_value = MagicMock()
        mock_init_ocr.return_value = MagicMock()

        run_pipeline(str(img_path), output_dir=str(output_dir))

        assert output_dir.exists(), "Nested output directory must be auto-created"
        json_file = output_dir / "shelf_result.json"
        assert json_file.exists()


# ---------------------------------------------------------------------------
# TestJsonOutputStructure — structure JSON de sortie
# ---------------------------------------------------------------------------


class TestJsonOutputStructure:
    """JSON output contains all required keys with correct types."""

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
    def test_json_has_required_top_level_keys(
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
        img_path = tmp_path / "shelf.jpg"
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
        output_dir = tmp_path / "out"

        mock_preprocess.return_value = FAKE_IMAGE
        mock_segment.return_value = [FAKE_SPINE]
        mock_init_detector.return_value = MagicMock()
        mock_init_ocr.return_value = MagicMock()
        mock_detect.return_value = [
            {"bbox": [[0, 0], [50, 0], [50, 20], [0, 20]], "confidence": 0.9}
        ]
        mock_correct.return_value = FAKE_SPINE
        mock_recognize.return_value = [{"text": "Title", "confidence": 0.8}]
        mock_aggregate.return_value = {
            "text": "Title",
            "confidence": 0.8,
            "engine": "paddleocr",
        }
        mock_postprocess.return_value = {
            "raw_text": "Title",
            "clean_text": "Title",
            "title": "Title",
            "author": "Author",
        }
        mock_identify.return_value = {
            "title": "Title",
            "author": "Author",
            "isbn": "0000000000",
            "confidence": 0.95,
            "provider": "openlibrary",
        }

        run_pipeline(str(img_path), output_dir=str(output_dir))

        json_file = output_dir / "shelf_result.json"
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)

        assert "image" in data
        assert "num_spines_detected" in data
        assert "processing_time_s" in data
        assert "books" in data
        assert isinstance(data["processing_time_s"], (int, float))
        assert isinstance(data["num_spines_detected"], int)

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
    def test_book_entries_have_required_keys(
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
        """Each book in the books list must have title, author, confidence keys."""
        img_path = tmp_path / "shelf.jpg"
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_preprocess.return_value = FAKE_IMAGE
        mock_segment.return_value = [FAKE_SPINE, FAKE_SPINE.copy()]
        mock_init_detector.return_value = MagicMock()
        mock_init_ocr.return_value = MagicMock()
        mock_detect.return_value = [
            {"bbox": [[0, 0], [50, 0], [50, 20], [0, 20]], "confidence": 0.9}
        ]
        mock_correct.return_value = FAKE_SPINE
        mock_recognize.return_value = [{"text": "Book", "confidence": 0.7}]
        mock_aggregate.return_value = {
            "text": "Book",
            "confidence": 0.7,
            "engine": "paddleocr",
        }
        mock_postprocess.return_value = {
            "raw_text": "Book",
            "clean_text": "Book",
            "title": "Book",
            "author": None,
        }
        mock_identify.return_value = None

        result = run_pipeline(str(img_path))

        assert len(result["books"]) == 2
        for book in result["books"]:
            assert "title" in book
            assert "author" in book
            assert "confidence" in book
            assert "spine_id" in book
            assert "raw_text" in book

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
    def test_json_output_is_valid_json_file(
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
        """Written JSON file must be parseable without errors."""
        img_path = tmp_path / "photo.jpeg"
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
        output_dir = tmp_path / "out"

        mock_preprocess.return_value = FAKE_IMAGE
        mock_segment.return_value = []
        mock_init_detector.return_value = MagicMock()
        mock_init_ocr.return_value = MagicMock()

        run_pipeline(str(img_path), output_dir=str(output_dir))

        json_file = output_dir / "photo_result.json"
        assert json_file.exists()

        raw = json_file.read_text(encoding="utf-8")
        data = json.loads(raw)  # Must not raise
        assert isinstance(data, dict)


# ---------------------------------------------------------------------------
# TestPipelineEdgeCases — cas limites
# ---------------------------------------------------------------------------


class TestPipelineEdgeCases:
    """Edge cases for pipeline reproducibility."""

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
    def test_empty_shelf_produces_valid_result(
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
        """Image with no detected spines still produces a valid JSON result."""
        img_path = tmp_path / "empty.jpg"
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_preprocess.return_value = FAKE_IMAGE
        mock_segment.return_value = []
        mock_init_detector.return_value = MagicMock()
        mock_init_ocr.return_value = MagicMock()

        result = run_pipeline(str(img_path))

        assert result["num_spines_detected"] == 0
        assert result["books"] == []
        assert result["image"] == "empty.jpg"
        assert isinstance(result["processing_time_s"], float)

    def test_nonexistent_image_raises_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            run_pipeline("/totally/nonexistent/image.jpg")

    def test_non_image_file_raises_value_error(self, tmp_path: Path) -> None:
        txt = tmp_path / "data.csv"
        txt.write_text("col1,col2\n1,2")
        with pytest.raises(ValueError, match="Not a valid image file"):
            run_pipeline(str(txt))

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
    def test_pipeline_accepts_path_object(
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
        """run_pipeline must accept pathlib.Path, not just str."""
        img_path = tmp_path / "shelf.png"
        img_path.write_bytes(b"\x89PNG" + b"\x00" * 100)

        mock_preprocess.return_value = FAKE_IMAGE
        mock_segment.return_value = []
        mock_init_detector.return_value = MagicMock()
        mock_init_ocr.return_value = MagicMock()

        result = run_pipeline(img_path)  # Pass Path object, not str
        assert isinstance(result, dict)
        assert result["image"] == "shelf.png"


# ---------------------------------------------------------------------------
# TestNoImplicitDependencies — pas de dépendances implicites
# ---------------------------------------------------------------------------


class TestNoImplicitDependencies:
    """Pipeline must not require undocumented environment variables."""

    def test_pipeline_module_importable(self) -> None:
        """src.pipeline can be imported without any special env vars."""
        import importlib

        mod = importlib.import_module("src.pipeline")
        assert hasattr(mod, "run_pipeline")
        assert hasattr(mod, "export_json")

    def test_no_env_var_access_in_pipeline(self) -> None:
        """pipeline.py should not use os.environ or os.getenv directly."""
        pipeline_path = PROJECT_ROOT / "src" / "pipeline.py"
        content = pipeline_path.read_text(encoding="utf-8")

        assert "os.environ" not in content, (
            "pipeline.py must not access os.environ — "
            "all config should be via function arguments"
        )
        assert "os.getenv" not in content, (
            "pipeline.py must not use os.getenv — "
            "all config should be via function arguments"
        )
