"""Tests for eval_utils module — ground truth loading and validation."""

import json

import pandas as pd
import pytest

from src.eval_utils import (
    compute_cer,
    compute_detection_rate,
    compute_identification_rate,
    evaluate_dataset,
    evaluate_image,
    load_ground_truth,
)


class TestLoadGroundTruth:
    """Tests for load_ground_truth function."""

    def _write_csv(self, path, content: str) -> str:
        """Helper: write CSV content to a file and return its path as string."""
        csv_file = path / "ground_truth.csv"
        csv_file.write_text(content, encoding="utf-8")
        return str(csv_file)

    def test_loads_valid_csv_returns_dataframe(self, tmp_path):
        csv_path = self._write_csv(
            tmp_path,
            (
                "image_filename,spine_index,title,author\n"
                "img1.jpeg,1,Title A,Author A\n"
                "img1.jpeg,2,Title B,Author B\n"
            ),
        )
        result = load_ground_truth(csv_path)
        assert isinstance(result, pd.DataFrame)

    def test_dataframe_has_required_columns(self, tmp_path):
        csv_path = self._write_csv(
            tmp_path,
            (
                "image_filename,spine_index,title,author\n"
                "img1.jpeg,1,Title A,Author A\n"
            ),
        )
        df = load_ground_truth(csv_path)
        for col in ["image_filename", "spine_index", "title", "author"]:
            assert col in df.columns

    def test_raises_value_error_if_file_not_found(self, tmp_path):
        with pytest.raises(ValueError, match="not found"):
            load_ground_truth(str(tmp_path / "nonexistent.csv"))

    def test_raises_value_error_if_columns_missing(self, tmp_path):
        csv_path = self._write_csv(
            tmp_path,
            "image_filename,spine_index\nimg1.jpeg,1\n",
        )
        with pytest.raises(ValueError, match="[Mm]issing.*column"):
            load_ground_truth(csv_path)

    def test_raises_value_error_if_title_empty(self, tmp_path):
        csv_path = self._write_csv(
            tmp_path,
            (
                "image_filename,spine_index,title,author\n"
                "img1.jpeg,1,,Author A\n"
            ),
        )
        with pytest.raises(ValueError, match="empty"):
            load_ground_truth(csv_path)

    def test_raises_value_error_if_title_whitespace_only(self, tmp_path):
        csv_path = self._write_csv(
            tmp_path,
            (
                "image_filename,spine_index,title,author\n"
                "img1.jpeg,1,   ,Author A\n"
            ),
        )
        with pytest.raises(ValueError, match="empty"):
            load_ground_truth(csv_path)

    def test_ground_truth_has_at_least_15_unique_images(self, tmp_path):
        lines = ["image_filename,spine_index,title,author"]
        for i in range(1, 16):
            for j in range(1, 4):
                lines.append(f"img{i:02d}.jpeg,{j},Title {j},Author {j}")
        csv_path = self._write_csv(tmp_path, "\n".join(lines) + "\n")
        df = load_ground_truth(csv_path)
        assert df["image_filename"].nunique() >= 15

    def test_each_image_has_at_least_3_titles(self, tmp_path):
        lines = ["image_filename,spine_index,title,author"]
        for i in range(1, 16):
            for j in range(1, 5):
                lines.append(f"img{i:02d}.jpeg,{j},Title {j},Author {j}")
        csv_path = self._write_csv(tmp_path, "\n".join(lines) + "\n")
        df = load_ground_truth(csv_path)
        counts = df.groupby("image_filename").size()
        assert (counts >= 3).all()

    def test_returns_correct_row_count(self, tmp_path):
        csv_path = self._write_csv(
            tmp_path,
            (
                "image_filename,spine_index,title,author\n"
                "img1.jpeg,1,Title A,Author A\n"
                "img1.jpeg,2,Title B,Author B\n"
                "img2.jpeg,1,Title C,Author C\n"
            ),
        )
        df = load_ground_truth(csv_path)
        assert len(df) == 3


class TestComputeDetectionRate:
    """Tests for compute_detection_rate function."""

    def test_perfect_detection_returns_1(self):
        assert compute_detection_rate(5, 5) == 1.0

    def test_partial_detection_returns_ratio(self):
        result = compute_detection_rate(3, 5)
        assert result == pytest.approx(0.6)

    def test_zero_ground_truth_returns_0(self):
        assert compute_detection_rate(3, 0) == 0.0

    def test_over_detection_capped_at_1(self):
        assert compute_detection_rate(10, 5) == 1.0

    def test_zero_predicted_returns_0(self):
        assert compute_detection_rate(0, 5) == 0.0


class TestComputeCer:
    """Tests for compute_cer function."""

    def test_identical_texts_returns_0(self):
        assert compute_cer("hello", "hello") == 0.0

    def test_different_texts_returns_positive(self):
        result = compute_cer("helo", "hello")
        assert result > 0.0

    def test_empty_ground_truth_nonempty_predicted_returns_1(self):
        assert compute_cer("hello", "") == 1.0

    def test_both_empty_returns_0(self):
        assert compute_cer("", "") == 0.0

    def test_completely_different_texts(self):
        result = compute_cer("abc", "xyz")
        assert result == pytest.approx(1.0)


class TestComputeIdentificationRate:
    """Tests for compute_identification_rate function."""

    def test_all_matched_returns_1(self):
        predicted = ["The Great Gatsby", "1984", "Dune"]
        ground_truth = ["The Great Gatsby", "1984", "Dune"]
        assert compute_identification_rate(predicted, ground_truth) == 1.0

    def test_none_matched_returns_0(self):
        predicted = ["xxxx", "yyyy"]
        ground_truth = ["The Great Gatsby", "1984"]
        assert compute_identification_rate(predicted, ground_truth) == 0.0

    def test_empty_ground_truth_returns_0(self):
        assert compute_identification_rate(["something"], []) == 0.0

    def test_empty_predicted_returns_0(self):
        assert compute_identification_rate([], ["The Great Gatsby"]) == 0.0

    def test_partial_match(self):
        predicted = ["The Great Gatsby", "xxxx"]
        ground_truth = ["The Great Gatsby", "1984"]
        result = compute_identification_rate(predicted, ground_truth)
        assert result == pytest.approx(0.5)


class TestEvaluateImage:
    """Tests for evaluate_image function."""

    def test_full_evaluation_returns_three_metrics(self):
        pipeline_result = {
            "books": [
                {"raw_text": "The Great Gatsby", "title": "The Great Gatsby"},
                {"raw_text": "1984", "title": "1984"},
            ],
        }
        ground_truth = {
            "titles": ["The Great Gatsby", "1984"],
            "count": 2,
        }
        result = evaluate_image(pipeline_result, ground_truth)
        assert "detection_rate" in result
        assert "cer" in result
        assert "identification_rate" in result
        assert result["detection_rate"] == 1.0
        assert result["identification_rate"] == 1.0

    def test_evaluation_with_mismatched_counts(self):
        pipeline_result = {
            "books": [
                {"raw_text": "The Great Gatsby", "title": "The Great Gatsby"},
            ],
        }
        ground_truth = {
            "titles": ["The Great Gatsby", "1984"],
            "count": 2,
        }
        result = evaluate_image(pipeline_result, ground_truth)
        assert result["detection_rate"] == pytest.approx(0.5)


class TestEvaluateDataset:
    """Tests for evaluate_dataset function."""

    def test_evaluate_with_temp_files(self, tmp_path):
        # Create results directory with JSON files
        results_dir = tmp_path / "results"
        results_dir.mkdir()

        result1 = {
            "image": "img01.jpeg",
            "books": [
                {"raw_text": "Title A", "title": "Title A"},
                {"raw_text": "Title B", "title": "Title B"},
            ],
        }
        (results_dir / "img01.json").write_text(
            json.dumps(result1), encoding="utf-8"
        )

        # Create ground truth directory with CSV
        gt_dir = tmp_path / "ground_truth"
        gt_dir.mkdir()
        csv_content = (
            "image_filename,spine_index,title,author\n"
            "img01.jpeg,1,Title A,Author A\n"
            "img01.jpeg,2,Title B,Author B\n"
        )
        (gt_dir / "ground_truth.csv").write_text(csv_content, encoding="utf-8")

        result = evaluate_dataset(str(results_dir), str(gt_dir))
        assert "per_image" in result
        assert "average" in result
        assert len(result["per_image"]) == 1
        assert result["average"]["detection_rate"] == 1.0

    def test_evaluate_empty_dataset(self, tmp_path):
        results_dir = tmp_path / "results"
        results_dir.mkdir()
        gt_dir = tmp_path / "ground_truth"
        gt_dir.mkdir()
        csv_content = "image_filename,spine_index,title,author\n"
        (gt_dir / "ground_truth.csv").write_text(csv_content, encoding="utf-8")

        result = evaluate_dataset(str(results_dir), str(gt_dir))
        assert result["per_image"] == []
        assert result["average"]["detection_rate"] == 0.0
