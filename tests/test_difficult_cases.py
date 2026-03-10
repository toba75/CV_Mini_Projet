"""Tests for difficult detection/OCR cases — robustness and preprocessing.

Covers five difficult scenarios using synthetic images:
1. Very small text (fine texture)
2. Very low contrast (gold-on-dark simulated)
3. Very narrow spine (< 30px wide)
4. Noisy image
5. Nearly uniform image (no text)

All tests verify that the pipeline does NOT crash and that filtering
functions handle edge cases gracefully.
"""

from unittest.mock import MagicMock

import cv2
import numpy as np
import pytest

from src.detect_text import (
    detect_text_regions,
    filter_by_aspect_ratio,
    filter_small_regions,
)
from src.preprocess import apply_clahe, enhance_for_difficult_text

# ---------------------------------------------------------------------------
# Synthetic image builders
# ---------------------------------------------------------------------------

def _make_small_text_image(
    height: int = 200, width: int = 300,
) -> np.ndarray:
    """Create a BGR image with very small text-like texture (fine lines)."""
    img = np.full((height, width, 3), 220, dtype=np.uint8)
    # Draw tiny horizontal lines to simulate small text
    for y in range(10, height - 10, 4):
        cv2.line(img, (20, y), (width - 20, y), (30, 30, 30), 1)
    return img


def _make_low_contrast_image(
    height: int = 200, width: int = 300,
) -> np.ndarray:
    """Create a dark image with faint gold-ish text (very low contrast)."""
    img = np.full((height, width, 3), 25, dtype=np.uint8)
    # Simulate gold text on dark background: small contrast delta
    cv2.putText(
        img, "GOLD", (30, height // 2),
        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (35, 35, 40), 2,
    )
    return img


def _make_narrow_spine_image(
    height: int = 300, width: int = 20,
) -> np.ndarray:
    """Create a very narrow BGR image simulating a thin book spine."""
    img = np.full((height, width, 3), 180, dtype=np.uint8)
    # Small vertical line to simulate text
    mid_x = width // 2
    cv2.line(img, (mid_x, 20), (mid_x, height - 20), (40, 40, 40), 1)
    return img


def _make_noisy_image(
    height: int = 200, width: int = 300,
) -> np.ndarray:
    """Create a BGR image with heavy Gaussian noise."""
    rng = np.random.default_rng(42)
    img = rng.integers(0, 256, (height, width, 3), dtype=np.uint8)
    return img


def _make_uniform_image(
    height: int = 200, width: int = 300,
) -> np.ndarray:
    """Create a nearly uniform BGR image with no text content."""
    img = np.full((height, width, 3), 128, dtype=np.uint8)
    return img


def _mock_detector_no_results() -> MagicMock:
    """Return a mock detector that finds no text."""
    detector = MagicMock()
    detector.ocr.return_value = [None]
    return detector


def _mock_detector_with_results() -> MagicMock:
    """Return a mock detector with realistic PaddleOCR detections."""
    detector = MagicMock()
    detector.ocr.return_value = [
        [
            [[[10.0, 20.0], [100.0, 20.0], [100.0, 50.0], [10.0, 50.0]], 0.95],
            [[[150.0, 60.0], [250.0, 60.0], [250.0, 90.0], [150.0, 90.0]], 0.82],
        ]
    ]
    return detector


# ---------------------------------------------------------------------------
# Tests — Pipeline robustness on difficult images
# ---------------------------------------------------------------------------

class TestDifficultCasesRobustness:
    """Pipeline must NOT crash on difficult input images."""

    def test_small_text_no_crash(self):
        """Robustness: small-text image does not crash detect_text_regions."""
        img = _make_small_text_image()
        detector = _mock_detector_no_results()

        result = detect_text_regions(img, detector=detector)

        assert isinstance(result, list)

    def test_low_contrast_no_crash(self):
        """Robustness: low-contrast image does not crash detect_text_regions."""
        img = _make_low_contrast_image()
        detector = _mock_detector_no_results()

        result = detect_text_regions(img, detector=detector)

        assert isinstance(result, list)

    def test_narrow_spine_no_crash(self):
        """Robustness: very narrow spine image does not crash detect_text_regions."""
        img = _make_narrow_spine_image()
        detector = _mock_detector_no_results()

        result = detect_text_regions(img, detector=detector)

        assert isinstance(result, list)

    def test_noisy_image_no_crash(self):
        """Robustness: heavily noisy image does not crash detect_text_regions."""
        img = _make_noisy_image()
        detector = _mock_detector_no_results()

        result = detect_text_regions(img, detector=detector)

        assert isinstance(result, list)

    def test_uniform_image_no_crash(self):
        """Robustness: uniform image (no text) does not crash detect_text_regions."""
        img = _make_uniform_image()
        detector = _mock_detector_no_results()

        result = detect_text_regions(img, detector=detector)

        assert isinstance(result, list)

    def test_uniform_image_returns_empty(self):
        """Edge: uniform image with no detections returns empty list."""
        img = _make_uniform_image()
        detector = _mock_detector_no_results()

        result = detect_text_regions(img, detector=detector)

        assert result == []


# ---------------------------------------------------------------------------
# Tests — Filtering on difficult-case regions
# ---------------------------------------------------------------------------

class TestFilteringOnDifficultCases:
    """Filtering functions must handle edge-case regions gracefully."""

    def test_filter_small_regions_on_narrow_spine(self):
        """Edge: tiny regions from narrow spine are filtered out."""
        # Simulate very small detections from a narrow spine
        regions = [
            {"bbox": [[0, 0], [5, 0], [5, 3], [0, 3]], "confidence": 0.8},
        ]
        result = filter_small_regions(regions, min_area=100)

        assert len(result) == 0

    def test_filter_aspect_ratio_on_narrow_spine(self):
        """Edge: extreme aspect ratio from narrow spine is filtered out."""
        # 5 wide x 200 tall → ratio = 0.025
        regions = [
            {"bbox": [[0, 0], [5, 0], [5, 200], [0, 200]], "confidence": 0.9},
        ]
        result = filter_by_aspect_ratio(regions, min_ratio=0.1, max_ratio=10.0)

        assert len(result) == 0

    def test_filter_keeps_valid_region_on_noisy_image(self):
        """Nominal: valid region on noisy image passes filters."""
        regions = [
            {"bbox": [[10, 20], [100, 20], [100, 50], [10, 50]], "confidence": 0.85},
        ]
        result = filter_small_regions(regions, min_area=100)
        result = filter_by_aspect_ratio(result, min_ratio=0.1, max_ratio=10.0)

        assert len(result) == 1

    def test_detect_text_regions_with_detections_on_low_contrast(self):
        """Nominal: detect_text_regions filters properly on low-contrast image."""
        img = _make_low_contrast_image()
        detector = _mock_detector_with_results()

        result = detect_text_regions(img, detector=detector)

        assert isinstance(result, list)
        assert len(result) >= 1
        for r in result:
            assert "bbox" in r
            assert "confidence" in r

    def test_detect_text_regions_with_detections_on_noisy_image(self):
        """Nominal: detect_text_regions filters properly on noisy image."""
        img = _make_noisy_image()
        detector = _mock_detector_with_results()

        result = detect_text_regions(img, detector=detector)

        assert isinstance(result, list)
        assert len(result) >= 1


# ---------------------------------------------------------------------------
# Tests — enhance_for_difficult_text preprocessing
# ---------------------------------------------------------------------------

class TestEnhanceForDifficultText:
    """Tests for the enhance_for_difficult_text preprocessing function."""

    def test_returns_valid_image(self):
        """Nominal: returns a valid BGR uint8 image."""
        img = _make_low_contrast_image()

        result = enhance_for_difficult_text(img)

        assert isinstance(result, np.ndarray)
        assert result.ndim == 3
        assert result.dtype == np.uint8

    def test_does_not_modify_input(self):
        """§R4: input image must not be modified in place."""
        img = _make_low_contrast_image()
        original = img.copy()

        enhance_for_difficult_text(img)

        np.testing.assert_array_equal(img, original)

    def test_preserves_dimensions(self):
        """Nominal: output has same dimensions as input."""
        img = _make_small_text_image(150, 250)

        result = enhance_for_difficult_text(img)

        assert result.shape == img.shape

    def test_none_raises_valueerror(self):
        """Error: None image raises ValueError."""
        with pytest.raises(ValueError, match="None"):
            enhance_for_difficult_text(None)

    def test_2d_image_raises_valueerror(self):
        """Error: grayscale 2D image raises ValueError."""
        img = np.zeros((100, 100), dtype=np.uint8)
        with pytest.raises(ValueError, match="3-dimensional"):
            enhance_for_difficult_text(img)

    def test_float_image_raises_valueerror(self):
        """Error: float dtype raises ValueError."""
        img = np.zeros((100, 100, 3), dtype=np.float64)
        with pytest.raises(ValueError, match="uint8"):
            enhance_for_difficult_text(img)

    def test_low_contrast_image_enhanced(self):
        """Nominal: low-contrast image has higher contrast after enhancement."""
        img = _make_low_contrast_image()
        result = enhance_for_difficult_text(img)

        # The enhanced image should have a wider intensity range
        gray_before = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_after = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        range_before = int(gray_before.max()) - int(gray_before.min())
        range_after = int(gray_after.max()) - int(gray_after.min())

        assert range_after >= range_before

    def test_small_text_image_sharpened(self):
        """Nominal: small-text image is sharpened (Laplacian variance increases)."""
        img = _make_small_text_image()
        result = enhance_for_difficult_text(img)

        gray_before = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_after = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        lap_before = cv2.Laplacian(gray_before, cv2.CV_64F).var()
        lap_after = cv2.Laplacian(gray_after, cv2.CV_64F).var()

        assert lap_after >= lap_before

    def test_narrow_spine_no_crash(self):
        """Robustness: narrow spine image does not crash enhancement."""
        img = _make_narrow_spine_image()

        result = enhance_for_difficult_text(img)

        assert result.shape == img.shape

    def test_noisy_image_no_crash(self):
        """Robustness: noisy image does not crash enhancement."""
        img = _make_noisy_image()

        result = enhance_for_difficult_text(img)

        assert result.shape == img.shape

    def test_uniform_image_no_crash(self):
        """Robustness: uniform image does not crash enhancement."""
        img = _make_uniform_image()

        result = enhance_for_difficult_text(img)

        assert result.shape == img.shape

    def test_clahe_still_works_after_enhancement(self):
        """Integration: apply_clahe works on enhanced output."""
        img = _make_low_contrast_image()
        enhanced = enhance_for_difficult_text(img)

        result = apply_clahe(enhanced)

        assert isinstance(result, np.ndarray)
        assert result.ndim == 3
        assert result.dtype == np.uint8
