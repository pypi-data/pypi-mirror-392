from PIL import Image
import os
from typing import Dict, Any


class ImageAnalyzer:
    """Basic image analysis for assessment purposes"""

    def analyze(self, image_path: str, mode: str = "assessment") -> Dict[str, Any]:
        """Analyze image file"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                file_size = os.path.getsize(image_path)

                analysis = {
                    "dimensions": {
                        "width": width,
                        "height": height,
                        "aspect_ratio": width / height if height > 0 else 0,
                    },
                    "file_info": {
                        "size_bytes": file_size,
                        "format": img.format,
                        "mode": img.mode,
                    },
                    "basic_stats": {
                        "has_alpha": "A" in img.mode,
                        "is_grayscale": img.mode in ("L", "P"),
                        "is_rgb": img.mode in ("RGB", "RGBA"),
                    },
                }

                # Add assessment-specific metrics
                if mode == "assessment":
                    analysis["assessment"] = self._assessment_analysis(img)
                elif mode == "research":
                    analysis["research"] = self._research_analysis(img)

                return analysis

        except Exception as e:
            return {"error": str(e)}

    def _assessment_analysis(self, img: Image.Image) -> Dict[str, Any]:
        """Assessment-focused analysis"""
        # Basic quality checks
        width, height = img.size

        # Check for common issues
        issues = []
        if width < 100 or height < 100:
            issues.append("Image dimensions too small")
        if img.mode not in ("RGB", "RGBA", "L"):
            issues.append("Unusual color mode")

        return {
            "quality_issues": issues,
            "resolution_category": self._categorize_resolution(width, height),
            "color_depth": self._get_color_depth(img.mode),
        }

    def _research_analysis(self, img: Image.Image) -> Dict[str, Any]:
        """Research-focused analysis"""
        # Placeholder for more advanced analysis
        return {"image_type": "raster", "potential_use": "visual_analysis"}

    def _categorize_resolution(self, width: int, height: int) -> str:
        """Categorize image resolution"""
        pixels = width * height
        if pixels < 10000:
            return "thumbnail"
        elif pixels < 100000:
            return "low"
        elif pixels < 1000000:
            return "medium"
        elif pixels < 5000000:
            return "high"
        else:
            return "ultra_high"

    def _get_color_depth(self, mode: str) -> int:
        """Get color depth in bits"""
        depths = {
            "1": 1,  # 1-bit pixels, black and white
            "L": 8,  # 8-bit pixels, grayscale
            "P": 8,  # 8-bit pixels, mapped to any other mode using a color palette
            "RGB": 24,  # 3x8-bit pixels, true color
            "RGBA": 32,  # 4x8-bit pixels, true color with transparency mask
            "CMYK": 32,  # 4x8-bit pixels, color separation
            "YCbCr": 24,  # 3x8-bit pixels, color video format
            "I": 32,  # 32-bit signed integer pixels
            "F": 32,  # 32-bit floating point pixels
        }
        return depths.get(mode, 0)
