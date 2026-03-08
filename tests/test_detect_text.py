"""Tests for the text detection module (PaddleOCR / CRAFT)."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.detect_text import (
    DEFAULT_DET_CONFIDENCE,
    correct_orientation,
    detect_text_on_spines,
    detect_text_regions,
    estimate_text_angle,
    filter_by_aspect_ratio,
    filter_small_regions,
    group_text_lines,
    init_detector,
    rotate_image,
)


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

    def test_init_detector_craft_raises(self):
        """Error: ValueError for craft model (not implemented)."""
        with pytest.raises(ValueError, match="Only 'paddleocr' is currently available"):
            init_detector("craft")


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
        """Nominal: the detector.ocr method is called with image content."""
        img = _make_image()
        detector = _mock_detector_with_results()

        detect_text_regions(img, detector=detector)

        detector.ocr.assert_called_once()
        call_args = detector.ocr.call_args
        passed_image = call_args[0][0]
        # A defensive copy is made, so the object differs but content matches.
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

    def test_2d_image_raises_valueerror(self):
        """Error: ValueError when image is 2-dimensional (grayscale)."""
        img = np.zeros((100, 100), dtype=np.uint8)
        with pytest.raises(ValueError, match="3-dimensional"):
            detect_text_regions(img)

    def test_4d_image_raises_valueerror(self):
        """Error: ValueError when image is 4-dimensional."""
        img = np.zeros((1, 100, 100, 3), dtype=np.uint8)
        with pytest.raises(ValueError, match="3-dimensional"):
            detect_text_regions(img)

    def test_float_image_raises_valueerror(self):
        """Error: ValueError when image dtype is float64 instead of uint8."""
        img = np.zeros((100, 100, 3), dtype=np.float64)
        with pytest.raises(ValueError, match="uint8"):
            detect_text_regions(img)

    def test_float32_image_raises_valueerror(self):
        """Error: ValueError when image dtype is float32 instead of uint8."""
        img = np.zeros((100, 100, 3), dtype=np.float32)
        with pytest.raises(ValueError, match="uint8"):
            detect_text_regions(img)


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

    def test_original_image_not_modified(self):
        """Edge: the original image array is not modified by detect_text_regions."""
        img = _make_image()
        original = img.copy()
        detector = _mock_detector_with_results()

        detect_text_regions(img, detector=detector)

        np.testing.assert_array_equal(img, original)

    def test_default_det_confidence_used_when_no_score(self):
        """Edge: DEFAULT_DET_CONFIDENCE is used when detection has no score."""
        detector = MagicMock()
        # Simulate det-only output: bbox without confidence score
        detector.ocr.return_value = [
            [
                [[[10.0, 20.0], [100.0, 20.0], [100.0, 50.0], [10.0, 50.0]]],
            ]
        ]
        img = _make_image()

        result = detect_text_regions(img, detector=detector)

        assert len(result) == 1
        assert result[0]["confidence"] == DEFAULT_DET_CONFIDENCE


# ---------------------------------------------------------------------------
# Tests — group_text_lines (Task 011)
# ---------------------------------------------------------------------------

class TestGroupTextLines:
    """Tests for group_text_lines function."""

    def test_groups_nearby_regions(self):
        """Nominal: regions on the same vertical line are grouped together."""
        # Two regions at similar y positions (vertical center ~35)
        regions = [
            {"bbox": [[10, 20], [100, 20], [100, 50], [10, 50]], "confidence": 0.9},
            {"bbox": [[120, 22], [200, 22], [200, 48], [120, 48]], "confidence": 0.8},
        ]
        groups = group_text_lines(regions, line_threshold=0.5)

        assert isinstance(groups, list)
        assert len(groups) == 1  # Both in same group
        assert len(groups[0]) == 2

    def test_isolated_regions_own_group(self):
        """Nominal: regions far apart vertically get their own group."""
        regions = [
            {"bbox": [[10, 10], [100, 10], [100, 30], [10, 30]], "confidence": 0.9},
            {"bbox": [[10, 200], [100, 200], [100, 220], [10, 220]], "confidence": 0.8},
        ]
        groups = group_text_lines(regions, line_threshold=0.5)

        assert len(groups) == 2
        assert len(groups[0]) == 1
        assert len(groups[1]) == 1

    def test_empty_list(self):
        """Edge: empty regions list returns empty groups list."""
        groups = group_text_lines([])

        assert groups == []


# ---------------------------------------------------------------------------
# Tests — detect_text_on_spines (Task 011)
# ---------------------------------------------------------------------------

class TestDetectTextOnSpines:
    """Tests for detect_text_on_spines function."""

    @patch("src.detect_text.detect_text_regions")
    def test_returns_list_per_crop(self, mock_detect):
        """Nominal: returns one result list per crop."""
        mock_detect.return_value = [
            {"bbox": [[10, 20], [100, 20], [100, 50], [10, 50]], "confidence": 0.9}
        ]
        crops = [_make_image(50, 30), _make_image(60, 25)]

        result = detect_text_on_spines(crops, engine="paddleocr")

        assert isinstance(result, list)
        assert len(result) == 2
        for item in result:
            assert isinstance(item, list)

    @patch("src.detect_text.detect_text_regions")
    def test_empty_crops_list(self, mock_detect):
        """Edge: empty crops list returns empty result list."""
        result = detect_text_on_spines([], engine="paddleocr")

        assert result == []
        mock_detect.assert_not_called()

    def test_none_raises_valueerror(self):
        """Error: None crops raises ValueError."""
        with pytest.raises(ValueError):
            detect_text_on_spines(None)


# ---------------------------------------------------------------------------
# Tests — estimate_text_angle (Task 012)
# ---------------------------------------------------------------------------

class TestEstimateTextAngle:
    """Tests for estimate_text_angle function."""

    def test_horizontal_text_near_zero(self):
        """Nominal: horizontal bboxes yield angle ~0 degrees."""
        bboxes = [
            {"bbox": [[10, 20], [100, 20], [100, 40], [10, 40]], "confidence": 0.9},
            {"bbox": [[10, 60], [100, 60], [100, 80], [10, 80]], "confidence": 0.8},
        ]
        angle = estimate_text_angle(bboxes)

        assert abs(angle) < 5.0

    def test_vertical_text_near_90(self):
        """Nominal: vertical bboxes yield angle ~90 degrees."""
        # Vertical text: top-left at top, top-right goes down
        bboxes = [
            {"bbox": [[20, 10], [20, 100], [40, 100], [40, 10]], "confidence": 0.9},
        ]
        angle = estimate_text_angle(bboxes)

        assert abs(abs(angle) - 90.0) < 10.0

    def test_empty_bboxes_returns_zero(self):
        """Edge: empty list returns 0.0."""
        angle = estimate_text_angle([])

        assert angle == 0.0


# ---------------------------------------------------------------------------
# Tests — rotate_image (Task 012)
# ---------------------------------------------------------------------------

class TestRotateImage:
    """Tests for rotate_image function."""

    def test_rotation_preserves_content(self):
        """Nominal: rotated image dimensions are adjusted to not clip content."""
        img = _make_image(100, 200)
        rotated = rotate_image(img, 45.0)

        # After 45-degree rotation with adjusted dimensions, the image should
        # be larger than the original to avoid clipping
        assert rotated.shape[0] >= img.shape[0]
        assert rotated.shape[1] >= img.shape[1]
        assert rotated.ndim == 3

    def test_zero_rotation_same_size(self):
        """Edge: 0-degree rotation returns image of same size."""
        img = _make_image(100, 200)
        rotated = rotate_image(img, 0.0)

        assert rotated.shape == img.shape

    def test_none_raises_valueerror(self):
        """Error: None image raises ValueError."""
        with pytest.raises(ValueError):
            rotate_image(None, 10.0)


# ---------------------------------------------------------------------------
# Tests — correct_orientation (Task 012)
# ---------------------------------------------------------------------------

class TestCorrectOrientation:
    """Tests for correct_orientation function."""

    def test_no_rotation_below_threshold(self):
        """Nominal: no rotation when angle < threshold."""
        img = _make_image(100, 200)
        # Horizontal bboxes => angle ~0
        bboxes = [
            {"bbox": [[10, 20], [100, 20], [100, 40], [10, 40]], "confidence": 0.9},
        ]

        result = correct_orientation(img, bboxes, angle_threshold=2.0)

        # Should return same-sized image (no rotation applied)
        assert result.shape == img.shape
        np.testing.assert_array_equal(result, img)

    def test_rotation_applied_when_needed(self):
        """Nominal: rotation applied when angle > threshold."""
        img = _make_image(100, 200)
        # Vertical bboxes => angle ~90
        bboxes = [
            {"bbox": [[20, 10], [20, 100], [40, 100], [40, 10]], "confidence": 0.9},
        ]

        result = correct_orientation(img, bboxes, angle_threshold=2.0)

        # Image should be rotated, so dimensions likely differ
        assert result is not None
        assert isinstance(result, np.ndarray)
        # After rotating ~90 degrees, width and height should be swapped approximately
        assert result.shape[0] != img.shape[0] or result.shape[1] != img.shape[1]

    def test_none_raises_valueerror(self):
        """Error: None image raises ValueError."""
        with pytest.raises(ValueError):
            correct_orientation(None, [])


# ---------------------------------------------------------------------------
# Tests — filter_small_regions (Task 021)
# ---------------------------------------------------------------------------

class TestFilterSmallRegions:
    """Tests for filter_small_regions function."""

    def test_keeps_large_regions(self):
        """Nominal: regions with area >= min_area are kept."""
        # 90 x 30 = 2700 area
        regions = [
            {"bbox": [[10, 20], [100, 20], [100, 50], [10, 50]], "confidence": 0.9},
        ]
        result = filter_small_regions(regions, min_area=100)

        assert len(result) == 1

    def test_removes_small_regions(self):
        """Nominal: regions with area < min_area are removed."""
        # 5 x 5 = 25 area
        regions = [
            {"bbox": [[10, 10], [15, 10], [15, 15], [10, 15]], "confidence": 0.9},
        ]
        result = filter_small_regions(regions, min_area=100)

        assert len(result) == 0

    def test_mixed_sizes(self):
        """Nominal: only large regions survive filtering."""
        regions = [
            {"bbox": [[10, 20], [100, 20], [100, 50], [10, 50]], "confidence": 0.9},
            {"bbox": [[10, 10], [15, 10], [15, 15], [10, 15]], "confidence": 0.8},
        ]
        result = filter_small_regions(regions, min_area=100)

        assert len(result) == 1
        assert result[0]["confidence"] == pytest.approx(0.9)

    def test_empty_list(self):
        """Edge: empty input returns empty output."""
        result = filter_small_regions([], min_area=100)

        assert result == []

    def test_exact_threshold(self):
        """Edge: region with area exactly equal to min_area is kept."""
        # 10 x 10 = 100 area
        regions = [
            {"bbox": [[0, 0], [10, 0], [10, 10], [0, 10]], "confidence": 0.9},
        ]
        result = filter_small_regions(regions, min_area=100)

        assert len(result) == 1

    def test_non_rectangular_bbox(self):
        """Nominal: area computed via Shoelace for non-rectangular polygons."""
        # Parallelogram: vertices (0,0), (10,5), (10,15), (0,10)
        # Shoelace area = 100
        regions = [
            {"bbox": [[0, 0], [10, 5], [10, 15], [0, 10]], "confidence": 0.9},
        ]
        result = filter_small_regions(regions, min_area=101)

        assert len(result) == 0


# ---------------------------------------------------------------------------
# Tests — filter_by_aspect_ratio (Task 021)
# ---------------------------------------------------------------------------

class TestFilterByAspectRatio:
    """Tests for filter_by_aspect_ratio function."""

    def test_keeps_normal_ratio(self):
        """Nominal: regions with normal aspect ratio are kept."""
        # 90 wide x 30 tall → ratio = 3.0
        regions = [
            {"bbox": [[10, 20], [100, 20], [100, 50], [10, 50]], "confidence": 0.9},
        ]
        result = filter_by_aspect_ratio(regions, min_ratio=0.1, max_ratio=10.0)

        assert len(result) == 1

    def test_removes_too_wide(self):
        """Nominal: region with extreme width-to-height ratio is removed."""
        # 200 wide x 2 tall → ratio = 100.0
        regions = [
            {"bbox": [[0, 0], [200, 0], [200, 2], [0, 2]], "confidence": 0.9},
        ]
        result = filter_by_aspect_ratio(regions, min_ratio=0.1, max_ratio=10.0)

        assert len(result) == 0

    def test_removes_too_narrow(self):
        """Nominal: region with extreme height-to-width ratio is removed."""
        # 2 wide x 200 tall → ratio = 0.01
        regions = [
            {"bbox": [[0, 0], [2, 0], [2, 200], [0, 200]], "confidence": 0.9},
        ]
        result = filter_by_aspect_ratio(regions, min_ratio=0.1, max_ratio=10.0)

        assert len(result) == 0

    def test_empty_list(self):
        """Edge: empty input returns empty output."""
        result = filter_by_aspect_ratio([], min_ratio=0.1, max_ratio=10.0)

        assert result == []

    def test_square_region_kept(self):
        """Edge: square region (ratio=1.0) is kept."""
        regions = [
            {"bbox": [[0, 0], [50, 0], [50, 50], [0, 50]], "confidence": 0.9},
        ]
        result = filter_by_aspect_ratio(regions, min_ratio=0.1, max_ratio=10.0)

        assert len(result) == 1

    def test_exact_min_ratio_kept(self):
        """Edge: region with ratio exactly at min_ratio is kept."""
        # 10 wide x 100 tall → ratio = 0.1
        regions = [
            {"bbox": [[0, 0], [10, 0], [10, 100], [0, 100]], "confidence": 0.9},
        ]
        result = filter_by_aspect_ratio(regions, min_ratio=0.1, max_ratio=10.0)

        assert len(result) == 1

    def test_exact_max_ratio_kept(self):
        """Edge: region with ratio exactly at max_ratio is kept."""
        # 100 wide x 10 tall → ratio = 10.0
        regions = [
            {"bbox": [[0, 0], [100, 0], [100, 10], [0, 10]], "confidence": 0.9},
        ]
        result = filter_by_aspect_ratio(regions, min_ratio=0.1, max_ratio=10.0)

        assert len(result) == 1


# ---------------------------------------------------------------------------
# Tests — confidence_threshold in detect_text_regions (Task 021)
# ---------------------------------------------------------------------------

class TestDetectTextRegionsConfidenceThreshold:
    """Tests for confidence_threshold parameter in detect_text_regions."""

    def test_default_threshold_filters_low_confidence(self):
        """Nominal: default threshold (0.5) filters out low-confidence detections."""
        detector = MagicMock()
        detector.ocr.return_value = [
            [
                [[[10, 20], [100, 20], [100, 50], [10, 50]], 0.95],
                [[[150, 60], [250, 60], [250, 90], [150, 90]], 0.3],
            ]
        ]
        img = _make_image()

        result = detect_text_regions(img, detector=detector)

        assert len(result) == 1
        assert result[0]["confidence"] == pytest.approx(0.95)

    def test_custom_threshold(self):
        """Nominal: custom confidence_threshold filters accordingly."""
        detector = MagicMock()
        detector.ocr.return_value = [
            [
                [[[10, 20], [100, 20], [100, 50], [10, 50]], 0.95],
                [[[150, 60], [250, 60], [250, 90], [150, 90]], 0.82],
                [[[10, 100], [80, 100], [80, 130], [10, 130]], 0.60],
            ]
        ]
        img = _make_image()

        result = detect_text_regions(img, detector=detector, confidence_threshold=0.8)

        assert len(result) == 2

    def test_zero_threshold_keeps_all(self):
        """Edge: confidence_threshold=0.0 keeps all detections."""
        detector = MagicMock()
        detector.ocr.return_value = [
            [
                [[[10, 20], [100, 20], [100, 50], [10, 50]], 0.01],
                [[[150, 60], [250, 60], [250, 90], [150, 90]], 0.99],
            ]
        ]
        img = _make_image()

        result = detect_text_regions(img, detector=detector, confidence_threshold=0.0)

        assert len(result) == 2

    def test_high_threshold_filters_most(self):
        """Edge: very high threshold filters most detections."""
        detector = MagicMock()
        detector.ocr.return_value = [
            [
                [[[10, 20], [100, 20], [100, 50], [10, 50]], 0.95],
                [[[150, 60], [250, 60], [250, 90], [150, 90]], 0.82],
            ]
        ]
        img = _make_image()

        result = detect_text_regions(img, detector=detector, confidence_threshold=0.99)

        assert len(result) == 0


# ---------------------------------------------------------------------------
# Tests — integrated filtering in detect_text_regions (Task 021)
# ---------------------------------------------------------------------------

class TestDetectTextRegionsIntegratedFiltering:
    """Tests for integrated size and aspect ratio filtering in detect_text_regions."""

    def test_small_regions_filtered_by_default(self):
        """Nominal: very small detected regions are filtered out."""
        detector = MagicMock()
        detector.ocr.return_value = [
            [
                # Large region: 90x30 = 2700 area
                [[[10, 20], [100, 20], [100, 50], [10, 50]], 0.95],
                # Tiny region: 3x3 = 9 area
                [[[10, 10], [13, 10], [13, 13], [10, 13]], 0.95],
            ]
        ]
        img = _make_image()

        result = detect_text_regions(img, detector=detector)

        assert len(result) == 1

    def test_aberrant_aspect_ratio_filtered(self):
        """Nominal: regions with extreme aspect ratio are filtered out."""
        detector = MagicMock()
        detector.ocr.return_value = [
            [
                # Normal region: 90x30 → ratio 3.0
                [[[10, 20], [100, 20], [100, 50], [10, 50]], 0.95],
                # Extreme ratio: 200x1 → ratio 200.0
                [[[0, 0], [200, 0], [200, 1], [0, 1]], 0.95],
            ]
        ]
        img = _make_image()

        result = detect_text_regions(img, detector=detector)

        assert len(result) == 1
