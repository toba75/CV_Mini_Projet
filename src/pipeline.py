"""End-to-end ShelfScan pipeline orchestration."""

import csv
import json
import logging
import time
from pathlib import Path

from src.detect_text import correct_orientation, detect_text_regions, init_detector
from src.ocr import _aggregate_ocr_results, init_ocr_engine, recognize_text
from src.postprocess import identify_book, postprocess_spine
from src.preprocess import preprocess
from src.segment import segment

logger = logging.getLogger(__name__)

_VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}

_DEFAULT_OUTPUT_DIR = "outputs"


def run_pipeline(
    image_path: str | Path,
    ocr_engine: str = "paddleocr",
    output_dir: str | Path | None = None,
) -> dict:
    """Run the full ShelfScan pipeline on an image.

    Pipeline steps: preprocess -> segment -> detect_text -> correct_orientation
    -> OCR -> postprocess -> identify.

    Args:
        image_path: Path to the shelf image.
        ocr_engine: OCR engine name (default ``"paddleocr"``).
        output_dir: If provided, auto-export JSON to this directory.

    Returns:
        Structured dict with keys ``image``, ``num_spines_detected``,
        ``processing_time_s``, and ``books``.

    Raises:
        FileNotFoundError: If image does not exist.
        ValueError: If file is not a valid image format.
    """
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    if image_path.suffix.lower() not in _VALID_IMAGE_EXTENSIONS:
        raise ValueError(
            f"Not a valid image file: {image_path.suffix}. "
            f"Supported: {_VALID_IMAGE_EXTENSIONS}"
        )

    start = time.perf_counter()

    # Step 1: Preprocess
    preprocessed = preprocess(str(image_path))

    # Step 2: Segment spines
    spines = segment(preprocessed)

    # Pre-initialise detector and OCR engine once (avoid per-spine overhead)
    detector = init_detector()
    ocr_engine_obj = init_ocr_engine(ocr_engine)

    books: list[dict] = []

    for idx, spine_crop in enumerate(spines, start=1):
        try:
            # Step 3: Detect text regions
            text_regions = detect_text_regions(spine_crop, detector=detector)

            # Step 4: Correct orientation
            corrected = correct_orientation(spine_crop, text_regions)

            # Step 5: OCR
            ocr_results = recognize_text(corrected, ocr_engine_obj)
            ocr_result = _aggregate_ocr_results(ocr_results, ocr_engine)
            raw_text = ocr_result.get("text", "")

            # Step 6: Postprocess
            spine_info = postprocess_spine([raw_text])

            # Step 7: Identify
            identification = identify_book(spine_info.get("title", ""))

            book_entry: dict = {
                "spine_id": idx,
                "raw_text": spine_info.get("raw_text", raw_text),
                "title": spine_info.get("title", ""),
                "author": spine_info.get("author"),
                "isbn": None,
                "confidence": 0.0,
            }

            if identification is not None:
                book_entry["title"] = identification.get("title", book_entry["title"])
                book_entry["author"] = identification.get("author", book_entry["author"])
                book_entry["isbn"] = identification.get("isbn")
                book_entry["confidence"] = identification.get("confidence", 0.0)

            books.append(book_entry)

        except Exception:
            logger.exception("Error processing spine %d, skipping.", idx)
            continue

    elapsed = time.perf_counter() - start

    result = {
        "image": image_path.name,
        "num_spines_detected": len(spines),
        "processing_time_s": round(elapsed, 3),
        "books": books,
    }

    if output_dir is not None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / f"{image_path.stem}_result.json"
        export_json(result, json_path)

    return result


def export_json(result: dict, output_path: str | Path) -> Path:
    """Write pipeline result to a JSON file.

    Args:
        result: Pipeline result dict.
        output_path: Destination file path.

    Returns:
        The output Path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return output_path


def export_csv(result: dict, output_path: str | Path) -> Path:
    """Export books list as CSV.

    Columns: spine_id, raw_text, title, author, isbn, confidence.

    Args:
        result: Pipeline result dict containing a ``books`` list.
        output_path: Destination file path.

    Returns:
        The output Path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["spine_id", "raw_text", "title", "author", "isbn", "confidence"]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for book in result.get("books", []):
            writer.writerow(book)

    return output_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python -m src.pipeline <image_path> [output_dir]\n")
        sys.exit(1)

    img = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else _DEFAULT_OUTPUT_DIR
    result = run_pipeline(img, output_dir=out)
    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
