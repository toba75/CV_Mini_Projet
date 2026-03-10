"""Tests for the image preprocessing module (CLAHE pipeline)."""

import cv2
import numpy as np
import pytest

from src.preprocess import (
    apply_clahe,
    correct_perspective,
    detect_shelf_contour,
    load_image,
    preprocess,
    resize_image,
)


class TestLoadImage:
    """Tests for load_image function."""

    def test_load_existing_image(self, tmp_path):
        """Nominal: load_image returns a valid BGR numpy array."""
        img = np.zeros((100, 150, 3), dtype=np.uint8)
        img[20:80, 30:120] = (128, 64, 200)
        path = tmp_path / "test_img.png"
        cv2.imwrite(str(path), img)

        result = load_image(str(path))

        assert isinstance(result, np.ndarray)
        assert result.ndim == 3
        assert result.shape == (100, 150, 3)
        np.testing.assert_array_equal(result, img)

    def test_load_image_file_not_found(self):
        """Error: FileNotFoundError when file does not exist."""
        with pytest.raises(FileNotFoundError):
            load_image("nonexistent_path/fake_image.png")

    def test_load_image_none_path(self):
        """Error: ValueError when path is None."""
        with pytest.raises((ValueError, TypeError)):
            load_image(None)

    def test_load_image_empty_path(self):
        """Error: ValueError or FileNotFoundError when path is empty string."""
        with pytest.raises((ValueError, FileNotFoundError)):
            load_image("")


class TestResizeImage:
    """Tests for resize_image function."""

    def test_resize_larger_image(self):
        """Nominal: image wider than max_width is resized with aspect ratio."""
        img = np.zeros((1000, 3000, 3), dtype=np.uint8)
        result = resize_image(img, max_width=1500)

        assert result.shape[1] == 1500
        expected_height = int(1000 * (1500 / 3000))
        assert result.shape[0] == expected_height
        assert result.shape[2] == 3

    def test_resize_preserves_aspect_ratio(self):
        """Nominal: aspect ratio is preserved after resize."""
        img = np.zeros((800, 2400, 3), dtype=np.uint8)
        original_ratio = img.shape[1] / img.shape[0]
        result = resize_image(img, max_width=1200)

        result_ratio = result.shape[1] / result.shape[0]
        assert pytest.approx(original_ratio, rel=0.01) == result_ratio

    def test_resize_smaller_image_unchanged(self):
        """Edge: image already smaller than max_width is not modified."""
        img = np.random.default_rng(42).integers(0, 256, (200, 300, 3), dtype=np.uint8)
        result = resize_image(img, max_width=1920)

        np.testing.assert_array_equal(result, img)

    def test_resize_image_none_raises(self):
        """Error: ValueError when image is None."""
        with pytest.raises(ValueError):
            resize_image(None)

    def test_resize_image_empty_raises(self):
        """Error: ValueError when image is empty."""
        with pytest.raises(ValueError):
            resize_image(np.array([]))

    def test_resize_image_wrong_ndim_raises(self):
        """Error: ValueError when image has wrong number of dimensions."""
        img_2d = np.zeros((100, 150), dtype=np.uint8)
        with pytest.raises(ValueError, match="3-dimensional"):
            resize_image(img_2d)

    def test_resize_image_wrong_dtype_raises(self):
        """Error: ValueError when image dtype is not uint8."""
        img_float = np.zeros((100, 150, 3), dtype=np.float32)
        with pytest.raises(ValueError, match="uint8"):
            resize_image(img_float)


class TestApplyClahe:
    """Tests for apply_clahe function."""

    def test_clahe_preserves_dimensions(self):
        """Nominal: output has same dimensions as input."""
        img = np.random.default_rng(42).integers(0, 256, (200, 300, 3), dtype=np.uint8)
        result = apply_clahe(img)

        assert result.shape == img.shape
        assert result.dtype == img.dtype

    def test_clahe_improves_contrast(self):
        """Nominal: CLAHE improves or maintains contrast (std dev)."""
        # Create a low-contrast image
        img = np.full((200, 300, 3), 120, dtype=np.uint8)
        img[50:150, 50:250] = 130  # slight variation

        result = apply_clahe(img)

        # Convert both to grayscale for comparison
        gray_orig = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

        std_orig = np.std(gray_orig.astype(np.float64))
        std_result = np.std(gray_result.astype(np.float64))

        assert std_result >= std_orig

    def test_clahe_does_not_modify_input(self):
        """Nominal: input image is not modified in place."""
        img = np.random.default_rng(42).integers(0, 256, (100, 150, 3), dtype=np.uint8)
        original = img.copy()
        apply_clahe(img)

        np.testing.assert_array_equal(img, original)

    def test_clahe_none_raises(self):
        """Error: ValueError when image is None."""
        with pytest.raises(ValueError):
            apply_clahe(None)

    def test_clahe_empty_raises(self):
        """Error: ValueError when image is empty."""
        with pytest.raises(ValueError):
            apply_clahe(np.array([]))

    def test_clahe_wrong_ndim_raises(self):
        """Error: ValueError when image has wrong number of dimensions."""
        img_2d = np.zeros((100, 150), dtype=np.uint8)
        with pytest.raises(ValueError, match="3-dimensional"):
            apply_clahe(img_2d)

    def test_clahe_wrong_dtype_raises(self):
        """Error: ValueError when image dtype is not uint8."""
        img_float = np.zeros((100, 150, 3), dtype=np.float32)
        with pytest.raises(ValueError, match="uint8"):
            apply_clahe(img_float)


class TestPreprocess:
    """Tests for preprocess orchestration function."""

    def test_preprocess_nominal(self, tmp_path):
        """Nominal: preprocess chains load, resize, and CLAHE correctly."""
        img = np.random.default_rng(42).integers(0, 256, (600, 2400, 3), dtype=np.uint8)
        path = tmp_path / "shelf.jpg"
        cv2.imwrite(str(path), img)

        result = preprocess(str(path))

        assert isinstance(result, np.ndarray)
        assert result.ndim == 3
        assert result.shape[2] == 3
        # Width should be capped at 1920
        assert result.shape[1] <= 1920

    def test_preprocess_small_image(self, tmp_path):
        """Nominal: preprocess works on image smaller than max_width."""
        img = np.random.default_rng(42).integers(0, 256, (200, 300, 3), dtype=np.uint8)
        path = tmp_path / "small.png"
        cv2.imwrite(str(path), img)

        result = preprocess(str(path))

        assert isinstance(result, np.ndarray)
        assert result.shape[1] == 300  # unchanged width

    def test_preprocess_file_not_found(self):
        """Error: FileNotFoundError propagated from load_image."""
        with pytest.raises(FileNotFoundError):
            preprocess("does_not_exist.png")


# ---------------------------------------------------------------------------
# Helper: create a synthetic warped quadrilateral image
# ---------------------------------------------------------------------------

def _make_synthetic_quad_image(
    width: int = 400,
    height: int = 400,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (image, corners) where *image* contains a bright filled
    quadrilateral on a black background.  *corners* are the 4 vertices in
    order: top-left, top-right, bottom-right, bottom-left.
    """
    img = np.zeros((height, width, 3), dtype=np.uint8)
    # Define a quadrilateral (slightly trapezoidal)
    tl = [80, 60]
    tr = [320, 70]
    br = [340, 340]
    bl = [60, 330]
    corners = np.array([tl, tr, br, bl], dtype=np.float32)
    pts = corners.astype(np.int32).reshape((-1, 1, 2))
    cv2.fillPoly(img, [pts], color=(255, 255, 255))
    return img, corners


class TestDetectShelfContour:
    """Tests for detect_shelf_contour function."""

    def test_returns_four_points_on_quad_image(self):
        """Nominal: returns array of shape (4, 2) for image with clear quad."""
        img, _ = _make_synthetic_quad_image()
        result = detect_shelf_contour(img)

        assert result is not None
        assert isinstance(result, np.ndarray)
        assert result.shape == (4, 2)

    def test_returns_none_on_uniform_image(self):
        """Edge: returns None when no contour is detectable."""
        img = np.full((300, 400, 3), 128, dtype=np.uint8)
        result = detect_shelf_contour(img)

        assert result is None

    def test_none_image_raises(self):
        """Error: ValueError when image is None."""
        with pytest.raises(ValueError):
            detect_shelf_contour(None)

    def test_empty_image_raises(self):
        """Error: ValueError when image is empty."""
        with pytest.raises(ValueError):
            detect_shelf_contour(np.array([]))

    def test_wrong_ndim_raises(self):
        """Error: ValueError when image is 2D."""
        with pytest.raises(ValueError, match="3-dimensional"):
            detect_shelf_contour(np.zeros((100, 100), dtype=np.uint8))

    def test_wrong_dtype_raises(self):
        """Error: ValueError when image dtype is not uint8."""
        with pytest.raises(ValueError, match="uint8"):
            detect_shelf_contour(np.zeros((100, 100, 3), dtype=np.float32))


class TestCorrectPerspective:
    """Tests for correct_perspective function."""

    def test_corrects_known_warp(self):
        """Nominal: correct_perspective straightens a synthetically warped image.

        Creates a known rectangle, applies a perspective warp to distort it,
        then verifies that correct_perspective (given the warped corners)
        produces an image with reasonable dimensions.
        """
        # Create a clean rectangle image
        src_img = np.zeros((300, 400, 3), dtype=np.uint8)
        src_img[50:250, 50:350] = (200, 180, 160)

        # Define source rectangle corners and destination (warped) corners
        src_pts = np.array(
            [[50, 50], [350, 50], [350, 250], [50, 250]], dtype=np.float32
        )
        dst_pts = np.array(
            [[70, 80], [330, 60], [360, 270], [40, 260]], dtype=np.float32
        )

        # Warp the image to simulate perspective distortion
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped = cv2.warpPerspective(src_img, M, (400, 300))

        # Now correct_perspective should straighten using the warped corners
        result = correct_perspective(warped, corners=dst_pts)

        assert isinstance(result, np.ndarray)
        assert result.ndim == 3
        assert result.shape[0] > 0 and result.shape[1] > 0

    def test_returns_original_when_no_contour(self):
        """Edge: returns original image unchanged when no corners and no
        detectable contour.
        """
        img = np.full((200, 300, 3), 128, dtype=np.uint8)
        result = correct_perspective(img, corners=None)

        np.testing.assert_array_equal(result, img)

    def test_output_dimensions_reasonable(self):
        """Nominal: output image has non-zero width and height."""
        img, corners = _make_synthetic_quad_image()
        result = correct_perspective(img, corners=corners)

        assert result.shape[0] > 0
        assert result.shape[1] > 0
        assert result.ndim == 3

    def test_does_not_modify_input(self):
        """Nominal: input image is not modified in place."""
        img, corners = _make_synthetic_quad_image()
        original = img.copy()
        correct_perspective(img, corners=corners)

        np.testing.assert_array_equal(img, original)

    def test_none_image_raises(self):
        """Error: ValueError when image is None."""
        with pytest.raises(ValueError):
            correct_perspective(None)

    def test_empty_image_raises(self):
        """Error: ValueError when image is empty."""
        with pytest.raises(ValueError):
            correct_perspective(np.array([]))

    def test_wrong_ndim_raises(self):
        """Error: ValueError when image is 2D."""
        with pytest.raises(ValueError, match="3-dimensional"):
            correct_perspective(np.zeros((100, 100), dtype=np.uint8))

    def test_wrong_dtype_raises(self):
        """Error: ValueError when image dtype is not uint8."""
        with pytest.raises(ValueError, match="uint8"):
            correct_perspective(np.zeros((100, 100, 3), dtype=np.float32))
