"""Tests for the text detection module (PaddleOCR / CRAFT)."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.detect_text import detect_text_regions, init_detector


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_image(height: int = 200, width: int = 300, channels: int = 3) -> np.ndarray:
    """Create a synthetic BGR test image."""
    rng = np.random.default_rng(42)
    return rng.integers(0, 256, (height, width, channels), dtype=np.uint8)


def _mock_detector_with_results() -> MagicMock:
    """Return a mock detector that produces realistic PaddleOCR detections."""
    detector = MagicMock()
    # PaddleOCR det-only format: [[bbox, confidence], ...]
    detector.ocr.return_value = [
        [
            [[[10.0, 20.0], [100.0, 20.0], [100.0, 50.0], [10.0, 50.0]], 0.95],
            [[[150.0, 60.0], [250.0, 60.0], [250.0, 90.0], [150.0, 90.0]], 0.82],
        ]
    ]
    return detector


def _mock_detector_no_results() -> MagicMock:
    """Return a mock detector that finds no text."""
    detector = MagicMock()
    detector.ocr.return_value = [None]
    return detector


# ---------------------------------------------------------------------------
# Tests — init_detector
# ---------------------------------------------------------------------------

class TestInitDetector:
    """Tests for init_detector function."""

    def test_init_detector_returns_object(self):
        """Nominal: init_detector returns a functional detector object."""
        mock_paddle_cls = MagicMock()
        mock_module = MagicMock()
        mock_module.PaddleOCR = mock_paddle_cls
        with patch.dict("sys.modules", {"paddleocr": mock_module}):
            detector = init_detector("paddleocr")

        assert detector is not None
        mock_paddle_cls.assert_called_once()

    def test_init_detector_unsupported_model_raises(self):
        """Error: ValueError for unsupported model name."""
        with pytest.raises(ValueError, match="Unsupported model"):
            init_detector("unknown_model")


# ---------------------------------------------------------------------------
# Tests — detect_text_regions output format
# ---------------------------------------------------------------------------

class TestDetectTextRegionsFormat:
    """Tests for detect_text_regions output structure."""

    def test_returns_list(self):
        """Nominal: detect_text_regions returns a list."""
        img = _make_image()
        detector = _mock_detector_with_results()

        result = detect_text_regions(img, detector=detector)

        assert isinstance(result, list)

    def test_each_element_is_dict_with_bbox_and_confidence(self):
        """Nominal: each element has keys 'bbox' and 'confidence'."""
        img = _make_image()
        detector = _mock_detector_with_results()

        result = detect_text_regions(img, detector=detector)

        for region in result:
            assert isinstance(region, dict)
            assert "bbox" in region
            assert "confidence" in region

    def test_bbox_has_four_points(self):
        """Nominal: each bbox contains exactly 4 points (polygon)."""
        img = _make_image()
        detector = _mock_detector_with_results()

        result = detect_text_regions(img, detector=detector)

        for region in result:
            bbox = region["bbox"]
            assert len(bbox) == 4, f"Expected 4 points, got {len(bbox)}"

    def test_bbox_points_are_numeric(self):
        """Nominal: bbox point coordinates are numeric (float)."""
        img = _make_image()
        detector = _mock_detector_with_results()

        result = detect_text_regions(img, detector=detector)

        for region in result:
            for point in region["bbox"]:
                assert len(point) == 2
                assert isinstance(point[0], float)
                assert isinstance(point[1], float)

    def test_confidence_is_float_between_0_and_1(self):
        """Nominal: confidence is a float in [0, 1]."""
        img = _make_image()
        detector = _mock_detector_with_results()

        result = detect_text_regions(img, detector=detector)

        for region in result:
            conf = region["confidence"]
            assert isinstance(conf, float)
            assert 0.0 <= conf <= 1.0


# ---------------------------------------------------------------------------
# Tests — detection behaviour
# ---------------------------------------------------------------------------

class TestDetectTextRegionsBehaviour:
    """Tests for detect_text_regions detection logic."""

    def test_image_with_text_returns_regions(self):
        """Nominal: at least one region detected on image with text (mocked)."""
        img = _make_image()
        detector = _mock_detector_with_results()

        result = detect_text_regions(img, detector=detector)

        assert len(result) >= 1

    def test_image_without_text_returns_empty_list(self):
        """Edge: detector finds no text → empty list returned."""
        img = _make_image()
        detector = _mock_detector_no_results()

        result = detect_text_regions(img, detector=detector)

        assert result == []

    def test_detector_ocr_called_with_image(self):
        """Nominal: the detector.ocr method is called with the image."""
        img = _make_image()
        detector = _mock_detector_with_results()

        detect_text_regions(img, detector=detector)

        detector.ocr.assert_called_once()
        call_args = detector.ocr.call_args
        passed_image = call_args[0][0]
        np.testing.assert_array_equal(passed_image, img)


# ---------------------------------------------------------------------------
# Tests — input validation
# ---------------------------------------------------------------------------

class TestDetectTextRegionsValidation:
    """Tests for input validation in detect_text_regions."""

    def test_none_image_raises_valueerror(self):
        """Error: ValueError when image is None."""
        with pytest.raises(ValueError, match="None"):
            detect_text_regions(None)

    def test_empty_image_raises_valueerror(self):
        """Error: ValueError when image is empty array."""
        with pytest.raises(ValueError, match="empty"):
            detect_text_regions(np.array([]))

    def test_non_array_image_raises_valueerror(self):
        """Error: ValueError when image is not a numpy array."""
        with pytest.raises(ValueError, match="numpy array"):
            detect_text_regions("not_an_image")


# ---------------------------------------------------------------------------
# Tests — edge cases
# ---------------------------------------------------------------------------

class TestDetectTextRegionsEdgeCases:
    """Tests for edge-case inputs."""

    def test_very_small_image(self):
        """Edge: very small image (1x1) does not crash."""
        img = np.zeros((1, 1, 3), dtype=np.uint8)
        detector = _mock_detector_no_results()

        result = detect_text_regions(img, detector=detector)

        assert isinstance(result, list)

    def test_grayscale_like_image_3channel(self):
        """Edge: grayscale-valued but 3-channel image works normally."""
        img = np.full((50, 50, 3), 128, dtype=np.uint8)
        detector = _mock_detector_with_results()

        result = detect_text_regions(img, detector=detector)

        assert isinstance(result, list)
        assert len(result) >= 1
