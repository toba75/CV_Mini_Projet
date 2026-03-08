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
        ValueError: If *image* is None, empty, not 3-dimensional, or
            not uint8.
    """
    if image is None:
        raise ValueError("Input image must not be None.")
    if not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("Input image must be a non-empty numpy array.")
    if image.ndim != 3:
        raise ValueError(
            f"image must have 3 dimensions (H, W, C), got ndim={image.ndim}"
        )
    if image.dtype != np.uint8:
        raise ValueError(f"image dtype must be uint8, got {image.dtype}")

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
        ValueError: If *image* is None, empty, not 3-dimensional, or
            not uint8.
    """
    if image is None:
        raise ValueError("Input image must not be None.")
    if not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("Input image must be a non-empty numpy array.")
    if image.ndim != 3:
        raise ValueError(
            f"image must have 3 dimensions (H, W, C), got ndim={image.ndim}"
        )
    if image.dtype != np.uint8:
        raise ValueError(f"image dtype must be uint8, got {image.dtype}")

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


def _validate_image(image: np.ndarray | None) -> None:
    """Raise ``ValueError`` if *image* is None, empty, or malformed."""
    if image is None:
        raise ValueError("Input image must not be None.")
    if not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("Input image must be a non-empty numpy array.")
    if image.ndim != 3:
        raise ValueError(
            f"image must have 3 dimensions (H, W, C), got ndim={image.ndim}"
        )
    if image.dtype != np.uint8:
        raise ValueError(f"image dtype must be uint8, got {image.dtype}")


def _order_corners(pts: np.ndarray) -> np.ndarray:
    """Order four points as: top-left, top-right, bottom-right, bottom-left.

    Args:
        pts: Array of shape (4, 2).

    Returns:
        Ordered array of shape (4, 2) with dtype float32.
    """
    pts = pts.reshape(4, 2).astype(np.float32)
    # Sum and diff discriminate corners:
    #   top-left has smallest sum, bottom-right has largest sum
    #   top-right has smallest diff, bottom-left has largest diff
    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).ravel()
    ordered = np.array(
        [pts[np.argmin(s)], pts[np.argmin(d)], pts[np.argmax(s)], pts[np.argmax(d)]],
        dtype=np.float32,
    )
    return ordered


def detect_shelf_contour(image: np.ndarray) -> np.ndarray | None:
    """Detect the dominant quadrilateral contour in a shelf image.

    Uses Canny edge detection followed by ``cv2.findContours`` and
    ``cv2.approxPolyDP`` to find the largest 4-sided contour.

    Args:
        image: Input BGR image (uint8).

    Returns:
        Ordered corners as an array of shape (4, 2) with dtype float32
        (top-left, top-right, bottom-right, bottom-left), or ``None``
        if no suitable quadrilateral is found.

    Raises:
        ValueError: If *image* is None, empty, not 3D, or not uint8.
    """
    _validate_image(image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # Dilate to close gaps in edge contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges = cv2.dilate(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # Sort contours by area (descending) and try to approximate to a quad
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for cnt in contours:
        peri = cv2.arcLength(cnt, closed=True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, closed=True)
        if len(approx) == 4 and cv2.contourArea(approx) > 1000:
            return _order_corners(approx.reshape(4, 2))

    return None


def correct_perspective(
    image: np.ndarray,
    corners: np.ndarray | None = None,
) -> np.ndarray:
    """Apply a perspective correction to straighten a shelf image.

    If *corners* is ``None``, attempts automatic detection via
    :func:`detect_shelf_contour`.  If no contour is found, returns
    a copy of the original image without raising an error.

    Args:
        image: Input BGR image (uint8).
        corners: Optional array of shape (4, 2) with the source
            quadrilateral corners (top-left, top-right, bottom-right,
            bottom-left).

    Returns:
        The perspective-corrected BGR image, or a copy of the original
        image if no correction could be applied.

    Raises:
        ValueError: If *image* is None, empty, not 3D, or not uint8.
    """
    _validate_image(image)

    if corners is None:
        corners = detect_shelf_contour(image)
        if corners is None:
            return image.copy()

    corners = corners.astype(np.float32).reshape(4, 2)

    # Compute destination rectangle from the bounding box of the corners
    tl, tr, br, bl = corners

    width_top = np.linalg.norm(tr - tl)
    width_bot = np.linalg.norm(br - bl)
    max_w = int(max(width_top, width_bot))

    height_left = np.linalg.norm(bl - tl)
    height_right = np.linalg.norm(br - tr)
    max_h = int(max(height_left, height_right))

    # Safeguard against degenerate sizes
    max_w = max(max_w, 1)
    max_h = max(max_h, 1)

    dst = np.array(
        [[0, 0], [max_w - 1, 0], [max_w - 1, max_h - 1], [0, max_h - 1]],
        dtype=np.float32,
    )

    M = cv2.getPerspectiveTransform(corners, dst)
    result = cv2.warpPerspective(image, M, (max_w, max_h))
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
