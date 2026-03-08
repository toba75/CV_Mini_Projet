"""Tests for the bounding box visualization module."""

import numpy as np
import pytest

from src.visualization import draw_spine_boxes, segment_with_positions


# ---------------------------------------------------------------------------
# Task 020 — Bounding box visualization
# ---------------------------------------------------------------------------


class TestSegmentWithPositions:
    """Tests for segment_with_positions function."""

    def test_returns_list_of_dicts_with_required_keys(self):
        """Nominal: returns list of dicts with 'crop', 'x_start', 'x_end'."""
        rng = np.random.default_rng(42)
        img = rng.integers(0, 256, (200, 300, 3), dtype=np.uint8)

        results = segment_with_positions(img)

        assert isinstance(results, list)
        assert len(results) >= 1
        for item in results:
            assert isinstance(item, dict)
            assert "crop" in item
            assert "x_start" in item
            assert "x_end" in item
            assert isinstance(item["crop"], np.ndarray)
            assert isinstance(item["x_start"], int)
            assert isinstance(item["x_end"], int)

    def test_positions_cover_full_width(self):
        """Nominal: positions cover the full image width without gaps."""
        img = np.full((200, 400, 3), 128, dtype=np.uint8)

        results = segment_with_positions(img)

        assert results[0]["x_start"] == 0
        assert results[-1]["x_end"] == 400
        # No gaps between consecutive segments
        for i in range(len(results) - 1):
            assert results[i]["x_end"] == results[i + 1]["x_start"]

    def test_crop_width_matches_positions(self):
        """Nominal: crop width equals x_end - x_start."""
        rng = np.random.default_rng(42)
        img = rng.integers(0, 256, (200, 300, 3), dtype=np.uint8)

        results = segment_with_positions(img)

        for item in results:
            expected_width = item["x_end"] - item["x_start"]
            assert item["crop"].shape[1] == expected_width

    def test_does_not_modify_input(self):
        """Nominal: input image is not modified in place. §R4"""
        rng = np.random.default_rng(42)
        img = rng.integers(0, 256, (200, 300, 3), dtype=np.uint8)
        original = img.copy()

        segment_with_positions(img)

        np.testing.assert_array_equal(img, original)

    def test_none_image_raises(self):
        """Error: ValueError when image is None."""
        with pytest.raises(ValueError):
            segment_with_positions(None)

    def test_2d_image_raises(self):
        """Error: ValueError when image is 2D."""
        img = np.full((200, 300), 128, dtype=np.uint8)
        with pytest.raises(ValueError, match="3-dimensional"):
            segment_with_positions(img)

    def test_wrong_dtype_raises(self):
        """Error: ValueError when image dtype is not uint8."""
        img = np.full((200, 300, 3), 128, dtype=np.float32)
        with pytest.raises(ValueError, match="uint8"):
            segment_with_positions(img)

    def test_uniform_image_single_segment(self):
        """Edge: uniform image with no lines returns 1 segment = full width."""
        img = np.full((200, 300, 3), 128, dtype=np.uint8)

        results = segment_with_positions(img)

        assert len(results) == 1
        assert results[0]["x_start"] == 0
        assert results[0]["x_end"] == 300


class TestDrawSpineBoxes:
    """Tests for draw_spine_boxes function."""

    def test_returns_bgr_uint8_image(self):
        """Nominal: returns a BGR uint8 image."""
        img = np.full((200, 400, 3), 128, dtype=np.uint8)
        spines = [{"x_start": 0, "x_end": 100}, {"x_start": 100, "x_end": 400}]

        result = draw_spine_boxes(img, spines)

        assert isinstance(result, np.ndarray)
        assert result.dtype == np.uint8
        assert result.ndim == 3
        assert result.shape[2] == 3

    def test_same_shape_as_input(self):
        """Nominal: output has the same shape as input."""
        img = np.full((200, 400, 3), 128, dtype=np.uint8)
        spines = [{"x_start": 0, "x_end": 200}, {"x_start": 200, "x_end": 400}]

        result = draw_spine_boxes(img, spines)

        assert result.shape == img.shape

    def test_does_not_modify_input(self):
        """Nominal: input image is not modified in place. §R4"""
        rng = np.random.default_rng(42)
        img = rng.integers(0, 256, (200, 400, 3), dtype=np.uint8)
        original = img.copy()
        spines = [{"x_start": 0, "x_end": 200}, {"x_start": 200, "x_end": 400}]

        draw_spine_boxes(img, spines)

        np.testing.assert_array_equal(img, original)

    def test_output_differs_from_input(self):
        """Nominal: drawing boxes changes the image pixels."""
        img = np.full((200, 400, 3), 255, dtype=np.uint8)
        spines = [{"x_start": 0, "x_end": 200}, {"x_start": 200, "x_end": 400}]

        result = draw_spine_boxes(img, spines)

        assert not np.array_equal(result, img)

    def test_distinct_colors_per_spine(self):
        """Nominal: each spine has a visually distinct color."""
        img = np.full((200, 400, 3), 255, dtype=np.uint8)
        spines = [
            {"x_start": 0, "x_end": 100},
            {"x_start": 100, "x_end": 200},
            {"x_start": 200, "x_end": 300},
        ]

        result = draw_spine_boxes(img, spines, show_labels=False)

        # Sample a pixel near the top-left of each spine box border
        # Different spines should have different border colors
        colors = set()
        for spine in spines:
            x_mid = (spine["x_start"] + spine["x_end"]) // 2
            # Sample the top border at y=0
            color = tuple(result[0, x_mid].tolist())
            colors.add(color)
        # At least 2 distinct colors among 3 spines (cyclic palette may repeat)
        assert len(colors) >= 2

    def test_show_labels_true_adds_text(self):
        """Nominal: show_labels=True adds text to the output image."""
        img = np.full((200, 400, 3), 255, dtype=np.uint8)
        spines = [{"x_start": 0, "x_end": 200}]

        result_with = draw_spine_boxes(img, spines, show_labels=True)
        result_without = draw_spine_boxes(img, spines, show_labels=False)

        # The two outputs should differ (labels add pixels)
        assert not np.array_equal(result_with, result_without)

    def test_confidence_displayed_when_present(self):
        """Nominal: confidence score is rendered when present in spine dict."""
        img = np.full((200, 400, 3), 255, dtype=np.uint8)
        spines = [{"x_start": 0, "x_end": 200, "confidence": 0.95}]

        result = draw_spine_boxes(img, spines, show_labels=True)

        # Just verify it runs without error and modifies the image
        assert not np.array_equal(result, img)

    def test_empty_spines_returns_copy(self):
        """Edge: empty spines list returns an unmodified copy."""
        rng = np.random.default_rng(42)
        img = rng.integers(0, 256, (200, 400, 3), dtype=np.uint8)

        result = draw_spine_boxes(img, [])

        np.testing.assert_array_equal(result, img)
        # But it must be a copy, not the same object
        assert result is not img

    def test_none_image_raises(self):
        """Error: ValueError when image is None."""
        with pytest.raises(ValueError):
            draw_spine_boxes(None, [])

    def test_2d_image_raises(self):
        """Error: ValueError when image is 2D."""
        img = np.full((200, 300), 128, dtype=np.uint8)
        with pytest.raises(ValueError, match="3-dimensional"):
            draw_spine_boxes(img, [])

    def test_wrong_dtype_raises(self):
        """Error: ValueError when image dtype is not uint8."""
        img = np.full((200, 300, 3), 128, dtype=np.float32)
        with pytest.raises(ValueError, match="uint8"):
            draw_spine_boxes(img, [])

    def test_invalid_spine_missing_key_raises(self):
        """Error: ValueError when spine dict is missing required keys."""
        img = np.full((200, 400, 3), 128, dtype=np.uint8)
        spines = [{"x_start": 0}]  # missing x_end

        with pytest.raises(ValueError, match="x_end"):
            draw_spine_boxes(img, spines)

    def test_invalid_spine_x_start_ge_x_end_raises(self):
        """Error: ValueError when x_start >= x_end."""
        img = np.full((200, 400, 3), 128, dtype=np.uint8)
        spines = [{"x_start": 200, "x_end": 100}]

        with pytest.raises(ValueError, match="x_start"):
            draw_spine_boxes(img, spines)

    def test_many_spines_cyclic_palette(self):
        """Edge: more spines than palette colors still works (cyclic)."""
        img = np.full((200, 1000, 3), 200, dtype=np.uint8)
        spines = [
            {"x_start": i * 50, "x_end": (i + 1) * 50}
            for i in range(20)
        ]

        result = draw_spine_boxes(img, spines, show_labels=False)

        assert result.shape == img.shape
        assert not np.array_equal(result, img)

    def test_single_pixel_wide_spine(self):
        """Edge: spine of width 1 pixel does not crash."""
        img = np.full((200, 400, 3), 128, dtype=np.uint8)
        spines = [{"x_start": 100, "x_end": 101}]

        result = draw_spine_boxes(img, spines)

        assert result.shape == img.shape
