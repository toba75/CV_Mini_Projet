"""Tests for OCR module — TDD RED phase for task #005."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.ocr import compare_engines, init_ocr_engine, recognize_text

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_ENGINES = ("paddleocr", "trocr", "tesseract")


def _make_image(height: int = 64, width: int = 256, channels: int = 3) -> np.ndarray:
    """Create a synthetic BGR uint8 image."""
    rng = np.random.default_rng(42)
    return rng.integers(0, 256, size=(height, width, channels), dtype=np.uint8)


# ---------------------------------------------------------------------------
# init_ocr_engine
# ---------------------------------------------------------------------------


class TestInitOcrEngine:
    """Tests for init_ocr_engine."""

    @patch("src.ocr.PaddleOCR")
    def test_init_paddleocr(self, mock_cls: MagicMock) -> None:
        mock_cls.return_value = MagicMock()
        engine = init_ocr_engine("paddleocr")
        assert engine is not None
        mock_cls.assert_called_once()

    @patch("src.ocr.VisionEncoderDecoderModel")
    @patch("src.ocr.TrOCRProcessor")
    def test_init_trocr(
        self, mock_proc: MagicMock, mock_model: MagicMock
    ) -> None:
        mock_proc.from_pretrained.return_value = MagicMock()
        mock_model.from_pretrained.return_value = MagicMock()
        engine = init_ocr_engine("trocr")
        assert engine is not None
        assert isinstance(engine, dict)
        assert "processor" in engine
        assert "model" in engine

    @patch("src.ocr.pytesseract", new_callable=lambda: MagicMock)
    def test_init_tesseract(self, _mock_tess: MagicMock) -> None:
        engine = init_ocr_engine("tesseract")
        assert engine is not None

    def test_init_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown"):
            init_ocr_engine("unknown")


# ---------------------------------------------------------------------------
# recognize_text
# ---------------------------------------------------------------------------


class TestRecognizeText:
    """Tests for recognize_text."""

    def test_returns_list_of_dicts(self) -> None:
        engine = MagicMock()
        engine.__class__.__name__ = "PaddleOCR"
        engine.ocr.return_value = [
            [
                [[[0, 0], [100, 0], [100, 30], [0, 30]], ("hello", 0.95)],
            ]
        ]
        image = _make_image()
        results = recognize_text(image, engine)
        assert isinstance(results, list)
        assert len(results) > 0
        for item in results:
            assert "text" in item
            assert "confidence" in item

    def test_confidence_is_float_between_0_and_1(self) -> None:
        engine = MagicMock()
        engine.__class__.__name__ = "PaddleOCR"
        engine.ocr.return_value = [
            [
                [[[0, 0], [100, 0], [100, 30], [0, 30]], ("word", 0.87)],
            ]
        ]
        image = _make_image()
        results = recognize_text(image, engine)
        for item in results:
            assert isinstance(item["confidence"], float)
            assert 0.0 <= item["confidence"] <= 1.0

    def test_non_empty_result_on_text_crop(self) -> None:
        engine = MagicMock()
        engine.__class__.__name__ = "PaddleOCR"
        engine.ocr.return_value = [
            [
                [[[0, 0], [80, 0], [80, 20], [0, 20]], ("ShelfScan", 0.92)],
            ]
        ]
        image = _make_image()
        results = recognize_text(image, engine)
        texts = [r["text"] for r in results]
        assert any(len(t) > 0 for t in texts)

    def test_raises_on_none_image(self) -> None:
        engine = MagicMock()
        with pytest.raises(ValueError, match="image"):
            recognize_text(None, engine)

    def test_raises_on_empty_image(self) -> None:
        engine = MagicMock()
        empty = np.empty((0, 0, 3), dtype=np.uint8)
        with pytest.raises(ValueError, match="image"):
            recognize_text(empty, engine)

    def test_very_small_image(self) -> None:
        """Edge case: 1x1 image should still be handled without crash."""
        engine = MagicMock()
        engine.__class__.__name__ = "PaddleOCR"
        engine.ocr.return_value = [[]]
        tiny = _make_image(height=1, width=1)
        results = recognize_text(tiny, engine)
        assert isinstance(results, list)

    def test_recognize_with_tesseract_engine(self) -> None:
        engine = MagicMock()
        engine.__class__.__module__ = "pytesseract"
        engine.__name__ = "pytesseract"
        engine.image_to_data.return_value = {
            "text": ["hello", "world", ""],
            "conf": [90, 85, -1],
        }
        image = _make_image()
        results = recognize_text(image, engine)
        assert isinstance(results, list)
        assert len(results) >= 1
        for item in results:
            assert "text" in item
            assert "confidence" in item
            assert 0.0 <= item["confidence"] <= 1.0

    def test_recognize_with_trocr_engine(self) -> None:
        mock_processor = MagicMock()
        mock_model = MagicMock()
        mock_processor.return_value = MagicMock(pixel_values=MagicMock())
        generated = MagicMock()
        mock_model.generate.return_value = generated
        mock_processor.batch_decode.return_value = ["detected text"]
        engine = {"processor": mock_processor, "model": mock_model}
        image = _make_image()
        results = recognize_text(image, engine)
        assert isinstance(results, list)
        assert len(results) >= 1
        assert results[0]["text"] == "detected text"


# ---------------------------------------------------------------------------
# compare_engines
# ---------------------------------------------------------------------------


class TestCompareEngines:
    """Tests for compare_engines."""

    @patch("src.ocr.recognize_text")
    @patch("src.ocr.init_ocr_engine")
    def test_returns_dict_with_engine_keys(
        self, mock_init: MagicMock, mock_recognize: MagicMock
    ) -> None:
        mock_init.return_value = MagicMock()
        mock_recognize.return_value = [{"text": "x", "confidence": 0.9}]
        image = _make_image()
        result = compare_engines(image, ["paddleocr", "tesseract"])
        assert isinstance(result, dict)
        assert "paddleocr" in result
        assert "tesseract" in result

    @patch("src.ocr.recognize_text")
    @patch("src.ocr.init_ocr_engine")
    def test_results_per_engine(
        self, mock_init: MagicMock, mock_recognize: MagicMock
    ) -> None:
        mock_init.return_value = MagicMock()
        mock_recognize.return_value = [{"text": "a", "confidence": 0.8}]
        image = _make_image()
        result = compare_engines(image, list(VALID_ENGINES))
        for name in VALID_ENGINES:
            assert name in result
            assert isinstance(result[name], list)

    def test_raises_on_none_image(self) -> None:
        with pytest.raises(ValueError, match="image"):
            compare_engines(None, ["paddleocr"])

    def test_raises_on_empty_image(self) -> None:
        empty = np.empty((0, 0, 3), dtype=np.uint8)
        with pytest.raises(ValueError, match="image"):
            compare_engines(empty, ["paddleocr"])
