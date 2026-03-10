"""Tests for demo images and performance — TDD RED phase for task #031.

Validates:
- data/demo/ directory structure with 3-4 images
- expected_results.json structure and consistency
- Pipeline benchmark timing logic on demo images
- Streamlit app loads and processes demo images without error
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Root of the project
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEMO_DIR = PROJECT_ROOT / "data" / "demo"
EXPECTED_RESULTS_PATH = DEMO_DIR / "expected_results.json"

VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def expected_results() -> dict:
    """Load expected_results.json and return parsed dict."""
    if not EXPECTED_RESULTS_PATH.exists():
        pytest.fail(f"expected_results.json not found at {EXPECTED_RESULTS_PATH}")
    return json.loads(EXPECTED_RESULTS_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Test: demo directory existence and image count
# ---------------------------------------------------------------------------


class TestDemoDirectoryStructure:
    """#031 — demo directory must exist with 3-4 images."""

    def test_demo_directory_exists(self) -> None:
        """data/demo/ directory must exist."""
        assert DEMO_DIR.is_dir(), f"Demo directory not found: {DEMO_DIR}"

    def test_demo_contains_3_to_4_images(self) -> None:
        """data/demo/ must contain between 3 and 4 image files."""
        images = [
            f for f in DEMO_DIR.iterdir()
            if f.is_file() and f.suffix.lower() in VALID_IMAGE_EXTENSIONS
        ]
        assert 3 <= len(images) <= 4, (
            f"Expected 3-4 images in data/demo/, found {len(images)}: "
            f"{[f.name for f in images]}"
        )

    def test_demo_images_are_valid_files(self) -> None:
        """Each image in data/demo/ should be non-empty."""
        images = [
            f for f in DEMO_DIR.iterdir()
            if f.is_file() and f.suffix.lower() in VALID_IMAGE_EXTENSIONS
        ]
        for img_path in images:
            assert img_path.stat().st_size > 0, (
                f"Image file is empty: {img_path.name}"
            )


# ---------------------------------------------------------------------------
# Test: expected_results.json structure
# ---------------------------------------------------------------------------


class TestExpectedResultsStructure:
    """#031 — expected_results.json must have correct structure."""

    def test_expected_results_file_exists(self) -> None:
        """expected_results.json must exist in data/demo/."""
        assert EXPECTED_RESULTS_PATH.is_file(), (
            f"expected_results.json not found at {EXPECTED_RESULTS_PATH}"
        )

    def test_expected_results_is_valid_json(self) -> None:
        """expected_results.json must be valid JSON."""
        raw = EXPECTED_RESULTS_PATH.read_text(encoding="utf-8")
        try:
            json.loads(raw)
        except json.JSONDecodeError as exc:
            pytest.fail(f"expected_results.json is not valid JSON: {exc}")

    def test_expected_results_has_images_key(self, expected_results: dict) -> None:
        """Top-level must have an 'images' key containing a list."""
        assert "images" in expected_results, (
            "expected_results.json must have an 'images' key"
        )
        assert isinstance(expected_results["images"], list), (
            "'images' must be a list"
        )

    def test_expected_results_contains_3_to_4_entries(
        self, expected_results: dict
    ) -> None:
        """images list must have 3-4 entries."""
        count = len(expected_results["images"])
        assert 3 <= count <= 4, (
            f"Expected 3-4 image entries, found {count}"
        )

    def test_each_entry_has_required_keys(self, expected_results: dict) -> None:
        """Each entry must have 'image', 'description', 'expected_books'."""
        required_keys = {"image", "description", "expected_books"}
        for i, entry in enumerate(expected_results["images"]):
            missing = required_keys - set(entry.keys())
            assert not missing, (
                f"Entry {i} missing keys: {missing}"
            )

    def test_expected_books_is_list_with_at_least_3(
        self, expected_results: dict
    ) -> None:
        """Each entry must have at least 3 expected_books."""
        for i, entry in enumerate(expected_results["images"]):
            books = entry["expected_books"]
            assert isinstance(books, list), (
                f"Entry {i}: expected_books must be a list"
            )
            assert len(books) >= 3, (
                f"Entry {i} ({entry['image']}): "
                f"expected at least 3 books, found {len(books)}"
            )

    def test_expected_books_have_title_key(self, expected_results: dict) -> None:
        """Each book in expected_books must have a 'title' key."""
        for i, entry in enumerate(expected_results["images"]):
            for j, book in enumerate(entry["expected_books"]):
                assert "title" in book, (
                    f"Entry {i}, book {j}: missing 'title' key"
                )

    def test_image_files_referenced_exist(self, expected_results: dict) -> None:
        """Every image referenced in expected_results.json must exist in data/demo/."""
        for entry in expected_results["images"]:
            img_path = DEMO_DIR / entry["image"]
            assert img_path.is_file(), (
                f"Referenced image not found: {entry['image']}"
            )


# ---------------------------------------------------------------------------
# Test: benchmark / performance measurement logic
# ---------------------------------------------------------------------------


class TestDemoBenchmark:
    """#031 — benchmark measures pipeline execution time per demo image."""

    @patch("src.pipeline.run_pipeline")
    def test_benchmark_demo_measures_time(
        self, mock_run_pipeline: MagicMock
    ) -> None:
        """Benchmark function returns timing per image."""
        from src.demo_benchmark import benchmark_demo_images

        mock_run_pipeline.return_value = {
            "image": "test.jpg",
            "num_spines_detected": 3,
            "processing_time_s": 1.5,
            "books": [],
        }

        results = benchmark_demo_images()

        assert isinstance(results, list)
        assert len(results) > 0
        for entry in results:
            assert "image" in entry
            assert "processing_time_s" in entry
            assert isinstance(entry["processing_time_s"], (int, float))
            assert entry["processing_time_s"] >= 0

    @patch("src.pipeline.run_pipeline")
    def test_benchmark_demo_under_30s(self, mock_run_pipeline: MagicMock) -> None:
        """Each demo image processing time must be < 30s (mocked)."""
        from src.demo_benchmark import benchmark_demo_images

        mock_run_pipeline.return_value = {
            "image": "test.jpg",
            "num_spines_detected": 3,
            "processing_time_s": 5.0,
            "books": [
                {
                    "spine_id": 1,
                    "raw_text": "Test",
                    "title": "Test",
                    "author": "Author",
                    "isbn": None,
                    "confidence": 0.9,
                }
            ],
        }

        results = benchmark_demo_images()

        for entry in results:
            assert entry["processing_time_s"] < 30, (
                f"Image {entry['image']} took {entry['processing_time_s']}s (>= 30s)"
            )

    @patch("src.pipeline.run_pipeline")
    def test_benchmark_returns_num_books(self, mock_run_pipeline: MagicMock) -> None:
        """Benchmark entries include num_books detected."""
        from src.demo_benchmark import benchmark_demo_images

        mock_run_pipeline.return_value = {
            "image": "test.jpg",
            "num_spines_detected": 2,
            "processing_time_s": 2.0,
            "books": [
                {
                    "spine_id": 1, "raw_text": "A", "title": "A",
                    "author": "B", "isbn": None, "confidence": 0.8,
                },
                {
                    "spine_id": 2, "raw_text": "C", "title": "C",
                    "author": "D", "isbn": None, "confidence": 0.7,
                },
            ],
        }

        results = benchmark_demo_images()

        for entry in results:
            assert "num_books" in entry
            assert isinstance(entry["num_books"], int)

    @patch("src.pipeline.run_pipeline")
    def test_benchmark_handles_pipeline_error(
        self, mock_run_pipeline: MagicMock
    ) -> None:
        """If pipeline raises on one image, benchmark records error without crashing."""
        from src.demo_benchmark import benchmark_demo_images

        mock_run_pipeline.side_effect = RuntimeError("Pipeline crashed")

        results = benchmark_demo_images()

        assert isinstance(results, list)
        for entry in results:
            assert "error" in entry


# ---------------------------------------------------------------------------
# Test: Streamlit app can load demo images
# ---------------------------------------------------------------------------


class TestStreamlitDemoLoading:
    """#031 — app.py helpers work with demo image paths."""

    def test_demo_images_have_valid_extensions_for_pipeline(self) -> None:
        """All demo images must have extensions accepted by the pipeline."""
        pipeline_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
        images = [
            f for f in DEMO_DIR.iterdir()
            if f.is_file() and f.suffix.lower() in VALID_IMAGE_EXTENSIONS
        ]
        for img_path in images:
            assert img_path.suffix.lower() in pipeline_extensions, (
                f"Image {img_path.name} has unsupported extension"
            )

    @patch("src.pipeline.run_pipeline")
    def test_pipeline_accepts_demo_image_paths(
        self, mock_run_pipeline: MagicMock
    ) -> None:
        """run_pipeline can be called with each demo image path (mocked)."""
        mock_run_pipeline.return_value = {
            "image": "demo.jpg",
            "num_spines_detected": 3,
            "processing_time_s": 2.0,
            "books": [],
        }

        images = [
            f for f in DEMO_DIR.iterdir()
            if f.is_file() and f.suffix.lower() in VALID_IMAGE_EXTENSIONS
        ]
        for img_path in images:
            mock_run_pipeline.return_value["image"] = img_path.name
            result = mock_run_pipeline(str(img_path))
            assert "books" in result
            assert "processing_time_s" in result
