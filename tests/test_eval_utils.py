"""Tests for eval_utils module — ground truth loading and validation."""

import pandas as pd
import pytest

from src.eval_utils import load_ground_truth


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
