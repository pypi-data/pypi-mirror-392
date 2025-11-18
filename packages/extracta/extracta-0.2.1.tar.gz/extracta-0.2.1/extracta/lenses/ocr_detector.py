"""Simple OCR functionality for text detection in images."""

import logging
from pathlib import Path
from typing import Any, List, Dict

from PIL import Image

try:
    import pytesseract

    _tesseract_available = True
except ImportError:
    _tesseract_available = False
    pytesseract = None

logger = logging.getLogger(__name__)


class TextRegion:
    """Detected text region with position and content."""

    def __init__(self, text: str, confidence: float, bbox: tuple[int, int, int, int]):
        self.text = text
        self.confidence = confidence
        self.bbox = bbox


class OCRResult:
    """Result of OCR operation on an image."""

    def __init__(self, text_regions: List[TextRegion], processing_time: float):
        self.text_regions = text_regions
        self.full_text = " ".join([region.text for region in text_regions])
        self.processing_time = processing_time
        self.total_text_regions = len(text_regions)
        self.average_confidence = (
            sum(region.confidence for region in text_regions) / len(text_regions)
            if text_regions
            else 0.0
        )


class OCRDetector:
    """Simple OCR text detection using Tesseract."""

    def __init__(self):
        """Initialize OCR detector."""
        if not _tesseract_available:
            raise ImportError(
                "Tesseract OCR not available. Install with: pip install pytesseract"
            )

        # Basic configuration
        self.languages = ["eng"]
        self.confidence_threshold = 30.0
        self.min_text_length = 1

    def detect_text(
        self, image_path: Path | None = None, pil_image: Image.Image | None = None
    ) -> OCRResult:
        """Detect text in an image."""
        import time

        start_time = time.time()

        if image_path:
            image = Image.open(image_path)
        elif pil_image:
            image = pil_image
        else:
            raise ValueError("Must provide image_path or pil_image")

        # Perform OCR
        text_regions = self._detect_text_tesseract(image)

        # Filter regions
        filtered_regions = self._filter_text_regions(text_regions)

        processing_time = time.time() - start_time

        return OCRResult(filtered_regions, processing_time)

    def _detect_text_tesseract(self, image: Image.Image) -> List[TextRegion]:
        """Detect text using Tesseract OCR."""
        text_regions: List[TextRegion] = []

        try:
            # Get detailed OCR data
            data = pytesseract.image_to_data(
                image,
                config="--oem 3 --psm 6",
                output_type=pytesseract.Output.DICT,
            )

            n_boxes = len(data["level"])
            for i in range(n_boxes):
                conf_value = data["conf"][i]
                confidence = (
                    float(conf_value) if conf_value not in (None, "", -1) else -1.0
                )
                text = str(data["text"][i]).strip()

                if confidence < 0 or not text:
                    continue

                # Extract bounding box
                x = int(data["left"][i])
                y = int(data["top"][i])
                w = int(data["width"][i])
                h = int(data["height"][i])

                text_region = TextRegion(text, confidence, (x, y, w, h))
                text_regions.append(text_region)

        except Exception as e:
            logger.warning(f"Tesseract OCR failed: {e}")

        return text_regions

    def _filter_text_regions(self, text_regions: List[TextRegion]) -> List[TextRegion]:
        """Filter text regions by confidence and length."""
        filtered: List[TextRegion] = []

        for region in text_regions:
            # Filter by confidence threshold
            if region.confidence < self.confidence_threshold:
                continue

            # Filter by minimum text length
            if len(region.text) < self.min_text_length:
                continue

            # Skip pure whitespace or non-printable characters
            if not region.text.strip() or not any(c.isprintable() for c in region.text):
                continue

            filtered.append(region)

        return filtered
