from pathlib import Path
from typing import Dict, Any
from ..base_lens import BaseLens


class ImageLens(BaseLens):
    """Lens for extracting content from image files"""

    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}

    def __init__(self, enable_ocr: bool = True):
        """Initialize image lens with OCR capability."""
        self.enable_ocr = enable_ocr
        self.ocr_detector = None
        if enable_ocr:
            self._initialize_ocr()

    def _initialize_ocr(self):
        """Initialize OCR detector if available."""
        try:
            from ..ocr_detector import OCRDetector

            self.ocr_detector = OCRDetector()
        except ImportError:
            # OCR not available, continue without it
            pass

    def extract(self, file_path: Path) -> Dict[str, Any]:
        """Extract content from image file"""
        try:
            if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {file_path.suffix}",
                    "data": {},
                }

            data = {
                "content_type": "image",
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
            }

            # Extract OCR text if available
            if self.ocr_detector:
                try:
                    ocr_result = self.ocr_detector.detect_text(image_path=file_path)
                    data["ocr_text"] = ocr_result.full_text
                    data["ocr_regions"] = len(ocr_result.text_regions)
                    data["ocr_confidence"] = ocr_result.average_confidence

                    # Apply cascading analysis for code detection in OCR text
                    if ocr_result.full_text.strip():
                        from .. import analyze_extracted_content

                        ocr_data = {"raw_content": ocr_result.full_text}
                        enhanced_ocr = analyze_extracted_content(ocr_data)
                        if "cascading_analysis" in enhanced_ocr:
                            data["ocr_cascading_analysis"] = enhanced_ocr[
                                "cascading_analysis"
                            ]

                except Exception as e:
                    # OCR failed, but don't fail the whole extraction
                    data["ocr_error"] = str(e)

            return {"success": True, "data": data}

        except Exception as e:
            return {"success": False, "error": str(e), "data": {}}

            return {
                "success": True,
                "data": {
                    "content_type": "image",
                    "file_path": str(file_path),
                    "file_size": file_path.stat().st_size,
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e), "data": {}}
