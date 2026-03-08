"""Book spine segmentation for the ShelfScan pipeline.

Provides naive segmentation of book spines on shelf images using
Canny edge detection and probabilistic Hough line transform to detect
vertical boundaries between books, then splitting the image into
vertical strips (crops).

All functions receive and return images in BGR convention (OpenCV default).
"""

import math

import cv2
import numpy as np

# Minimum gap between two x-cut positions (pixels). §R2
MIN_GAP_PX: int = 5
# Minimum gap between two x-cut positions as a ratio of image width. §R2
MIN_GAP_RATIO: float = 0.02


def detect_vertical_lines(
    image: np.ndarray,
    canny_low: int = 50,
    canny_high: int = 150,
    hough_threshold: int = 50,
    min_line_length: int = 50,
    max_line_gap: int = 10,
    angle_threshold: float = 15.0,
) -> list[tuple]:
    """Detect quasi-vertical lines in a BGR image using Canny + HoughLinesP.

    Args:
        image: Input BGR image (uint8).
        canny_low: Lower threshold for Canny edge detector (default 50).
        canny_high: Upper threshold for Canny edge detector (default 150).
        hough_threshold: Accumulator threshold for HoughLinesP (default 50).
        min_line_length: Minimum line length in pixels for HoughLinesP
            (default 50).
        max_line_gap: Maximum gap between line segments for HoughLinesP
            (default 10).
        angle_threshold: Maximum angle in degrees from vertical to keep a
            line (default 15.0).

    Returns:
        List of (x1, y1, x2, y2) tuples sorted by x position (ascending).

    Raises:
        ValueError: If *image* is None, empty, not 3D, or not uint8.
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

    # Convert to grayscale for edge detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray, canny_low, canny_high)

    raw_lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=hough_threshold,
        minLineLength=min_line_length,
        maxLineGap=max_line_gap,
    )

    if raw_lines is None:
        return []

    vertical_lines: list[tuple] = []
    for line in raw_lines:
        x1, y1, x2, y2 = line[0]
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        # Compute angle from vertical (y-axis): atan2(dx, dy)
        angle_deg = math.degrees(math.atan2(dx, dy))
        if angle_deg <= angle_threshold:
            vertical_lines.append((int(x1), int(y1), int(x2), int(y2)))

    # Sort by mean x position
    vertical_lines.sort(key=lambda ln: (ln[0] + ln[2]) / 2)

    return vertical_lines


def split_spines(
    image: np.ndarray,
    lines: list[tuple],
) -> list[np.ndarray]:
    """Split an image into vertical strips based on detected line positions.

    Args:
        image: Input BGR image (uint8).
        lines: List of (x1, y1, x2, y2) line coordinates, sorted by
            x position.

    Returns:
        List of cropped BGR images (book spine candidates).

    Raises:
        ValueError: If *image* is None, empty, not 3D, or not uint8.
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

    if not lines:
        return [image.copy()]

    height, width = image.shape[:2]

    # Compute x cut positions as mean of x1 and x2 for each line
    x_cuts_raw = sorted(int((x1 + x2) / 2) for x1, _, x2, _ in lines)

    # Merge cuts that are within a minimum distance (avoid duplicate
    # detections from both edges of the same book boundary).
    # Minimum gap: 2% of image width or 5 pixels, whichever is larger.
    min_gap = max(MIN_GAP_PX, int(width * MIN_GAP_RATIO))
    x_cuts: list[int] = []
    for x in x_cuts_raw:
        if not x_cuts or (x - x_cuts[-1]) >= min_gap:
            x_cuts.append(x)

    # Build boundaries: [0, x_cut1, x_cut2, ..., width]
    boundaries = [0] + x_cuts + [width]

    crops: list[np.ndarray] = []
    for i in range(len(boundaries) - 1):
        x_start = boundaries[i]
        x_end = boundaries[i + 1]
        if x_end > x_start:
            crop = image[:height, x_start:x_end].copy()
            crops.append(crop)

    return crops


def segment(image: np.ndarray) -> list[np.ndarray]:
    """Segment a shelf image into individual book spine crops.

    Orchestrates detect_vertical_lines and split_spines. If no lines
    are detected, returns the entire image as a single crop.

    Args:
        image: Input BGR image (uint8).

    Returns:
        List of cropped BGR images (one per detected book spine).

    Raises:
        ValueError: If *image* is None, empty, not 3D, or not uint8.
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

    lines = detect_vertical_lines(image)
    crops = split_spines(image, lines)

    if not crops:
        return [image.copy()]

    return crops
