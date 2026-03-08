"""Tests for the naive Hough segmentation module."""

import cv2
import numpy as np
import pytest

from src.segment import (
    classify_spine,
    crop_spines,
    detect_empty_regions,
    detect_vertical_lines,
    filter_lines,
    merge_thin_spines,
    segment,
    segment_robust,
    split_spines,
    split_wide_gaps,
)


class TestDetectVerticalLines:
    """Tests for detect_vertical_lines function."""

    def test_detects_vertical_lines_sorted_by_x(self):
        """Nominal: vertical lines are detected and sorted by x position."""
        img = np.full((300, 400, 3), 255, dtype=np.uint8)
        # Draw two vertical lines at x=200 and x=100
        cv2.line(img, (200, 0), (200, 299), (0, 0, 0), 2)
        cv2.line(img, (100, 0), (100, 299), (0, 0, 0), 2)

        lines = detect_vertical_lines(img)

        assert len(lines) >= 2
        # Sorted by x position (mean of x1, x2)
        x_positions = [(x1 + x2) / 2 for x1, _, x2, _ in lines]
        assert x_positions == sorted(x_positions)

    def test_returns_list_of_tuples(self):
        """Nominal: return type is a list of (x1, y1, x2, y2) tuples."""
        img = np.full((300, 400, 3), 255, dtype=np.uint8)
        cv2.line(img, (150, 0), (150, 299), (0, 0, 0), 2)

        lines = detect_vertical_lines(img)

        assert isinstance(lines, list)
        for line in lines:
            assert isinstance(line, tuple)
            assert len(line) == 4

    def test_filters_non_vertical_lines(self):
        """Nominal: oblique lines (angle > threshold) are filtered out."""
        img = np.full((300, 400, 3), 255, dtype=np.uint8)
        # Draw a horizontal line — should be filtered
        cv2.line(img, (0, 150), (399, 150), (0, 0, 0), 2)
        # Draw a 45-degree diagonal — should be filtered
        cv2.line(img, (50, 50), (250, 250), (0, 0, 0), 2)

        lines = detect_vertical_lines(img)

        assert len(lines) == 0

    def test_none_image_raises(self):
        """Error: ValueError when image is None."""
        with pytest.raises(ValueError):
            detect_vertical_lines(None)

    def test_empty_image_raises(self):
        """Error: ValueError when image is empty."""
        with pytest.raises(ValueError):
            detect_vertical_lines(np.array([]))

    def test_no_lines_returns_empty_list(self):
        """Edge: uniform image with no edges returns empty list."""
        img = np.full((200, 300, 3), 128, dtype=np.uint8)

        lines = detect_vertical_lines(img)

        assert lines == []

    def test_small_image(self):
        """Edge: very small image does not crash."""
        img = np.full((10, 10, 3), 200, dtype=np.uint8)

        lines = detect_vertical_lines(img)

        assert isinstance(lines, list)

    def test_2d_image_raises(self):
        """Error: ValueError when image is 2D (ndim != 3)."""
        img = np.full((200, 300), 128, dtype=np.uint8)
        with pytest.raises(ValueError, match="3-dimensional"):
            detect_vertical_lines(img)

    def test_wrong_dtype_raises(self):
        """Error: ValueError when image dtype is not uint8."""
        img = np.full((200, 300, 3), 128, dtype=np.float32)
        with pytest.raises(ValueError, match="uint8"):
            detect_vertical_lines(img)

    def test_does_not_modify_input(self):
        """Nominal: input image is not modified in place. §R4"""
        img = np.random.default_rng(42).integers(
            0, 256, (200, 300, 3), dtype=np.uint8,
        )
        original = img.copy()

        detect_vertical_lines(img)

        np.testing.assert_array_equal(img, original)


class TestSplitSpines:
    """Tests for split_spines function."""

    def test_crops_non_empty(self):
        """Nominal: all returned crops have width > 0 and height > 0."""
        img = np.full((200, 400, 3), 128, dtype=np.uint8)
        lines = [(100, 0, 100, 199), (250, 0, 250, 199)]

        crops = split_spines(img, lines)

        assert len(crops) >= 1
        for crop in crops:
            assert crop.shape[0] > 0
            assert crop.shape[1] > 0

    def test_covers_full_width(self):
        """Nominal: crops cover the entire width of the image."""
        img = np.full((200, 400, 3), 128, dtype=np.uint8)
        lines = [(100, 0, 100, 199), (300, 0, 300, 199)]

        crops = split_spines(img, lines)

        total_width = sum(crop.shape[1] for crop in crops)
        assert total_width == img.shape[1]

    def test_empty_lines_returns_full_image(self):
        """Edge: empty lines list returns the full image as single crop."""
        img = np.random.default_rng(42).integers(
            0, 256, (200, 300, 3), dtype=np.uint8,
        )

        crops = split_spines(img, [])

        assert len(crops) == 1
        np.testing.assert_array_equal(crops[0], img)

    def test_does_not_modify_input(self):
        """Nominal: input image is not modified in place."""
        img = np.random.default_rng(42).integers(
            0, 256, (100, 200, 3), dtype=np.uint8,
        )
        original = img.copy()
        lines = [(100, 0, 100, 99)]

        split_spines(img, lines)

        np.testing.assert_array_equal(img, original)

    def test_none_image_raises(self):
        """Error: ValueError when image is None."""
        with pytest.raises(ValueError):
            split_spines(None, [])

    def test_empty_image_raises(self):
        """Error: ValueError when image is empty."""
        with pytest.raises(ValueError):
            split_spines(np.array([]), [])

    def test_2d_image_raises(self):
        """Error: ValueError when image is 2D (ndim != 3)."""
        img = np.full((200, 300), 128, dtype=np.uint8)
        with pytest.raises(ValueError, match="3-dimensional"):
            split_spines(img, [])

    def test_wrong_dtype_raises(self):
        """Error: ValueError when image dtype is not uint8."""
        img = np.full((200, 300, 3), 128, dtype=np.float32)
        with pytest.raises(ValueError, match="uint8"):
            split_spines(img, [])


class TestSegment:
    """Tests for segment orchestration function."""

    def test_no_lines_returns_full_image(self):
        """Nominal: uniform image (no lines) returns 1 crop = full image."""
        img = np.full((200, 300, 3), 128, dtype=np.uint8)

        crops = segment(img)

        assert len(crops) == 1
        np.testing.assert_array_equal(crops[0], img)

    def test_single_line_returns_two_crops(self):
        """Nominal: image with one vertical line returns 2 crops."""
        img = np.full((300, 400, 3), 255, dtype=np.uint8)
        cv2.line(img, (200, 0), (200, 299), (0, 0, 0), 2)

        crops = segment(img)

        assert len(crops) == 2

    def test_returns_at_least_one_crop(self):
        """Nominal: segment always returns at least 1 crop."""
        img = np.full((100, 100, 3), 200, dtype=np.uint8)

        crops = segment(img)

        assert len(crops) >= 1

    def test_none_image_raises(self):
        """Error: ValueError when image is None."""
        with pytest.raises(ValueError):
            segment(None)

    def test_empty_image_raises(self):
        """Error: ValueError when image is empty."""
        with pytest.raises(ValueError):
            segment(np.array([]))

    def test_2d_image_raises(self):
        """Error: ValueError when image is 2D (ndim != 3)."""
        img = np.full((200, 300), 128, dtype=np.uint8)
        with pytest.raises(ValueError, match="3-dimensional"):
            segment(img)

    def test_wrong_dtype_raises(self):
        """Error: ValueError when image dtype is not uint8."""
        img = np.full((200, 300, 3), 128, dtype=np.float32)
        with pytest.raises(ValueError, match="uint8"):
            segment(img)

    def test_small_image(self):
        """Edge: very small image returns at least 1 crop."""
        img = np.full((5, 5, 3), 100, dtype=np.uint8)

        crops = segment(img)

        assert len(crops) >= 1


# ---------------------------------------------------------------------------
# Task 010 — Refined segmentation
# ---------------------------------------------------------------------------


class TestFilterLines:
    """Tests for filter_lines function."""

    def test_keeps_long_vertical_lines(self):
        """Nominal: lines that are long enough and vertical are kept."""
        # image_height=300, line from y=0 to y=299 → length 299 > 0.3*300=90
        lines = [(100, 0, 100, 299)]
        result = filter_lines(lines, image_height=300)
        assert len(result) == 1

    def test_removes_short_lines(self):
        """Nominal: lines shorter than min_length_ratio * image_height are removed."""
        # line from y=0 to y=20 → length 20, threshold = 0.3*300 = 90
        lines = [(100, 0, 100, 20)]
        result = filter_lines(lines, image_height=300, min_length_ratio=0.3)
        assert len(result) == 0

    def test_removes_inclined_lines(self):
        """Nominal: lines too inclined from vertical are removed."""
        # dx=100, dy=200 → angle ~26.5° from vertical, threshold=15°
        lines = [(100, 0, 200, 200)]
        result = filter_lines(lines, image_height=300, max_angle_deg=15.0)
        assert len(result) == 0

    def test_keeps_slightly_inclined_lines(self):
        """Nominal: lines within angle threshold are kept."""
        # dx=5, dy=250 → angle ~1.15° from vertical
        lines = [(100, 0, 105, 250)]
        result = filter_lines(lines, image_height=300, max_angle_deg=15.0)
        assert len(result) == 1

    def test_empty_lines_returns_empty(self):
        """Edge: empty input returns empty output."""
        result = filter_lines([], image_height=300)
        assert result == []


class TestSplitWideGaps:
    """Tests for split_wide_gaps function."""

    def test_does_not_modify_normal_gaps(self):
        """Nominal: gaps within threshold are not subdivided."""
        # x_cuts at 100, 200 → gap = 100, median_width = 100 → 2*100=200 > 100
        lines = [(100, 0, 100, 299), (200, 0, 200, 299)]
        result = split_wide_gaps(lines, image_width=400, median_width=100.0)
        assert len(result) == len(lines)

    def test_inserts_virtual_lines_for_wide_gap(self):
        """Nominal: a gap > 2*median_width gets subdivided."""
        # x_cuts at 50 and 350 → gap=300, median_width=50 → threshold=100
        lines = [(50, 0, 50, 299), (350, 0, 350, 299)]
        result = split_wide_gaps(lines, image_width=400, median_width=50.0)
        # Should insert virtual lines to subdivide the gap
        assert len(result) > len(lines)

    def test_empty_lines_returns_empty(self):
        """Edge: empty input returns empty output."""
        result = split_wide_gaps([], image_width=400, median_width=50.0)
        assert result == []

    def test_single_line_returns_single(self):
        """Edge: single line has no gap to split."""
        lines = [(200, 0, 200, 299)]
        result = split_wide_gaps(lines, image_width=400, median_width=50.0)
        assert len(result) == 1


class TestCropSpines:
    """Tests for crop_spines function."""

    def test_returns_crops_with_min_width(self):
        """Nominal: all crops have width >= min_width."""
        img = np.full((200, 400, 3), 128, dtype=np.uint8)
        lines = [(100, 0, 100, 199), (250, 0, 250, 199)]
        crops = crop_spines(img, lines, min_width=20)
        for crop in crops:
            assert crop.shape[1] >= 20

    def test_ignores_narrow_crops(self):
        """Nominal: crops narrower than min_width are excluded."""
        img = np.full((200, 400, 3), 128, dtype=np.uint8)
        # Lines at x=5 and x=10 → gap of 5, then x=300 → gap of 290
        lines = [(5, 0, 5, 199), (10, 0, 10, 199), (300, 0, 300, 199)]
        crops = crop_spines(img, lines, min_width=20)
        for crop in crops:
            assert crop.shape[1] >= 20

    def test_returns_full_image_if_no_lines(self):
        """Edge: returns full image as single crop when no lines."""
        img = np.full((200, 400, 3), 128, dtype=np.uint8)
        crops = crop_spines(img, [], min_width=20)
        assert len(crops) == 1
        assert crops[0].shape[1] == 400

    def test_covers_full_width(self):
        """Nominal: total width of crops covers entire image width (excluding narrow)."""
        img = np.full((200, 400, 3), 128, dtype=np.uint8)
        lines = [(100, 0, 100, 199), (250, 0, 250, 199)]
        crops = crop_spines(img, lines, min_width=1)
        total_width = sum(c.shape[1] for c in crops)
        assert total_width == 400

    def test_none_image_raises(self):
        """Error: ValueError when image is None."""
        with pytest.raises(ValueError):
            crop_spines(None, [])

    def test_empty_image_raises(self):
        """Error: ValueError when image is empty."""
        with pytest.raises(ValueError):
            crop_spines(np.array([]), [])


# ---------------------------------------------------------------------------
# Task 019 — Edge cases segmentation
# ---------------------------------------------------------------------------


class TestDetectEmptyRegions:
    """Tests for detect_empty_regions function."""

    def test_uniform_crops_detected_as_empty(self):
        """Nominal: uniform (low variance) crops are flagged as empty."""
        img = np.full((200, 400, 3), 128, dtype=np.uint8)
        # Two uniform crops (no texture)
        crop1 = np.full((200, 50, 3), 128, dtype=np.uint8)
        crop2 = np.full((200, 50, 3), 200, dtype=np.uint8)
        crops = [crop1, crop2]

        result = detect_empty_regions(img, crops)

        assert isinstance(result, list)
        assert len(result) == 2
        # Both uniform crops should be flagged as empty
        assert all(r is True for r in result)

    def test_textured_crops_not_empty(self):
        """Nominal: crops with texture (high variance) are not flagged."""
        rng = np.random.default_rng(42)
        img = rng.integers(0, 256, (200, 400, 3), dtype=np.uint8)
        crop1 = rng.integers(0, 256, (200, 50, 3), dtype=np.uint8)
        crops = [crop1]

        result = detect_empty_regions(img, crops)

        assert result[0] is False

    def test_mixed_crops(self):
        """Nominal: mix of empty and textured crops."""
        rng = np.random.default_rng(42)
        img = np.full((200, 400, 3), 128, dtype=np.uint8)
        uniform_crop = np.full((200, 50, 3), 128, dtype=np.uint8)
        textured_crop = rng.integers(0, 256, (200, 50, 3), dtype=np.uint8)
        crops = [uniform_crop, textured_crop]

        result = detect_empty_regions(img, crops)

        assert result[0] is True
        assert result[1] is False

    def test_none_image_raises(self):
        """Error: ValueError when image is None."""
        with pytest.raises(ValueError):
            detect_empty_regions(None, [])

    def test_empty_crops_list(self):
        """Edge: empty crops list returns empty result."""
        img = np.full((200, 400, 3), 128, dtype=np.uint8)
        result = detect_empty_regions(img, [])
        assert result == []

    def test_custom_variance_threshold(self):
        """Nominal: variance_threshold parameter controls sensitivity."""
        # Crop with slight noise — low variance
        rng = np.random.default_rng(42)
        base = np.full((200, 50, 3), 128, dtype=np.uint8)
        noise = rng.integers(-5, 6, base.shape, dtype=np.int16)
        crop = np.clip(base.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        img = np.full((200, 400, 3), 128, dtype=np.uint8)

        # With high threshold, it should be empty
        result_high = detect_empty_regions(img, [crop], variance_threshold=100.0)
        assert result_high[0] is True

        # With very low threshold, it should not be empty
        result_low = detect_empty_regions(img, [crop], variance_threshold=0.1)
        assert result_low[0] is False


class TestClassifySpine:
    """Tests for classify_spine function."""

    def test_returns_dict_with_required_keys(self):
        """Nominal: returns dict with 'is_book' and 'reason' keys."""
        rng = np.random.default_rng(42)
        crop = rng.integers(0, 256, (300, 50, 3), dtype=np.uint8)

        result = classify_spine(crop)

        assert isinstance(result, dict)
        assert "is_book" in result
        assert "reason" in result
        assert isinstance(result["is_book"], bool)
        assert isinstance(result["reason"], str)

    def test_tall_textured_crop_is_book(self):
        """Nominal: tall crop with texture is classified as book."""
        rng = np.random.default_rng(42)
        # Aspect ratio h/w = 300/40 = 7.5 — tall, book-like
        crop = rng.integers(0, 256, (300, 40, 3), dtype=np.uint8)

        result = classify_spine(crop)

        assert result["is_book"] is True

    def test_uniform_crop_is_not_book(self):
        """Nominal: uniform crop (no texture) is not a book."""
        crop = np.full((300, 40, 3), 128, dtype=np.uint8)

        result = classify_spine(crop)

        assert result["is_book"] is False

    def test_square_crop_is_not_book(self):
        """Nominal: square crop (low aspect ratio) is not a book spine."""
        rng = np.random.default_rng(42)
        crop = rng.integers(0, 256, (100, 100, 3), dtype=np.uint8)

        result = classify_spine(crop)

        assert result["is_book"] is False

    def test_wide_crop_is_not_book(self):
        """Nominal: wider-than-tall crop is not a book spine."""
        rng = np.random.default_rng(42)
        crop = rng.integers(0, 256, (50, 200, 3), dtype=np.uint8)

        result = classify_spine(crop)

        assert result["is_book"] is False

    def test_none_image_raises(self):
        """Error: ValueError when crop is None."""
        with pytest.raises(ValueError):
            classify_spine(None)

    def test_2d_image_raises(self):
        """Error: ValueError when crop is 2D."""
        crop = np.full((200, 50), 128, dtype=np.uint8)
        with pytest.raises(ValueError, match="3-dimensional"):
            classify_spine(crop)


class TestMergeThinSpines:
    """Tests for merge_thin_spines function."""

    def test_merges_adjacent_thin_crops(self):
        """Nominal: adjacent thin crops are merged into one."""
        # total_width = 5+5+100 = 110, ratio=0.1 → min_width=11
        # thin crops (5px) < 11 → thin, wide (100px) >= 11 → not thin
        thin1 = np.full((200, 5, 3), 100, dtype=np.uint8)
        thin2 = np.full((200, 5, 3), 120, dtype=np.uint8)
        wide = np.full((200, 100, 3), 150, dtype=np.uint8)
        crops = [thin1, thin2, wide]

        result = merge_thin_spines(crops, min_width_ratio=0.1)

        # thin1 + thin2 should be merged, wide stays
        assert len(result) < len(crops)
        # The merged crop should have width = 10
        assert result[0].shape[1] == 10
        assert result[-1].shape[1] == 100

    def test_no_thin_crops_unchanged(self):
        """Nominal: no thin crops means no merging."""
        crop1 = np.full((200, 100, 3), 100, dtype=np.uint8)
        crop2 = np.full((200, 80, 3), 150, dtype=np.uint8)
        crops = [crop1, crop2]

        result = merge_thin_spines(crops, min_width_ratio=0.1)

        assert len(result) == 2

    def test_all_thin_crops_merged_into_one(self):
        """Edge: all crops are thin — they merge into a single crop."""
        # total_width = 3+4+3 = 10, ratio=0.5 → min_width=5
        # All crops (3, 4, 3) < 5 → all thin → merged into one
        thin1 = np.full((200, 3, 3), 100, dtype=np.uint8)
        thin2 = np.full((200, 4, 3), 120, dtype=np.uint8)
        thin3 = np.full((200, 3, 3), 140, dtype=np.uint8)
        crops = [thin1, thin2, thin3]

        result = merge_thin_spines(crops, min_width_ratio=0.5)

        assert len(result) == 1
        assert result[0].shape[1] == 10

    def test_empty_crops_returns_empty(self):
        """Edge: empty input returns empty output."""
        result = merge_thin_spines([], min_width_ratio=0.02)
        assert result == []

    def test_single_thin_crop_stays(self):
        """Edge: single thin crop is returned as-is (nothing to merge with)."""
        thin = np.full((200, 3, 3), 100, dtype=np.uint8)

        result = merge_thin_spines([thin], min_width_ratio=0.5)

        assert len(result) == 1

    def test_preserves_height(self):
        """Nominal: merged crop preserves the height of input crops."""
        thin1 = np.full((200, 5, 3), 100, dtype=np.uint8)
        thin2 = np.full((200, 5, 3), 120, dtype=np.uint8)
        crops = [thin1, thin2]

        result = merge_thin_spines(crops, min_width_ratio=0.6)

        assert result[0].shape[0] == 200


class TestSegmentRobust:
    """Tests for segment_robust orchestrator."""

    def test_returns_list_of_dicts(self):
        """Nominal: returns list of dicts with 'crop' and 'is_book' keys."""
        rng = np.random.default_rng(42)
        img = rng.integers(0, 256, (300, 400, 3), dtype=np.uint8)

        results = segment_robust(img)

        assert isinstance(results, list)
        assert len(results) >= 1
        for item in results:
            assert isinstance(item, dict)
            assert "crop" in item
            assert "is_book" in item
            assert isinstance(item["crop"], np.ndarray)
            assert isinstance(item["is_book"], bool)

    def test_none_image_raises(self):
        """Error: ValueError when image is None."""
        with pytest.raises(ValueError):
            segment_robust(None)

    def test_empty_image_raises(self):
        """Error: ValueError when image is empty."""
        with pytest.raises(ValueError):
            segment_robust(np.array([]))

    def test_2d_image_raises(self):
        """Error: ValueError when image is 2D."""
        img = np.full((200, 300), 128, dtype=np.uint8)
        with pytest.raises(ValueError, match="3-dimensional"):
            segment_robust(img)

    def test_uniform_image_single_result(self):
        """Edge: uniform image returns at least one result."""
        img = np.full((200, 300, 3), 128, dtype=np.uint8)

        results = segment_robust(img)

        assert len(results) >= 1

    def test_does_not_modify_input(self):
        """Nominal: input image is not modified in place. §R4"""
        rng = np.random.default_rng(42)
        img = rng.integers(0, 256, (200, 300, 3), dtype=np.uint8)
        original = img.copy()

        segment_robust(img)

        np.testing.assert_array_equal(img, original)

    def test_regression_segment_still_works(self):
        """Regression: original segment() function still works."""
        img = np.full((300, 400, 3), 255, dtype=np.uint8)
        cv2.line(img, (200, 0), (200, 299), (0, 0, 0), 2)

        crops = segment(img)

        assert len(crops) == 2
