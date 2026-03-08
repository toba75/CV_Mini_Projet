"""Text region detection for the ShelfScan pipeline."""

import numpy as np


def init_detector(model_name: str = "paddleocr"):
    """Initialize a text detector.

    Args:
        model_name: Name of the detection model ("paddleocr" or "craft").

    Returns:
        Initialized detector object.

    Raises:
        ValueError: If model_name is not supported.
    """
    if model_name not in ("paddleocr", "craft"):
        raise ValueError(
            f"Unsupported model: {model_name}. Use 'paddleocr' or 'craft'."
        )

    if model_name == "paddleocr":
        from paddleocr import PaddleOCR

        return PaddleOCR(
            use_angle_cls=True, lang="fr", det=True, rec=False, show_log=False
        )

    raise ValueError(f"Model '{model_name}' is not yet implemented.")


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

    if detector is None:
        detector = init_detector()

    result = detector.ocr(image, det=True, rec=False, cls=False)

    regions: list[dict] = []
    if result and result[0]:
        for detection in result[0]:
            bbox_raw = detection[0] if isinstance(detection[0], list) else detection
            if isinstance(bbox_raw, (list, np.ndarray)) and len(bbox_raw) >= 4:
                points = [[float(p[0]), float(p[1])] for p in bbox_raw[:4]]
                confidence = (
                    float(detection[1])
                    if isinstance(detection, (list, tuple)) and len(detection) > 1
                    else 1.0
                )
                confidence = max(0.0, min(1.0, confidence))
                regions.append({"bbox": points, "confidence": confidence})

    return regions
