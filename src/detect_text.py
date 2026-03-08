"""Text region detection for the ShelfScan pipeline."""

import math

import cv2
import numpy as np

from src import validate_image

# PaddleOCR in det-only mode (rec=False) does not return a confidence score
# for detected text regions. We use 1.0 as the default confidence in that case.
DEFAULT_DET_CONFIDENCE: float = 1.0


def init_detector(model_name: str = "paddleocr"):
    """Initialize a text detector.

    Args:
        model_name: Name of the detection model. Currently only "paddleocr"
            is supported.

    Returns:
        Initialized detector object.

    Raises:
        ValueError: If model_name is not supported.
    """
    if model_name != "paddleocr":
        raise ValueError(
            f"Unsupported model: {model_name}. Only 'paddleocr' is currently available."
        )

    from paddleocr import PaddleOCR

    return PaddleOCR(
        use_angle_cls=True, lang="fr", det=True, rec=False, show_log=False
    )


def _polygon_area(points: list[list[float]]) -> float:
    """Compute the area of a polygon using the Shoelace formula.

    Args:
        points: List of [x, y] coordinate pairs forming the polygon.

    Returns:
        Absolute area of the polygon.
    """
    n = len(points)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    return abs(area) / 2.0


def filter_small_regions(
    regions: list[dict], min_area: float = 100,
) -> list[dict]:
    """Remove bounding boxes whose area is below *min_area*.

    The area is computed from the 4-point polygon using the Shoelace formula.

    Args:
        regions: List of dicts with key ``bbox`` (4-point polygon).
        min_area: Minimum polygon area to keep a region.

    Returns:
        Filtered list of region dicts.
    """
    return [r for r in regions if _polygon_area(r["bbox"]) >= min_area]


def filter_by_aspect_ratio(
    regions: list[dict],
    min_ratio: float = 0.1,
    max_ratio: float = 10.0,
) -> list[dict]:
    """Remove regions whose width/height aspect ratio is outside bounds.

    Width and height are derived from the axis-aligned bounding rectangle
    of the 4-point polygon.

    Args:
        regions: List of dicts with key ``bbox`` (4-point polygon).
        min_ratio: Minimum width/height ratio (inclusive).
        max_ratio: Maximum width/height ratio (inclusive).

    Returns:
        Filtered list of region dicts.
    """
    filtered: list[dict] = []
    for r in regions:
        xs = [p[0] for p in r["bbox"]]
        ys = [p[1] for p in r["bbox"]]
        w = max(xs) - min(xs)
        h = max(ys) - min(ys)
        if h == 0.0:
            continue
        ratio = w / h
        if min_ratio <= ratio <= max_ratio:
            filtered.append(r)
    return filtered


# Default thresholds for detection filtering (§R2 — no hardcoding)
CONFIDENCE_THRESHOLD: float = 0.5
MIN_REGION_AREA: float = 100.0
MIN_ASPECT_RATIO: float = 0.1
MAX_ASPECT_RATIO: float = 10.0


def detect_text_regions(
    image: np.ndarray,
    detector=None,
    confidence_threshold: float = CONFIDENCE_THRESHOLD,
    min_area: float = MIN_REGION_AREA,
    min_ratio: float = MIN_ASPECT_RATIO,
    max_ratio: float = MAX_ASPECT_RATIO,
) -> list[dict]:
    """Detect text regions in an image.

    Args:
        image: Input image in BGR format.
        detector: Initialized detector (from init_detector).
            If None, a default detector is initialized.
        confidence_threshold: Minimum confidence to keep a detection.
        min_area: Minimum polygon area to keep a detection.
        min_ratio: Minimum width/height aspect ratio.
        max_ratio: Maximum width/height aspect ratio.

    Returns:
        List of dicts with keys 'bbox' (4-point polygon) and
        'confidence' (float in [0, 1]).

    Raises:
        ValueError: If image is None, not a numpy array, or empty.
    """
    validate_image(image)

    image = image.copy()

    if detector is None:
        detector = init_detector()

    result = detector.ocr(image, det=True, rec=False, cls=False)

    regions: list[dict] = []
    if result and result[0]:
        for detection in result[0]:
            bbox_raw = detection[0] if isinstance(detection[0], list) else detection
            if isinstance(bbox_raw, (list, np.ndarray)) and len(bbox_raw) >= 4:
                points = [[float(p[0]), float(p[1])] for p in bbox_raw[:4]]
                # In det-only mode, PaddleOCR may not return a confidence
                # score; use DEFAULT_DET_CONFIDENCE in that case.
                confidence = (
                    float(detection[1])
                    if isinstance(detection, (list, tuple)) and len(detection) > 1
                    else DEFAULT_DET_CONFIDENCE
                )
                confidence = max(0.0, min(1.0, confidence))
                if confidence >= confidence_threshold:
                    regions.append({"bbox": points, "confidence": confidence})

    regions = filter_small_regions(regions, min_area=min_area)
    regions = filter_by_aspect_ratio(
        regions, min_ratio=min_ratio, max_ratio=max_ratio,
    )

    return regions


def group_text_lines(
    regions: list[dict], line_threshold: float = 0.5
) -> list[list[dict]]:
    """Group text regions into logical lines based on vertical proximity.

    Regions whose vertical centers are within *line_threshold* times the
    average region height of each other are placed into the same group.

    Args:
        regions: List of dicts with key ``bbox`` (4-point polygon).
        line_threshold: Multiplier of average height used as proximity
            threshold for grouping.

    Returns:
        List of groups, where each group is a list of region dicts.
    """
    if not regions:
        return []

    def _vertical_center(region: dict) -> float:
        ys = [pt[1] for pt in region["bbox"]]
        return (min(ys) + max(ys)) / 2.0

    def _height(region: dict) -> float:
        ys = [pt[1] for pt in region["bbox"]]
        return max(ys) - min(ys)

    avg_height = sum(_height(r) for r in regions) / len(regions)
    threshold = line_threshold * avg_height if avg_height > 0 else 1.0

    # Sort by vertical center
    sorted_regions = sorted(regions, key=_vertical_center)

    groups: list[list[dict]] = [[sorted_regions[0]]]
    for region in sorted_regions[1:]:
        last_center = _vertical_center(groups[-1][-1])
        curr_center = _vertical_center(region)
        if abs(curr_center - last_center) <= threshold:
            groups[-1].append(region)
        else:
            groups.append([region])

    return groups


def detect_text_on_spines(
    crops: list[np.ndarray], engine: str = "paddleocr"
) -> list[list[dict]]:
    """Apply text detection on a batch of spine crops.

    Args:
        crops: List of BGR images (spine crops).
        engine: Detection engine name (default ``"paddleocr"``).

    Returns:
        List of detection results, one list of region dicts per crop.

    Raises:
        ValueError: If *crops* is None.
    """
    if crops is None:
        raise ValueError("crops cannot be None.")

    if len(crops) == 0:
        return []

    detector = init_detector(engine)
    results: list[list[dict]] = []
    for crop in crops:
        regions = detect_text_regions(crop, detector=detector)
        results.append(regions)

    return results


def estimate_text_angle(bboxes: list[dict]) -> float:
    """Estimate the dominant text angle from oriented bounding boxes.

    Uses the median angle of the top edge (first two points) of each bbox.

    Args:
        bboxes: List of dicts with key ``bbox`` (4-point polygon).

    Returns:
        Estimated angle in degrees. Returns 0.0 for an empty list.
    """
    if not bboxes:
        return 0.0

    angles: list[float] = []
    for box in bboxes:
        pts = box["bbox"]
        # Top edge: from pts[0] to pts[1]
        dx = pts[1][0] - pts[0][0]
        dy = pts[1][1] - pts[0][1]
        angle = math.degrees(math.atan2(dy, dx))
        angles.append(angle)

    # Use median for robustness
    angles.sort()
    n = len(angles)
    if n % 2 == 1:
        return angles[n // 2]
    return (angles[n // 2 - 1] + angles[n // 2]) / 2.0


# Keep module-level alias so that internal callers continue to work.
_validate_image = validate_image


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """Rotate *image* around its center by *angle* degrees.

    Adjusts the output dimensions so that no content is clipped.

    Args:
        image: Input BGR image.
        angle: Rotation angle in degrees (counter-clockwise positive).

    Returns:
        Rotated image (BGR, uint8).

    Raises:
        ValueError: If *image* is None or invalid.
    """
    _validate_image(image)

    h, w = image.shape[:2]
    cx, cy = w / 2.0, h / 2.0

    rot_mat = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)

    # Compute new bounding dimensions to avoid clipping
    cos_a = abs(rot_mat[0, 0])
    sin_a = abs(rot_mat[0, 1])
    new_w = int(math.ceil(h * sin_a + w * cos_a))
    new_h = int(math.ceil(h * cos_a + w * sin_a))

    # Adjust the rotation matrix for the new center
    rot_mat[0, 2] += (new_w / 2.0) - cx
    rot_mat[1, 2] += (new_h / 2.0) - cy

    return cv2.warpAffine(image, rot_mat, (new_w, new_h))


def correct_orientation(
    crop: np.ndarray,
    bboxes: list[dict],
    angle_threshold: float = 2.0,
) -> np.ndarray:
    """Correct the orientation of a spine crop based on detected text angles.

    Estimates the dominant text angle and rotates the crop if the angle
    exceeds *angle_threshold*.

    Args:
        crop: Input BGR image (spine crop).
        bboxes: List of detected text region dicts with ``bbox`` key.
        angle_threshold: Minimum angle (degrees) to trigger rotation.

    Returns:
        Orientation-corrected image, or the original crop if the angle
        is below the threshold.

    Raises:
        ValueError: If *crop* is None or invalid.
    """
    _validate_image(crop)

    angle = estimate_text_angle(bboxes)
    if abs(angle) < angle_threshold:
        return crop.copy()

    return rotate_image(crop, -angle)
