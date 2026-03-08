"""ShelfScan source package."""

import numpy as np


def validate_image(image: np.ndarray | None) -> None:
    """Raise ``ValueError`` if *image* is None, empty, or malformed.

    Shared validation helper used by all pipeline modules.

    Args:
        image: Image to validate. Must be a 3-D uint8 numpy array.

    Raises:
        ValueError: If *image* is None, not an ndarray, empty,
            not 3-dimensional, or not uint8.
    """
    if image is None:
        raise ValueError("Input image must not be None.")
    if not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("Input image must be a non-empty numpy array.")
    if image.ndim != 3:
        raise ValueError(
            f"image must be 3-dimensional (H, W, C), got ndim={image.ndim}"
        )
    if image.dtype != np.uint8:
        raise ValueError(f"image dtype must be uint8, got {image.dtype}")
