"""Bounding box visualization for the ShelfScan pipeline.

Provides functions to draw colored bounding boxes on shelf images
for debugging, Streamlit demos, and qualitative evaluation.

All functions receive and return images in BGR convention (OpenCV default).
"""

import cv2
import numpy as np

from src import validate_image
from src.segment import (
    MIN_GAP_PX,
    MIN_GAP_RATIO,
    detect_vertical_lines,
)

# Cyclic color palette (BGR) — 10 visually distinct colors. §R2
PALETTE_BGR: list[tuple[int, int, int]] = [
    (0, 255, 0),      # green
    (255, 0, 0),      # blue
    (0, 0, 255),      # red
    (0, 255, 255),    # yellow
    (255, 0, 255),    # magenta
    (255, 255, 0),    # cyan
    (0, 128, 255),    # orange
    (128, 0, 255),    # pink
    (255, 128, 0),    # sky blue
    (0, 255, 128),    # spring green
]

# Box line thickness in pixels. §R2
BOX_THICKNESS: int = 2

# Font settings for labels. §R2
LABEL_FONT = cv2.FONT_HERSHEY_SIMPLEX
LABEL_FONT_SCALE: float = 0.5
LABEL_FONT_THICKNESS: int = 1
LABEL_Y_OFFSET: int = 20


def segment_with_positions(image: np.ndarray) -> list[dict]:
    """Segment a shelf image and return crops with their x-positions.

    Uses the same segmentation logic as :func:`src.segment.segment`
    but also returns the x-boundaries for each crop.

    Args:
        image: Input BGR image (uint8).

    Returns:
        List of dicts, each with keys ``crop`` (np.ndarray),
        ``x_start`` (int), and ``x_end`` (int).

    Raises:
        ValueError: If *image* is None, empty, not 3D, or not uint8.
    """
    validate_image(image)

    lines = detect_vertical_lines(image)
    height, width = image.shape[:2]

    if not lines:
        return [{"crop": image.copy(), "x_start": 0, "x_end": width}]

    # Compute x cut positions as mean of x1 and x2 for each line
    x_cuts_raw = sorted(int((x1 + x2) / 2) for x1, _, x2, _ in lines)

    # Merge cuts that are within a minimum distance
    min_gap = max(MIN_GAP_PX, int(width * MIN_GAP_RATIO))
    x_cuts: list[int] = []
    for x in x_cuts_raw:
        if not x_cuts or (x - x_cuts[-1]) >= min_gap:
            x_cuts.append(x)

    # Build boundaries: [0, x_cut1, x_cut2, ..., width]
    boundaries = [0] + x_cuts + [width]

    results: list[dict] = []
    for i in range(len(boundaries) - 1):
        x_start = boundaries[i]
        x_end = boundaries[i + 1]
        if x_end > x_start:
            crop = image[:height, x_start:x_end].copy()
            results.append({
                "crop": crop,
                "x_start": x_start,
                "x_end": x_end,
            })

    return results


def draw_spine_boxes(
    image: np.ndarray,
    spines: list[dict],
    show_labels: bool = True,
) -> np.ndarray:
    """Draw colored bounding boxes on a copy of the image.

    Args:
        image: Input BGR image (uint8).
        spines: List of dicts, each with keys ``x_start`` (int) and
            ``x_end`` (int). Optional key ``confidence`` (float)
            is displayed when *show_labels* is True.
        show_labels: If True, draw spine index and confidence score
            on each box (default True).

    Returns:
        BGR uint8 image with bounding boxes drawn.

    Raises:
        ValueError: If *image* is None, empty, not 3D, or not uint8.
        ValueError: If any spine dict is missing ``x_start`` or ``x_end``.
        ValueError: If any spine has ``x_start >= x_end``.
    """
    validate_image(image)

    # Validate all spines before drawing anything
    for i, spine in enumerate(spines):
        if "x_start" not in spine:
            raise ValueError(
                f"Spine {i} is missing required key 'x_start'."
            )
        if "x_end" not in spine:
            raise ValueError(
                f"Spine {i} is missing required key 'x_end'."
            )
        if spine["x_start"] >= spine["x_end"]:
            raise ValueError(
                f"Spine {i}: x_start ({spine['x_start']}) must be "
                f"less than x_end ({spine['x_end']})."
            )

    canvas = image.copy()

    if not spines:
        return canvas

    height = image.shape[0]

    for i, spine in enumerate(spines):
        color = PALETTE_BGR[i % len(PALETTE_BGR)]
        x_start = spine["x_start"]
        x_end = spine["x_end"]

        # Draw bounding box rectangle (full height vertical strip)
        cv2.rectangle(
            canvas,
            (x_start, 0),
            (x_end - 1, height - 1),
            color,
            BOX_THICKNESS,
        )

        if show_labels:
            label = f"#{i}"
            if "confidence" in spine:
                label = f"#{i} ({spine['confidence']:.2f})"
            cv2.putText(
                canvas,
                label,
                (x_start + 2, LABEL_Y_OFFSET),
                LABEL_FONT,
                LABEL_FONT_SCALE,
                color,
                LABEL_FONT_THICKNESS,
            )

    return canvas
