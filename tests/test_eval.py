"""Tests for eval module — full evaluation on annotated dataset."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.eval import (
    export_evaluation_results,
    generate_evaluation_report,
    identify_worst_images,
    run_full_evaluation,
)


def _make_ground_truth_csv(tmp_path: Path, images: int = 3, spines: int = 2) -> Path:
    """Create a ground truth CSV with the given number of images and spines."""
    csv_path = tmp_path / "ground_truth.csv"
    lines = ["image_filename,spine_index,title,author"]
    for i in range(1, images + 1):
        for j in range(1, spines + 1):
            lines.append(f"img{i:02d}.jpeg,{j},Title {j} Img{i},Author {j}")
    csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return csv_path


def _make_data_dir(tmp_path: Path, images: int = 3) -> Path:
    """Create a data directory with dummy image files."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    for i in range(1, images + 1):
        (data_dir / f"img{i:02d}.jpeg").write_bytes(b"fake image data")
    return data_dir


def _mock_pipeline_result(image_name: str, spines: int = 2) -> dict:
    """Build a fake pipeline result dict."""
    books = []
    for j in range(1, spines + 1):
        books.append({
            "spine_id": j,
            "raw_text": f"Title {j} Img{image_name}",
            "title": f"Title {j} Img{image_name}",
            "author": f"Author {j}",
        })
    return {
        "image": image_name,
        "num_spines_detected": spines,
        "processing_time_s": 1.5,
        "books": books,
    }


class TestRunFullEvaluation:
    """Tests for run_full_evaluation function."""

    @patch("src.eval.run_pipeline")
    def test_returns_dict_with_per_image_and_summary(self, mock_pipeline, tmp_path):
        gt_csv = _make_ground_truth_csv(tmp_path, images=2, spines=2)
        data_dir = _make_data_dir(tmp_path, images=2)
        output_dir = tmp_path / "output"

        mock_pipeline.side_effect = lambda path, **kw: _mock_pipeline_result(
            Path(path).name, spines=2
        )

        result = run_full_evaluation(data_dir, gt_csv, output_dir)
        assert "per_image" in result
        assert "summary" in result
        assert isinstance(result["per_image"], list)
        assert isinstance(result["summary"], dict)

    @patch("src.eval.run_pipeline")
    def test_per_image_contains_all_images(self, mock_pipeline, tmp_path):
        gt_csv = _make_ground_truth_csv(tmp_path, images=3, spines=2)
        data_dir = _make_data_dir(tmp_path, images=3)
        output_dir = tmp_path / "output"

        mock_pipeline.side_effect = lambda path, **kw: _mock_pipeline_result(
            Path(path).name, spines=2
        )

        result = run_full_evaluation(data_dir, gt_csv, output_dir)
        assert len(result["per_image"]) == 3

    @patch("src.eval.run_pipeline")
    def test_per_image_has_required_keys(self, mock_pipeline, tmp_path):
        gt_csv = _make_ground_truth_csv(tmp_path, images=1, spines=2)
        data_dir = _make_data_dir(tmp_path, images=1)
        output_dir = tmp_path / "output"

        mock_pipeline.side_effect = lambda path, **kw: _mock_pipeline_result(
            Path(path).name, spines=2
        )

        result = run_full_evaluation(data_dir, gt_csv, output_dir)
        entry = result["per_image"][0]
        assert "image" in entry
        assert "detection_rate" in entry
        assert "cer" in entry
        assert "identification_rate" in entry
        assert "time_s" in entry

    @patch("src.eval.run_pipeline")
    def test_summary_has_means_and_stds(self, mock_pipeline, tmp_path):
        gt_csv = _make_ground_truth_csv(tmp_path, images=2, spines=2)
        data_dir = _make_data_dir(tmp_path, images=2)
        output_dir = tmp_path / "output"

        mock_pipeline.side_effect = lambda path, **kw: _mock_pipeline_result(
            Path(path).name, spines=2
        )

        result = run_full_evaluation(data_dir, gt_csv, output_dir)
        summary = result["summary"]
        assert "mean_detection_rate" in summary
        assert "mean_cer" in summary
        assert "mean_identification_rate" in summary
        assert "mean_time_s" in summary
        assert "std_detection_rate" in summary
        assert "std_cer" in summary
        assert "std_identification_rate" in summary
        assert "std_time_s" in summary

    @patch("src.eval.run_pipeline")
    def test_perfect_pipeline_returns_expected_metrics(self, mock_pipeline, tmp_path):
        gt_csv = _make_ground_truth_csv(tmp_path, images=2, spines=2)
        data_dir = _make_data_dir(tmp_path, images=2)
        output_dir = tmp_path / "output"

        def perfect_result(path, **kw):
            stem = Path(path).stem
            idx = int(stem.replace("img", ""))
            books = []
            for j in range(1, 3):
                title = f"Title {j} Img{idx}"
                books.append({
                    "spine_id": j,
                    "raw_text": title,
                    "title": title,
                    "author": f"Author {j}",
                })
            return {
                "image": Path(path).name,
                "num_spines_detected": 2,
                "processing_time_s": 1.0,
                "books": books,
            }

        mock_pipeline.side_effect = perfect_result

        result = run_full_evaluation(data_dir, gt_csv, output_dir)
        summary = result["summary"]
        assert summary["mean_detection_rate"] == pytest.approx(1.0)
        assert summary["mean_cer"] == pytest.approx(0.0)
        assert summary["mean_identification_rate"] == pytest.approx(1.0)

    @patch("src.eval.run_pipeline")
    def test_measures_time_with_perf_counter(self, mock_pipeline, tmp_path):
        gt_csv = _make_ground_truth_csv(tmp_path, images=1, spines=1)
        data_dir = _make_data_dir(tmp_path, images=1)
        output_dir = tmp_path / "output"

        mock_pipeline.side_effect = lambda path, **kw: _mock_pipeline_result(
            Path(path).name, spines=1
        )

        result = run_full_evaluation(data_dir, gt_csv, output_dir)
        assert result["per_image"][0]["time_s"] >= 0.0

    def test_raises_on_invalid_ground_truth_path(self, tmp_path):
        data_dir = _make_data_dir(tmp_path, images=1)
        output_dir = tmp_path / "output"
        with pytest.raises(ValueError):
            run_full_evaluation(data_dir, tmp_path / "nonexistent.csv", output_dir)

    def test_raises_on_invalid_data_dir(self, tmp_path):
        gt_csv = _make_ground_truth_csv(tmp_path, images=1, spines=1)
        output_dir = tmp_path / "output"
        with pytest.raises(ValueError):
            run_full_evaluation(tmp_path / "nonexistent_dir", gt_csv, output_dir)

    @patch("src.eval.run_pipeline")
    def test_ocr_engine_forwarded_to_pipeline(self, mock_pipeline, tmp_path):
        gt_csv = _make_ground_truth_csv(tmp_path, images=1, spines=1)
        data_dir = _make_data_dir(tmp_path, images=1)
        output_dir = tmp_path / "output"

        mock_pipeline.side_effect = lambda path, **kw: _mock_pipeline_result(
            Path(path).name, spines=1
        )

        run_full_evaluation(data_dir, gt_csv, output_dir, ocr_engine="tesseract")
        _, kwargs = mock_pipeline.call_args
        assert kwargs.get("ocr_engine") == "tesseract"


class TestGenerateEvaluationReport:
    """Tests for generate_evaluation_report function."""

    def _make_eval_results(self) -> dict:
        return {
            "per_image": [
                {
                    "image": "img01.jpeg",
                    "detection_rate": 1.0,
                    "cer": 0.05,
                    "identification_rate": 0.8,
                    "time_s": 2.0,
                },
                {
                    "image": "img02.jpeg",
                    "detection_rate": 0.5,
                    "cer": 0.30,
                    "identification_rate": 0.5,
                    "time_s": 3.0,
                },
            ],
            "summary": {
                "mean_detection_rate": 0.75,
                "mean_cer": 0.175,
                "mean_identification_rate": 0.65,
                "mean_time_s": 2.5,
                "std_detection_rate": 0.25,
                "std_cer": 0.125,
                "std_identification_rate": 0.15,
                "std_time_s": 0.5,
            },
        }

    def test_returns_markdown_string(self):
        report = generate_evaluation_report(self._make_eval_results())
        assert isinstance(report, str)
        assert len(report) > 0

    def test_contains_table_header(self):
        report = generate_evaluation_report(self._make_eval_results())
        assert "Métrique" in report or "Metric" in report
        assert "Résultat" in report or "Result" in report
        assert "Cible" in report or "Target" in report

    def test_contains_target_comparison(self):
        report = generate_evaluation_report(self._make_eval_results())
        assert "80%" in report or "0.8" in report
        assert "20%" in report or "0.2" in report
        assert "60%" in report or "0.6" in report
        assert "30" in report

    def test_contains_per_image_results(self):
        report = generate_evaluation_report(self._make_eval_results())
        assert "img01.jpeg" in report
        assert "img02.jpeg" in report

    def test_indicates_targets_achieved(self):
        results = self._make_eval_results()
        report = generate_evaluation_report(results)
        # The report should indicate whether targets are met or not
        assert "✓" in report or "✗" in report or "Oui" in report or "Non" in report

    def test_raises_on_empty_results(self):
        with pytest.raises(ValueError):
            generate_evaluation_report({"per_image": [], "summary": {}})


class TestExportEvaluationResults:
    """Tests for export_evaluation_results function."""

    def _make_eval_results(self) -> dict:
        return {
            "per_image": [
                {
                    "image": "img01.jpeg",
                    "detection_rate": 1.0,
                    "cer": 0.05,
                    "identification_rate": 0.8,
                    "time_s": 2.0,
                },
            ],
            "summary": {
                "mean_detection_rate": 1.0,
                "mean_cer": 0.05,
                "mean_identification_rate": 0.8,
                "mean_time_s": 2.0,
                "std_detection_rate": 0.0,
                "std_cer": 0.0,
                "std_identification_rate": 0.0,
                "std_time_s": 0.0,
            },
        }

    def test_creates_json_file(self, tmp_path):
        output_path = tmp_path / "results.json"
        result_path = export_evaluation_results(self._make_eval_results(), output_path)
        assert result_path.exists()
        assert result_path.suffix == ".json"

    def test_json_content_matches(self, tmp_path):
        output_path = tmp_path / "results.json"
        export_evaluation_results(self._make_eval_results(), output_path)
        with open(output_path, encoding="utf-8") as f:
            loaded = json.load(f)
        assert "per_image" in loaded
        assert "summary" in loaded
        assert len(loaded["per_image"]) == 1

    def test_returns_path_object(self, tmp_path):
        output_path = tmp_path / "results.json"
        result = export_evaluation_results(self._make_eval_results(), output_path)
        assert isinstance(result, Path)

    def test_creates_parent_directories(self, tmp_path):
        output_path = tmp_path / "sub" / "dir" / "results.json"
        result_path = export_evaluation_results(self._make_eval_results(), output_path)
        assert result_path.exists()

    def test_raises_on_empty_results(self, tmp_path):
        output_path = tmp_path / "results.json"
        with pytest.raises(ValueError):
            export_evaluation_results({"per_image": [], "summary": {}}, output_path)


class TestIdentifyWorstImages:
    """Tests for identify_worst_images function."""

    def _make_eval_results(self) -> dict:
        per_image = []
        for i in range(10):
            per_image.append({
                "image": f"img{i:02d}.jpeg",
                "detection_rate": 1.0,
                "cer": i * 0.1,
                "identification_rate": 1.0,
                "time_s": 1.0,
            })
        return {
            "per_image": per_image,
            "summary": {
                "mean_detection_rate": 1.0,
                "mean_cer": 0.45,
                "mean_identification_rate": 1.0,
                "mean_time_s": 1.0,
                "std_detection_rate": 0.0,
                "std_cer": 0.3,
                "std_identification_rate": 0.0,
                "std_time_s": 0.0,
            },
        }

    def test_returns_list_of_dicts(self):
        result = identify_worst_images(self._make_eval_results())
        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)

    def test_default_returns_5_images(self):
        result = identify_worst_images(self._make_eval_results())
        assert len(result) == 5

    def test_custom_n(self):
        result = identify_worst_images(self._make_eval_results(), n=3)
        assert len(result) == 3

    def test_sorted_by_worst_cer_first(self):
        result = identify_worst_images(self._make_eval_results(), n=5)
        cers = [item["cer"] for item in result]
        assert cers == sorted(cers, reverse=True)

    def test_worst_image_has_highest_cer(self):
        result = identify_worst_images(self._make_eval_results(), n=1)
        assert result[0]["image"] == "img09.jpeg"
        assert result[0]["cer"] == pytest.approx(0.9)

    def test_each_item_has_required_keys(self):
        result = identify_worst_images(self._make_eval_results(), n=1)
        item = result[0]
        assert "image" in item
        assert "cer" in item

    def test_raises_on_empty_per_image(self):
        with pytest.raises(ValueError):
            identify_worst_images({"per_image": [], "summary": {}})

    def test_n_larger_than_dataset(self):
        results = self._make_eval_results()
        result = identify_worst_images(results, n=20)
        assert len(result) == 10
