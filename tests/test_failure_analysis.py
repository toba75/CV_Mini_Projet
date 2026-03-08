"""Tests for failure analysis module."""

import pytest

from src.failure_analysis import (
    analyze_failures,
    categorize_failure,
    export_failure_report,
    generate_failure_report,
)


# ---------------------------------------------------------------------------
# categorize_failure
# ---------------------------------------------------------------------------


class TestCategorizeFailure:
    """Tests for categorize_failure."""

    def test_segmentation_failure(self):
        metrics = {"detection_rate": 0.3, "cer": 0.1, "identification_rate": 0.8}
        assert categorize_failure(metrics) == "segmentation"

    def test_ocr_failure(self):
        metrics = {"detection_rate": 0.8, "cer": 0.7, "identification_rate": 0.8}
        assert categorize_failure(metrics) == "ocr"

    def test_identification_failure(self):
        metrics = {"detection_rate": 0.8, "cer": 0.1, "identification_rate": 0.2}
        assert categorize_failure(metrics) == "identification"

    def test_multiple_failures(self):
        metrics = {"detection_rate": 0.3, "cer": 0.7, "identification_rate": 0.1}
        assert categorize_failure(metrics) == "multiple"

    def test_two_failures_segmentation_ocr(self):
        metrics = {"detection_rate": 0.4, "cer": 0.6, "identification_rate": 0.5}
        assert categorize_failure(metrics) == "multiple"

    def test_acceptable(self):
        metrics = {"detection_rate": 0.8, "cer": 0.1, "identification_rate": 0.5}
        assert categorize_failure(metrics) == "acceptable"

    def test_boundary_segmentation(self):
        """detection_rate exactly 0.5 is NOT a segmentation failure."""
        metrics = {"detection_rate": 0.5, "cer": 0.1, "identification_rate": 0.5}
        assert categorize_failure(metrics) == "acceptable"

    def test_boundary_cer(self):
        """cer exactly 0.5 is NOT an OCR failure."""
        metrics = {"detection_rate": 0.8, "cer": 0.5, "identification_rate": 0.5}
        assert categorize_failure(metrics) == "acceptable"

    def test_boundary_identification(self):
        """identification_rate exactly 0.3 is NOT an identification failure."""
        metrics = {"detection_rate": 0.8, "cer": 0.1, "identification_rate": 0.3}
        assert categorize_failure(metrics) == "acceptable"

    def test_missing_key_raises(self):
        with pytest.raises(ValueError, match="detection_rate"):
            categorize_failure({"cer": 0.1, "identification_rate": 0.5})

    def test_empty_dict_raises(self):
        with pytest.raises(ValueError):
            categorize_failure({})


# ---------------------------------------------------------------------------
# analyze_failures
# ---------------------------------------------------------------------------


class TestAnalyzeFailures:
    """Tests for analyze_failures."""

    def _make_eval_results(self, per_image_list):
        return {"per_image": per_image_list, "summary": {}}

    def test_mixed_dataset(self):
        per_image = [
            {"image": "a.jpg", "detection_rate": 0.3, "cer": 0.1, "identification_rate": 0.8},
            {"image": "b.jpg", "detection_rate": 0.9, "cer": 0.8, "identification_rate": 0.7},
            {"image": "c.jpg", "detection_rate": 0.9, "cer": 0.1, "identification_rate": 0.9},
            {"image": "d.jpg", "detection_rate": 0.2, "cer": 0.9, "identification_rate": 0.1},
        ]
        result = analyze_failures(self._make_eval_results(per_image))

        assert "categories" in result
        assert "worst_per_category" in result
        assert "total_failures" in result

        assert result["categories"]["segmentation"] == 1
        assert result["categories"]["ocr"] == 1
        assert result["categories"]["multiple"] == 1
        assert result["categories"].get("acceptable", 0) == 1
        assert result["total_failures"] == 3

    def test_all_acceptable(self):
        per_image = [
            {"image": "a.jpg", "detection_rate": 0.9, "cer": 0.1, "identification_rate": 0.8},
            {"image": "b.jpg", "detection_rate": 0.8, "cer": 0.2, "identification_rate": 0.5},
        ]
        result = analyze_failures(self._make_eval_results(per_image))
        assert result["total_failures"] == 0
        assert result["categories"]["acceptable"] == 2

    def test_all_failing(self):
        per_image = [
            {"image": "a.jpg", "detection_rate": 0.1, "cer": 0.9, "identification_rate": 0.0},
            {"image": "b.jpg", "detection_rate": 0.2, "cer": 0.8, "identification_rate": 0.1},
        ]
        result = analyze_failures(self._make_eval_results(per_image))
        assert result["total_failures"] == 2

    def test_empty_results_raises(self):
        with pytest.raises(ValueError, match="per_image"):
            analyze_failures({"per_image": [], "summary": {}})

    def test_worst_per_category_contains_image_name(self):
        per_image = [
            {"image": "bad_seg.jpg", "detection_rate": 0.1, "cer": 0.1, "identification_rate": 0.8},
            {"image": "worse_seg.jpg", "detection_rate": 0.05, "cer": 0.1, "identification_rate": 0.8},
        ]
        result = analyze_failures(self._make_eval_results(per_image))
        # worst segmentation = lowest detection_rate
        assert result["worst_per_category"]["segmentation"] == "worse_seg.jpg"

    def test_missing_per_image_key_raises(self):
        with pytest.raises(ValueError):
            analyze_failures({"summary": {}})


# ---------------------------------------------------------------------------
# generate_failure_report
# ---------------------------------------------------------------------------


class TestGenerateFailureReport:
    """Tests for generate_failure_report."""

    def _make_analysis(self):
        return {
            "categories": {"segmentation": 2, "ocr": 1, "acceptable": 1},
            "worst_per_category": {
                "segmentation": "bad_seg.jpg",
                "ocr": "bad_ocr.jpg",
            },
            "total_failures": 3,
        }

    def test_report_is_markdown(self):
        report = generate_failure_report(self._make_analysis())
        assert isinstance(report, str)
        assert report.startswith("#")

    def test_report_contains_summary_section(self):
        report = generate_failure_report(self._make_analysis())
        assert "segmentation" in report.lower()
        assert "ocr" in report.lower()

    def test_report_contains_categories(self):
        report = generate_failure_report(self._make_analysis())
        assert "2" in report  # segmentation count
        assert "1" in report  # ocr count

    def test_report_contains_improvements(self):
        report = generate_failure_report(self._make_analysis())
        lower = report.lower()
        assert "amélioration" in lower or "improvement" in lower or "piste" in lower

    def test_empty_analysis_raises(self):
        with pytest.raises(ValueError):
            generate_failure_report({"categories": {}, "worst_per_category": {}, "total_failures": 0})


# ---------------------------------------------------------------------------
# export_failure_report
# ---------------------------------------------------------------------------


class TestExportFailureReport:
    """Tests for export_failure_report."""

    def test_export_creates_file(self, tmp_path):
        analysis = {
            "categories": {"segmentation": 1},
            "worst_per_category": {"segmentation": "img.jpg"},
            "total_failures": 1,
        }
        output = tmp_path / "report.md"
        result = export_failure_report(analysis, output)

        assert result == output
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "#" in content

    def test_export_creates_parent_dirs(self, tmp_path):
        analysis = {
            "categories": {"ocr": 1},
            "worst_per_category": {"ocr": "img.jpg"},
            "total_failures": 1,
        }
        output = tmp_path / "sub" / "dir" / "report.md"
        result = export_failure_report(analysis, output)
        assert result.exists()

    def test_export_returns_path_object(self, tmp_path):
        from pathlib import Path

        analysis = {
            "categories": {"ocr": 1},
            "worst_per_category": {"ocr": "img.jpg"},
            "total_failures": 1,
        }
        result = export_failure_report(analysis, str(tmp_path / "report.md"))
        assert isinstance(result, Path)
