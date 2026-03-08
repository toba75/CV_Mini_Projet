"""Optical character recognition for the ShelfScan pipeline.

Provides a unified interface for three OCR engines:
- PaddleOCR
- TrOCR (Microsoft, via HuggingFace transformers)
- Tesseract 5

All functions validate inputs explicitly and raise ``ValueError``
on invalid data. Images are expected in BGR uint8 format (OpenCV).
"""

from __future__ import annotations

import logging

import cv2
import numpy as np

from src import validate_image

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy imports — heavy dependencies are imported inside functions so that
# the module can be loaded without every backend installed.  For testing,
# these names are patched at module level by unittest.mock.
# ---------------------------------------------------------------------------
# The following names are set at module level *only* when the corresponding
# init function is called.  They are declared here so that ``patch`` targets
# (e.g. ``src.ocr.PaddleOCR``) resolve correctly.
PaddleOCR = None  # type: ignore[assignment]
TrOCRProcessor = None  # type: ignore[assignment]
VisionEncoderDecoderModel = None  # type: ignore[assignment]
pytesseract = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SUPPORTED_ENGINES: tuple[str, ...] = ("paddleocr", "trocr", "tesseract")

# TrOCR default model identifier (configurable).
TROCR_MODEL_NAME: str = "microsoft/trocr-base-printed"

# TrOCR does not expose per-token confidence; use this constant as placeholder.
TROCR_DEFAULT_CONFIDENCE: float = 1.0

# Tesseract confidence threshold below which entries are discarded.
TESSERACT_MIN_CONF: int = 0


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

# Keep module-level alias so that internal callers continue to work.
_validate_image = validate_image


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def init_ocr_engine(engine_name: str) -> object:
    """Initialise and return an OCR engine.

    Args:
        engine_name: One of ``"paddleocr"``, ``"trocr"``, or
            ``"tesseract"``.

    Returns:
        The initialised engine (type depends on *engine_name*).

    Raises:
        ValueError: If *engine_name* is not in :data:`SUPPORTED_ENGINES`.
    """
    global PaddleOCR, TrOCRProcessor, VisionEncoderDecoderModel, pytesseract  # noqa: PLW0603

    if engine_name not in SUPPORTED_ENGINES:
        raise ValueError(
            f"Unknown OCR engine '{engine_name}'. "
            f"Supported: {SUPPORTED_ENGINES}"
        )

    if engine_name == "paddleocr":
        if PaddleOCR is None:
            from paddleocr import PaddleOCR  # type: ignore[no-redef]
        return PaddleOCR(use_angle_cls=True, lang="fr", show_log=False)

    if engine_name == "trocr":
        if TrOCRProcessor is None:
            from transformers import TrOCRProcessor  # type: ignore[no-redef]
        if VisionEncoderDecoderModel is None:
            from transformers import VisionEncoderDecoderModel  # type: ignore[no-redef]
        processor = TrOCRProcessor.from_pretrained(TROCR_MODEL_NAME)
        model = VisionEncoderDecoderModel.from_pretrained(TROCR_MODEL_NAME)
        return {"processor": processor, "model": model}

    # engine_name == "tesseract"
    if pytesseract is None:
        import pytesseract as _pytesseract  # type: ignore[no-redef]
        pytesseract = _pytesseract
    return pytesseract


def recognize_text(
    image: np.ndarray, engine: object
) -> list[dict[str, object]]:
    """Run OCR on *image* using *engine* and return results.

    Args:
        image: BGR uint8 image (OpenCV convention).
        engine: An object returned by :func:`init_ocr_engine`.

    Returns:
        List of dicts, each containing ``"text"`` (str) and
        ``"confidence"`` (float 0-1).
    """
    _validate_image(image)
    image = image.copy()

    # Determine engine type and dispatch.
    if isinstance(engine, dict) and "processor" in engine and "model" in engine:
        return _recognize_trocr(image, engine)

    # pytesseract module: identified by __name__ == "pytesseract".
    if getattr(engine, "__name__", None) == "pytesseract":
        return _recognize_tesseract(image, engine)

    # PaddleOCR-like (has ``.ocr`` method).
    if hasattr(engine, "ocr"):
        return _recognize_paddle(image, engine)

    raise ValueError(
        f"Unrecognised engine type: {type(engine).__name__}"
    )


# ---------------------------------------------------------------------------
# Private engine-specific helpers
# ---------------------------------------------------------------------------

def _recognize_paddle(
    image: np.ndarray, engine: object
) -> list[dict[str, object]]:
    result = engine.ocr(image, cls=True)  # type: ignore[union-attr]
    results: list[dict[str, object]] = []
    if result is None:
        logger.debug("PaddleOCR returned None (no text detected)")
        return results
    for line_group in result:
        if line_group is None:
            logger.debug("PaddleOCR line_group is None, skipping")
            continue
        for entry in line_group:
            text_conf = entry[1]
            text = str(text_conf[0])
            confidence = float(text_conf[1])
            results.append({"text": text, "confidence": confidence})
    return results


def _recognize_trocr(
    image: np.ndarray, engine: dict
) -> list[dict[str, object]]:
    processor = engine["processor"]
    model = engine["model"]
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pixel_values = processor(rgb, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    texts = processor.batch_decode(generated_ids, skip_special_tokens=True)
    results: list[dict[str, object]] = []
    for text in texts:
        # TrOCR does not provide per-token confidence; use default placeholder.
        results.append({"text": str(text), "confidence": TROCR_DEFAULT_CONFIDENCE})
    return results


def _recognize_tesseract(
    image: np.ndarray, engine: object
) -> list[dict[str, object]]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    data = engine.image_to_data(gray, output_type=engine.Output.DICT)  # type: ignore[union-attr]
    results: list[dict[str, object]] = []
    for text, conf in zip(data["text"], data["conf"]):
        conf_val = int(conf)
        if conf_val < TESSERACT_MIN_CONF:
            continue
        if not str(text).strip():
            continue
        results.append({
            "text": str(text),
            "confidence": float(conf_val) / 100.0,
        })
    return results


def _aggregate_ocr_results(
    results: list[dict[str, object]], engine: str
) -> dict[str, object]:
    """Aggregate a list of per-line OCR results into a single dict.

    Args:
        results: List of dicts with ``"text"`` and ``"confidence"`` keys,
            as returned by :func:`recognize_text`.
        engine: Engine name to embed in the returned dict.

    Returns:
        Dict with keys ``"text"`` (concatenated texts), ``"confidence"``
        (mean confidence), and ``"engine"``.
    """
    if not results:
        return {"text": "", "confidence": 0.0, "engine": engine}
    text = " ".join(r["text"] for r in results)
    confidence = sum(float(r["confidence"]) for r in results) / len(results)
    return {"text": text, "confidence": confidence, "engine": engine}


def recognize_text_unified(
    crop: np.ndarray,
    engine: str = "paddleocr",
) -> dict[str, object]:
    """Unified OCR interface: run OCR on a single crop.

    Args:
        crop: BGR uint8 image (oriented text crop).
        engine: Engine name — one of :data:`SUPPORTED_ENGINES`.

    Returns:
        Dict with keys ``"text"`` (str), ``"confidence"`` (float 0-1),
        and ``"engine"`` (str).

    Raises:
        ValueError: If *crop* is invalid or *engine* is unknown.
    """
    _validate_image(crop)
    if engine not in SUPPORTED_ENGINES:
        raise ValueError(
            f"Unknown OCR engine '{engine}'. "
            f"Supported: {SUPPORTED_ENGINES}"
        )
    engine_obj = init_ocr_engine(engine)
    results = recognize_text(crop, engine_obj)
    return _aggregate_ocr_results(results, engine)


def recognize_batch(
    crops: list[np.ndarray],
    engine: str = "paddleocr",
) -> list[dict[str, object]]:
    """Run OCR on a list of crops, reusing a single engine instance.

    Args:
        crops: List of BGR uint8 images.
        engine: Engine name — one of :data:`SUPPORTED_ENGINES`.

    Returns:
        List of dicts, one per crop, each with keys ``"text"``,
        ``"confidence"``, ``"engine"``.

    Raises:
        ValueError: If any crop is invalid or *engine* is unknown.
    """
    if engine not in SUPPORTED_ENGINES:
        raise ValueError(
            f"Unknown OCR engine '{engine}'. "
            f"Supported: {SUPPORTED_ENGINES}"
        )
    if not crops:
        return []
    engine_obj = init_ocr_engine(engine)
    results: list[dict[str, object]] = []
    for crop in crops:
        _validate_image(crop)
        ocr_results = recognize_text(crop, engine_obj)
        results.append(_aggregate_ocr_results(ocr_results, engine))
    return results


def compare_engines(
    image: np.ndarray,
    engine_names: list[str],
) -> dict[str, list[dict[str, object]]]:
    """Run OCR with multiple engines and return comparative results.

    Args:
        image: BGR uint8 image.
        engine_names: List of engine names (each must be in
            :data:`SUPPORTED_ENGINES`).

    Returns:
        Dict ``{engine_name: [results]}`` where each result is a dict
        with ``"text"`` and ``"confidence"``.
    """
    _validate_image(image)
    results: dict[str, list[dict[str, object]]] = {}
    for name in engine_names:
        engine = init_ocr_engine(name)
        results[name] = recognize_text(image, engine)
    return results
