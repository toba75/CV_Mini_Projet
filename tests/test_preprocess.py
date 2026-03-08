"""Tests for the image preprocessing module (CLAHE pipeline)."""

import numpy as np
import cv2
import pytest

from src.preprocess import apply_clahe, load_image, preprocess, resize_image


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
