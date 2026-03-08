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

from src import validate_image

# Minimum gap between two x-cut positions (pixels). §R2
MIN_GAP_PX: int = 5
# Minimum gap between two x-cut positions as a ratio of image width. §R2
MIN_GAP_RATIO: float = 0.02
# Default variance threshold for empty region detection. §R2
DEFAULT_VARIANCE_THRESHOLD: float = 50.0
# Minimum aspect ratio (height/width) for a crop to be considered a book spine. §R2
MIN_BOOK_ASPECT_RATIO: float = 2.0
# Default minimum width ratio for thin spine merging. §R2
DEFAULT_MIN_WIDTH_RATIO: float = 0.02


# Keep module-level alias so that internal callers continue to work.
_validate_image = validate_image


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
    _validate_image(image)

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
    _validate_image(image)

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


def filter_lines(
    lines: list[tuple],
    image_height: int,
    min_length_ratio: float = 0.3,
    max_angle_deg: float = 15.0,
) -> list[tuple]:
    """Filter lines that are too short or too inclined from vertical.

    Args:
        lines: List of (x1, y1, x2, y2) line coordinates.
        image_height: Height of the source image in pixels.
        min_length_ratio: Minimum line length as a ratio of *image_height*
            (default 0.3).
        max_angle_deg: Maximum angle in degrees from vertical to keep a
            line (default 15.0).

    Returns:
        Filtered list of (x1, y1, x2, y2) tuples.
    """
    min_length = min_length_ratio * image_height
    filtered: list[tuple] = []
    for x1, y1, x2, y2 in lines:
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        length = math.hypot(dx, dy)
        if length < min_length:
            continue
        angle_deg = math.degrees(math.atan2(dx, dy))
        if angle_deg > max_angle_deg:
            continue
        filtered.append((x1, y1, x2, y2))
    return filtered


def split_wide_gaps(
    lines: list[tuple],
    image_width: int,
    median_width: float,
) -> list[tuple]:
    """Insert virtual vertical lines where the gap between consecutive
    lines exceeds 2× the *median_width*.

    Args:
        lines: List of (x1, y1, x2, y2) line coordinates, sorted by x.
        image_width: Width of the source image in pixels.
        median_width: Median width of detected segments.

    Returns:
        Augmented list of lines with virtual lines inserted, sorted by x.
    """
    if not lines or median_width <= 0:
        return list(lines)

    threshold = 2.0 * median_width

    # Compute x-cut positions
    x_cuts = sorted(int((x1 + x2) / 2) for x1, _, x2, _ in lines)

    # Determine representative y-span from existing lines
    y_min = min(min(y1, y2) for _, y1, _, y2 in lines)
    y_max = max(max(y1, y2) for _, y1, _, y2 in lines)

    augmented = list(lines)

    for i in range(len(x_cuts) - 1):
        gap = x_cuts[i + 1] - x_cuts[i]
        if gap > threshold:
            n_virtual = int(gap / median_width)
            step = gap / (n_virtual + 1)
            for j in range(1, n_virtual + 1):
                vx = int(x_cuts[i] + j * step)
                augmented.append((vx, y_min, vx, y_max))

    # Sort by x position
    augmented.sort(key=lambda ln: (ln[0] + ln[2]) / 2)
    return augmented


def crop_spines(
    image: np.ndarray,
    lines: list[tuple],
    min_width: int = 20,
) -> list[np.ndarray]:
    """Produce individual spine crops from filtered lines.

    Similar to :func:`split_spines` but discards crops narrower than
    *min_width*.

    Args:
        image: Input BGR image (uint8).
        lines: List of (x1, y1, x2, y2) line coordinates, sorted by x.
        min_width: Minimum crop width in pixels (default 20). Crops
            narrower than this are discarded.

    Returns:
        List of cropped BGR images with width >= *min_width*.

    Raises:
        ValueError: If *image* is None, empty, not 3D, or not uint8.
    """
    _validate_image(image)

    if not lines:
        return [image.copy()]

    height, width = image.shape[:2]

    x_cuts_raw = sorted(int((x1 + x2) / 2) for x1, _, x2, _ in lines)

    # Merge nearby cuts
    min_gap = max(MIN_GAP_PX, int(width * MIN_GAP_RATIO))
    x_cuts: list[int] = []
    for x in x_cuts_raw:
        if not x_cuts or (x - x_cuts[-1]) >= min_gap:
            x_cuts.append(x)

    boundaries = [0] + x_cuts + [width]

    crops: list[np.ndarray] = []
    for i in range(len(boundaries) - 1):
        x_start = boundaries[i]
        x_end = boundaries[i + 1]
        crop_width = x_end - x_start
        if crop_width >= min_width:
            crop = image[:height, x_start:x_end].copy()
            crops.append(crop)

    if not crops:
        return [image.copy()]

    return crops


def detect_empty_regions(
    image: np.ndarray,
    crops: list[np.ndarray],
    variance_threshold: float = DEFAULT_VARIANCE_THRESHOLD,
) -> list[bool]:
    """Detect crops that are empty (low texture variance).

    Args:
        image: Source BGR image (uint8), used for validation.
        crops: List of cropped BGR images to evaluate.
        variance_threshold: Maximum variance (on grayscale) below which
            a crop is considered empty (default 50.0).

    Returns:
        List of booleans, True if the corresponding crop is empty.

    Raises:
        ValueError: If *image* is None, empty, not 3D, or not uint8.
    """
    _validate_image(image)

    if not crops:
        return []

    result: list[bool] = []
    for crop in crops:
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        variance = float(np.var(gray))
        result.append(variance < variance_threshold)

    return result


def classify_spine(crop: np.ndarray) -> dict:
    """Classify a crop as book or non-book based on aspect ratio and texture.

    Args:
        crop: BGR image crop (uint8).

    Returns:
        Dictionary with keys ``is_book`` (bool) and ``reason`` (str).

    Raises:
        ValueError: If *crop* is None, empty, not 3D, or not uint8.
    """
    _validate_image(crop)

    h, w = crop.shape[:2]
    aspect_ratio = h / w

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    variance = float(np.var(gray))

    if variance < DEFAULT_VARIANCE_THRESHOLD:
        return {"is_book": False, "reason": "low texture variance"}

    if aspect_ratio < MIN_BOOK_ASPECT_RATIO:
        return {"is_book": False, "reason": "aspect ratio too low"}

    return {"is_book": True, "reason": "book spine"}


def merge_thin_spines(
    crops: list[np.ndarray],
    min_width_ratio: float = DEFAULT_MIN_WIDTH_RATIO,
) -> list[np.ndarray]:
    """Merge adjacent thin crops into wider ones.

    Args:
        crops: List of cropped BGR images, ordered left to right.
        min_width_ratio: Minimum width as a ratio of the total width
            of all crops. Crops thinner than this are merged with
            their neighbours.

    Returns:
        List of merged BGR images.
    """
    if not crops:
        return []

    total_width = sum(c.shape[1] for c in crops)
    min_width = max(1, int(total_width * min_width_ratio))

    merged: list[np.ndarray] = []
    buffer: list[np.ndarray] = []

    for crop in crops:
        is_thin = crop.shape[1] < min_width
        if is_thin:
            buffer.append(crop)
        else:
            # Flush buffer before adding non-thin crop
            if buffer:
                merged_crop = np.concatenate(buffer, axis=1)
                merged.append(merged_crop)
                buffer = []
            merged.append(crop)

    # Flush remaining buffer
    if buffer:
        if merged:
            # Merge remaining thin crops with the last merged crop
            last = merged.pop()
            combined = [last] + buffer
            merged.append(np.concatenate(combined, axis=1))
        else:
            merged.append(np.concatenate(buffer, axis=1))

    return merged


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
    _validate_image(image)

    lines = detect_vertical_lines(image)
    crops = split_spines(image, lines)

    if not crops:
        return [image.copy()]

    return crops


def segment_robust(image: np.ndarray) -> list[dict]:
    """Robust segmentation with edge-case handling.

    Orchestrates the full pipeline: detect lines, crop spines, merge thin
    spines, detect empty regions, and classify each crop as book or
    non-book.

    Args:
        image: Input BGR image (uint8).

    Returns:
        List of dicts, each with keys ``crop`` (np.ndarray) and
        ``is_book`` (bool).

    Raises:
        ValueError: If *image* is None, empty, not 3D, or not uint8.
    """
    _validate_image(image)

    lines = detect_vertical_lines(image)
    crops = split_spines(image, lines)

    if not crops:
        crops = [image.copy()]

    # Merge thin spines
    crops = merge_thin_spines(crops)

    # Detect empty regions
    empty_flags = detect_empty_regions(image, crops)

    # Classify each crop
    results: list[dict] = []
    for i, crop in enumerate(crops):
        if empty_flags[i]:
            results.append({"crop": crop, "is_book": False})
        else:
            classification = classify_spine(crop)
            results.append({"crop": crop, "is_book": classification["is_book"]})

    return results
