"""Image preprocessing for the ShelfScan pipeline.

Provides functions for loading, resizing, and enhancing contrast
of shelf images using CLAHE on the LAB luminance channel.
All functions receive and return images in BGR convention (OpenCV default).
"""

from pathlib import Path

import cv2
import numpy as np


def load_image(path: str) -> np.ndarray:
    """Load an image from disk in BGR format.

    Args:
        path: Path to the image file.

    Returns:
        The loaded image in BGR format (uint8).

    Raises:
        ValueError: If *path* is None or empty, or if OpenCV cannot
            decode the image.
        FileNotFoundError: If the file does not exist on disk.
    """
    if path is None:
        raise ValueError("Image path must not be None.")
    if not isinstance(path, (str, Path)):
        raise TypeError(f"Expected str or Path, got {type(path).__name__}.")

    file_path = Path(path)

    if str(file_path) == "":
        raise ValueError("Image path must not be empty.")

    if not file_path.is_file():
        raise FileNotFoundError(f"Image file not found: {file_path}")

    image = cv2.imread(str(file_path), cv2.IMREAD_COLOR)
    if image is None or image.size == 0:
        raise ValueError(f"Failed to decode image: {file_path}")

    return image


def resize_image(image: np.ndarray, max_width: int = 1920) -> np.ndarray:
    """Resize an image so its width does not exceed *max_width*.

    The aspect ratio is preserved. If the image is already narrower than
    *max_width*, a copy is returned without modification.

    Args:
        image: Input BGR image.
        max_width: Maximum allowed width in pixels (default 1920).

    Returns:
        The (possibly resized) image.

    Raises:
        ValueError: If *image* is None or empty.
    """
    if image is None:
        raise ValueError("Input image must not be None.")
    if not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("Input image must be a non-empty numpy array.")

    height, width = image.shape[:2]

    if width <= max_width:
        return image.copy()

    scale = max_width / width
    new_width = max_width
    new_height = int(height * scale)
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return resized


def apply_clahe(
    image: np.ndarray,
    clip_limit: float = 2.0,
    tile_grid_size: tuple = (8, 8),
) -> np.ndarray:
    """Apply CLAHE on the luminance channel of a BGR image.

    The image is converted from BGR to LAB colour space. CLAHE is applied
    on the L channel, then the image is converted back to BGR.

    Args:
        image: Input BGR image (uint8).
        clip_limit: Contrast limit for CLAHE (default 2.0).
        tile_grid_size: Grid size for the CLAHE algorithm
            (default (8, 8)).

    Returns:
        The contrast-enhanced BGR image.

    Raises:
        ValueError: If *image* is None or empty.
    """
    if image is None:
        raise ValueError("Input image must not be None.")
    if not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("Input image must be a non-empty numpy array.")

    # Work on a copy — never modify the input in place (§R4)
    img = image.copy()

    # BGR → LAB conversion (§R9: CLAHE on L channel)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=clip_limit,
        tileGridSize=tile_grid_size,
    )
    l_enhanced = clahe.apply(l_channel)

    lab_enhanced = cv2.merge([l_enhanced, a_channel, b_channel])

    # LAB → BGR conversion
    result = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
    return result


def preprocess(path: str) -> np.ndarray:
    """Run the full preprocessing pipeline on an image file.

    Steps: load -> resize -> CLAHE.

    Args:
        path: Path to the image file.

    Returns:
        The preprocessed BGR image.
    """
    image = load_image(path)
    image = resize_image(image)
    image = apply_clahe(image)
    return image
