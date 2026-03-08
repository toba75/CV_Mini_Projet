"""Text region detection for the ShelfScan pipeline."""

import numpy as np

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


def detect_text_regions(
    image: np.ndarray, detector=None
) -> list[dict]:
    """Detect text regions in an image.

    Args:
        image: Input image in BGR format.
        detector: Initialized detector (from init_detector).
            If None, a default detector is initialized.

    Returns:
        List of dicts with keys 'bbox' (4-point polygon) and
        'confidence' (float in [0, 1]).

    Raises:
        ValueError: If image is None, not a numpy array, or empty.
    """
    if image is None:
        raise ValueError("Image cannot be None.")
    if not isinstance(image, np.ndarray):
        raise ValueError("Image must be a numpy array.")
    if image.size == 0:
        raise ValueError("Image cannot be empty.")
    if image.ndim != 3:
        raise ValueError("Image must be 3-dimensional (H, W, C).")
    if image.dtype != np.uint8:
        raise ValueError("Image must be uint8.")

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
                regions.append({"bbox": points, "confidence": confidence})

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
