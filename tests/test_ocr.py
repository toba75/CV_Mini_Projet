"""Tests for OCR module — TDD RED phase for task #005."""

import logging
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.ocr import (
    DEFAULT_FALLBACK_CONFIDENCE_THRESHOLD,
    compare_engines,
    init_ocr_engine,
    recognize_batch,
    recognize_batch_with_fallback,
    recognize_text,
    recognize_text_unified,
    recognize_with_fallback,
)

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

    def test_recognize_text_does_not_modify_input(self) -> None:
        """Verify that recognize_text does not alter the original image (§R4)."""
        engine = MagicMock()
        engine.__class__.__name__ = "PaddleOCR"
        engine.ocr.return_value = [
            [
                [[[0, 0], [100, 0], [100, 30], [0, 30]], ("hello", 0.95)],
            ]
        ]
        image = _make_image()
        original = image.copy()
        recognize_text(image, engine)
        np.testing.assert_array_equal(image, original)

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


# ---------------------------------------------------------------------------
# recognize_text_unified
# ---------------------------------------------------------------------------


class TestRecognizeTextUnified:
    """Tests for recognize_text_unified."""

    @patch("src.ocr.recognize_text")
    @patch("src.ocr.init_ocr_engine")
    def test_returns_dict_with_expected_keys(
        self, mock_init: MagicMock, mock_recognize: MagicMock
    ) -> None:
        mock_init.return_value = MagicMock()
        mock_recognize.return_value = [
            {"text": "hello", "confidence": 0.95},
        ]
        image = _make_image()
        result = recognize_text_unified(image, engine="paddleocr")
        assert isinstance(result, dict)
        assert "text" in result
        assert "confidence" in result
        assert "engine" in result
        assert isinstance(result["text"], str)
        assert isinstance(result["confidence"], float)
        assert result["engine"] == "paddleocr"

    @patch("src.ocr.recognize_text")
    @patch("src.ocr.init_ocr_engine")
    def test_concatenates_multiple_results(
        self, mock_init: MagicMock, mock_recognize: MagicMock
    ) -> None:
        mock_init.return_value = MagicMock()
        mock_recognize.return_value = [
            {"text": "hello", "confidence": 0.9},
            {"text": "world", "confidence": 0.8},
        ]
        image = _make_image()
        result = recognize_text_unified(image, engine="paddleocr")
        assert "hello" in result["text"]
        assert "world" in result["text"]

    @patch("src.ocr.recognize_text")
    @patch("src.ocr.init_ocr_engine")
    def test_empty_result_when_no_text(
        self, mock_init: MagicMock, mock_recognize: MagicMock
    ) -> None:
        mock_init.return_value = MagicMock()
        mock_recognize.return_value = []
        image = _make_image()
        result = recognize_text_unified(image, engine="paddleocr")
        assert result["text"] == ""
        assert result["confidence"] == 0.0
        assert result["engine"] == "paddleocr"

    def test_unknown_engine_raises(self) -> None:
        image = _make_image()
        with pytest.raises(ValueError):
            recognize_text_unified(image, engine="unknown_engine")

    def test_none_image_raises(self) -> None:
        with pytest.raises(ValueError):
            recognize_text_unified(None, engine="paddleocr")

    @patch("src.ocr.recognize_text")
    @patch("src.ocr.init_ocr_engine")
    def test_engine_key_matches_argument(
        self, mock_init: MagicMock, mock_recognize: MagicMock
    ) -> None:
        mock_init.return_value = MagicMock()
        mock_recognize.return_value = [{"text": "x", "confidence": 0.5}]
        image = _make_image()
        result = recognize_text_unified(image, engine="tesseract")
        assert result["engine"] == "tesseract"


# ---------------------------------------------------------------------------
# recognize_batch
# ---------------------------------------------------------------------------


class TestRecognizeBatch:
    """Tests for recognize_batch."""

    @patch("src.ocr.recognize_text")
    @patch("src.ocr.init_ocr_engine")
    def test_returns_list_of_dicts(
        self, mock_init: MagicMock, mock_recognize: MagicMock
    ) -> None:
        mock_init.return_value = MagicMock()
        mock_recognize.return_value = [{"text": "hi", "confidence": 0.9}]
        crops = [_make_image(), _make_image()]
        results = recognize_batch(crops, engine="paddleocr")
        assert isinstance(results, list)
        assert len(results) == 2
        for r in results:
            assert isinstance(r, dict)
            assert "text" in r
            assert "confidence" in r
            assert "engine" in r

    @patch("src.ocr.recognize_text")
    @patch("src.ocr.init_ocr_engine")
    def test_empty_list_returns_empty(
        self, mock_init: MagicMock, mock_recognize: MagicMock
    ) -> None:
        mock_init.return_value = MagicMock()
        results = recognize_batch([], engine="paddleocr")
        assert results == []

    @patch("src.ocr.recognize_text")
    @patch("src.ocr.init_ocr_engine")
    def test_none_image_in_list_raises(
        self, mock_init: MagicMock, mock_recognize: MagicMock
    ) -> None:
        mock_init.return_value = MagicMock()
        mock_recognize.side_effect = ValueError("image must not be None")
        with pytest.raises(ValueError):
            recognize_batch([None], engine="paddleocr")

    @patch("src.ocr.recognize_text")
    @patch("src.ocr.init_ocr_engine")
    def test_engine_initialized_once(
        self, mock_init: MagicMock, mock_recognize: MagicMock
    ) -> None:
        """Engine should be initialized only once for all crops."""
        mock_init.return_value = MagicMock()
        mock_recognize.return_value = [{"text": "a", "confidence": 0.9}]
        crops = [_make_image(), _make_image(), _make_image()]
        recognize_batch(crops, engine="paddleocr")
        mock_init.assert_called_once()


# ---------------------------------------------------------------------------
# DEFAULT_FALLBACK_CONFIDENCE_THRESHOLD
# ---------------------------------------------------------------------------


class TestDefaultFallbackConfidenceThreshold:
    """Tests for the DEFAULT_FALLBACK_CONFIDENCE_THRESHOLD constant."""

    def test_is_float(self) -> None:
        assert isinstance(DEFAULT_FALLBACK_CONFIDENCE_THRESHOLD, float)

    def test_value(self) -> None:
        assert DEFAULT_FALLBACK_CONFIDENCE_THRESHOLD == pytest.approx(0.3)


# ---------------------------------------------------------------------------
# recognize_with_fallback
# ---------------------------------------------------------------------------


class TestRecognizeWithFallback:
    """Tests for recognize_with_fallback."""

    @patch("src.ocr.recognize_text")
    @patch("src.ocr.init_ocr_engine")
    def test_first_engine_above_threshold_returns_immediately(
        self, mock_init: MagicMock, mock_recognize: MagicMock
    ) -> None:
        """When the first engine gives high confidence, no fallback needed."""
        mock_init.return_value = MagicMock()
        mock_recognize.return_value = [{"text": "hello", "confidence": 0.9}]
        image = _make_image()
        result = recognize_with_fallback(image, ["paddleocr", "tesseract"])
        assert result["engine_used"] == "paddleocr"
        assert result["engines_tried"] == ["paddleocr"]
        assert result["text"] == "hello"
        assert result["confidence"] == pytest.approx(0.9)
        # init_ocr_engine called only once (no fallback)
        mock_init.assert_called_once_with("paddleocr")

    @patch("src.ocr.recognize_text")
    @patch("src.ocr.init_ocr_engine")
    def test_fallback_to_second_engine(
        self, mock_init: MagicMock, mock_recognize: MagicMock
    ) -> None:
        """When the first engine gives low confidence, try second."""
        mock_init.return_value = MagicMock()
        # First call: low confidence; second call: high confidence
        mock_recognize.side_effect = [
            [{"text": "lo", "confidence": 0.1}],
            [{"text": "hello world", "confidence": 0.85}],
        ]
        image = _make_image()
        result = recognize_with_fallback(
            image, ["paddleocr", "tesseract"], confidence_threshold=0.3
        )
        assert result["engine_used"] == "tesseract"
        assert result["engines_tried"] == ["paddleocr", "tesseract"]
        assert result["text"] == "hello world"
        assert result["confidence"] == pytest.approx(0.85)

    @patch("src.ocr.recognize_text")
    @patch("src.ocr.init_ocr_engine")
    def test_all_below_threshold_returns_best(
        self, mock_init: MagicMock, mock_recognize: MagicMock
    ) -> None:
        """When all engines are below threshold, return the best result."""
        mock_init.return_value = MagicMock()
        mock_recognize.side_effect = [
            [{"text": "a", "confidence": 0.1}],
            [{"text": "ab", "confidence": 0.25}],
            [{"text": "abc", "confidence": 0.2}],
        ]
        image = _make_image()
        result = recognize_with_fallback(
            image,
            ["paddleocr", "trocr", "tesseract"],
            confidence_threshold=0.5,
        )
        # Best confidence is 0.25 from trocr
        assert result["engine_used"] == "trocr"
        assert result["engines_tried"] == ["paddleocr", "trocr", "tesseract"]
        assert result["text"] == "ab"
        assert result["confidence"] == pytest.approx(0.25)

    def test_empty_engines_raises(self) -> None:
        """Empty engines list must raise ValueError."""
        image = _make_image()
        with pytest.raises(ValueError, match="engines"):
            recognize_with_fallback(image, [])

    def test_unsupported_engine_raises(self) -> None:
        """Unsupported engine name must raise ValueError."""
        image = _make_image()
        with pytest.raises(ValueError, match="not_an_engine"):
            recognize_with_fallback(image, ["not_an_engine"])

    def test_none_image_raises(self) -> None:
        with pytest.raises(ValueError, match="image"):
            recognize_with_fallback(None, ["paddleocr"])

    @patch("src.ocr.recognize_text")
    @patch("src.ocr.init_ocr_engine")
    def test_uses_default_threshold(
        self, mock_init: MagicMock, mock_recognize: MagicMock
    ) -> None:
        """Default threshold should be DEFAULT_FALLBACK_CONFIDENCE_THRESHOLD."""
        mock_init.return_value = MagicMock()
        # Confidence 0.25 < default threshold 0.3 => fallback
        mock_recognize.side_effect = [
            [{"text": "x", "confidence": 0.25}],
            [{"text": "y", "confidence": 0.9}],
        ]
        image = _make_image()
        result = recognize_with_fallback(image, ["paddleocr", "tesseract"])
        assert result["engine_used"] == "tesseract"

    @patch("src.ocr.recognize_text")
    @patch("src.ocr.init_ocr_engine")
    def test_logging_engine_used(
        self, mock_init: MagicMock, mock_recognize: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """The engine used should be logged."""
        mock_init.return_value = MagicMock()
        mock_recognize.return_value = [{"text": "ok", "confidence": 0.9}]
        image = _make_image()
        with caplog.at_level(logging.INFO, logger="src.ocr"):
            recognize_with_fallback(image, ["paddleocr"])
        assert any("paddleocr" in msg.lower() for msg in caplog.messages)

    @patch("src.ocr.recognize_text")
    @patch("src.ocr.init_ocr_engine")
    def test_empty_ocr_result_treated_as_zero_confidence(
        self, mock_init: MagicMock, mock_recognize: MagicMock
    ) -> None:
        """Engine returning no results should be treated as 0 confidence."""
        mock_init.return_value = MagicMock()
        mock_recognize.side_effect = [
            [],  # No results from first engine
            [{"text": "found", "confidence": 0.8}],
        ]
        image = _make_image()
        result = recognize_with_fallback(image, ["paddleocr", "tesseract"])
        assert result["engine_used"] == "tesseract"
        assert result["text"] == "found"

    @patch("src.ocr.recognize_text")
    @patch("src.ocr.init_ocr_engine")
    def test_single_engine_returns_result(
        self, mock_init: MagicMock, mock_recognize: MagicMock
    ) -> None:
        """Single engine should return its result regardless of confidence."""
        mock_init.return_value = MagicMock()
        mock_recognize.return_value = [{"text": "low", "confidence": 0.1}]
        image = _make_image()
        result = recognize_with_fallback(image, ["paddleocr"])
        assert result["engine_used"] == "paddleocr"
        assert result["engines_tried"] == ["paddleocr"]


# ---------------------------------------------------------------------------
# recognize_batch_with_fallback
# ---------------------------------------------------------------------------


class TestRecognizeBatchWithFallback:
    """Tests for recognize_batch_with_fallback."""

    @patch("src.ocr.recognize_with_fallback")
    def test_returns_list_of_results(
        self, mock_fallback: MagicMock
    ) -> None:
        mock_fallback.return_value = {
            "text": "ok",
            "confidence": 0.9,
            "engine_used": "paddleocr",
            "engines_tried": ["paddleocr"],
        }
        crops = [_make_image(), _make_image()]
        results = recognize_batch_with_fallback(crops, ["paddleocr", "tesseract"])
        assert isinstance(results, list)
        assert len(results) == 2

    @patch("src.ocr.recognize_with_fallback")
    def test_empty_crops_returns_empty(
        self, mock_fallback: MagicMock
    ) -> None:
        results = recognize_batch_with_fallback([], ["paddleocr"])
        assert results == []
        mock_fallback.assert_not_called()

    def test_empty_engines_raises(self) -> None:
        with pytest.raises(ValueError, match="engines"):
            recognize_batch_with_fallback([_make_image()], [])

    def test_unsupported_engine_raises(self) -> None:
        with pytest.raises(ValueError, match="bad_engine"):
            recognize_batch_with_fallback([_make_image()], ["bad_engine"])

    @patch("src.ocr.recognize_with_fallback")
    def test_passes_threshold(
        self, mock_fallback: MagicMock
    ) -> None:
        mock_fallback.return_value = {
            "text": "x",
            "confidence": 0.5,
            "engine_used": "paddleocr",
            "engines_tried": ["paddleocr"],
        }
        crops = [_make_image()]
        recognize_batch_with_fallback(
            crops, ["paddleocr"], confidence_threshold=0.7
        )
        mock_fallback.assert_called_once()
        call_kwargs = mock_fallback.call_args.kwargs
        assert call_kwargs["confidence_threshold"] == pytest.approx(0.7)
