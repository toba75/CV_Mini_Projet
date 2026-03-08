"""Tests for project structure and module importability."""

from pathlib import Path

import pytest

# Project root: two levels up from this test file
ROOT = Path(__file__).resolve().parent.parent


class TestDirectoryStructure:
    """Verify that all required directories exist."""

    @pytest.mark.parametrize(
        "directory",
        [
            "src",
            "tests",
            "data/raw",
            "data/ground_truth",
            "outputs",
            "notebooks",
        ],
    )
    def test_directory_exists(self, directory: str) -> None:
        path = ROOT / directory
        assert path.is_dir(), f"Directory '{directory}' does not exist at {path}"


class TestSourceFiles:
    """Verify that all required source files exist."""

    EXPECTED_MODULES = [
        "preprocess.py",
        "segment.py",
        "detect_text.py",
        "ocr.py",
        "postprocess.py",
        "pipeline.py",
        "app.py",
        "eval_utils.py",
    ]

    @pytest.mark.parametrize("filename", EXPECTED_MODULES)
    def test_source_file_exists(self, filename: str) -> None:
        path = ROOT / "src" / filename
        assert path.is_file(), f"Source file 'src/{filename}' does not exist"

    def test_src_init_exists(self) -> None:
        path = ROOT / "src" / "__init__.py"
        assert path.is_file(), "src/__init__.py does not exist"

    def test_tests_init_exists(self) -> None:
        path = ROOT / "tests" / "__init__.py"
        assert path.is_file(), "tests/__init__.py does not exist"


class TestModuleImportability:
    """Verify that all src modules are importable."""

    @pytest.mark.parametrize(
        "module_name",
        [
            "preprocess",
            "segment",
            "detect_text",
            "ocr",
            "postprocess",
            "pipeline",
            "app",
            "eval_utils",
        ],
    )
    def test_module_importable(self, module_name: str) -> None:
        import importlib

        module = importlib.import_module(f"src.{module_name}")
        assert module is not None

    def test_from_src_import_all_modules(self) -> None:
        from src import (  # noqa: F401
            app,
            detect_text,
            eval_utils,
            ocr,
            pipeline,
            postprocess,
            preprocess,
            segment,
        )


class TestErrorCases:
    """Verify error scenarios raise expected exceptions."""

    def test_import_nonexistent_module_raises_error(self) -> None:
        import importlib

        with pytest.raises(ModuleNotFoundError):
            importlib.import_module("src.nonexistent_module")


class TestEdgeCases:
    """Verify edge cases: source files are non-empty and contain a docstring."""

    SOURCE_FILES = [
        "preprocess.py",
        "segment.py",
        "detect_text.py",
        "ocr.py",
        "postprocess.py",
        "pipeline.py",
        "app.py",
        "eval_utils.py",
        "__init__.py",
    ]

    @pytest.mark.parametrize("filename", SOURCE_FILES)
    def test_source_file_not_empty(self, filename: str) -> None:
        path = ROOT / "src" / filename
        content = path.read_text(encoding="utf-8")
        assert len(content.strip()) > 0, f"src/{filename} is empty"

    @pytest.mark.parametrize("filename", SOURCE_FILES)
    def test_source_file_has_docstring(self, filename: str) -> None:
        path = ROOT / "src" / filename
        content = path.read_text(encoding="utf-8").strip()
        assert content.startswith('"""') or content.startswith("'''"), (
            f"src/{filename} does not start with a module-level docstring"
        )


class TestRequirements:
    """Verify that requirements.txt exists and lists key dependencies."""

    def test_requirements_file_exists(self) -> None:
        path = ROOT / "requirements.txt"
        assert path.is_file(), "requirements.txt does not exist"

    @pytest.mark.parametrize(
        "dependency",
        [
            "opencv-python",
            "paddleocr",
            "paddlepaddle",
            "torch",
            "torchvision",
            "streamlit",
            "pillow",
            "pandas",
            "pytesseract",
            "rapidfuzz",
            "requests",
        ],
    )
    def test_dependency_listed(self, dependency: str) -> None:
        content = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
        assert dependency.lower() in content, (
            f"Dependency '{dependency}' not found in requirements.txt"
        )
