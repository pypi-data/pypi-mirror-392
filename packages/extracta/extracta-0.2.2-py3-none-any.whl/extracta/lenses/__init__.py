import re
from pathlib import Path
from typing import Dict, Any, Optional


def get_lens_for_file(file_path: Path, semantic_mode: str = "technical"):
    """Get appropriate lens for file type

    Args:
        file_path: Path to the file
        semantic_mode: "technical" (default) or "semantic"
                      - technical: strict format-based routing
                      - semantic: user-intuitive routing (videos can be presentations)
    """
    from .document_lens import DocumentLens
    from .image_lens import ImageLens
    from .audio_lens import AudioLens
    from .video_lens import VideoLens
    from .code_lens import CodeLens
    from .presentation_lens import PresentationLens

    suffix = file_path.suffix.lower()

    # Semantic mode: allow videos to be treated as presentations
    if semantic_mode == "semantic":
        # Check if it's a presentation format (including videos)
        if suffix in PresentationLens.SUPPORTED_EXTENSIONS:
            return PresentationLens()
        elif suffix in DocumentLens.SUPPORTED_EXTENSIONS:
            return DocumentLens()
        elif suffix in ImageLens.SUPPORTED_EXTENSIONS:
            return ImageLens()
        elif suffix in AudioLens.SUPPORTED_EXTENSIONS:
            return AudioLens()
        elif suffix in CodeLens.SUPPORTED_EXTENSIONS or suffix == ".ipynb":
            return CodeLens()

    # Technical mode: strict format-based routing (default)
    else:
        # Check presentation formats first (more specific)
        if (
            suffix in PresentationLens.SUPPORTED_EXTENSIONS
            and suffix not in VideoLens.SUPPORTED_EXTENSIONS
        ):
            return PresentationLens()
        elif suffix in DocumentLens.SUPPORTED_EXTENSIONS:
            return DocumentLens()
        elif suffix in ImageLens.SUPPORTED_EXTENSIONS:
            return ImageLens()
        elif suffix in AudioLens.SUPPORTED_EXTENSIONS:
            return AudioLens()
        elif suffix in VideoLens.SUPPORTED_EXTENSIONS:
            return VideoLens()
        elif suffix in CodeLens.SUPPORTED_EXTENSIONS or suffix == ".ipynb":
            return CodeLens()

    return None


def detect_code_in_text(text: str, min_length: int = 50) -> bool:
    """
    Detect if text contains code based on heuristics

    Args:
        text: Text to analyze
        min_length: Minimum length to consider for code detection

    Returns:
        True if text likely contains code
    """
    if len(text.strip()) < min_length:
        return False

    # Code indicators
    code_indicators = [
        # Programming keywords
        r"\b(def|class|function|var|let|const|if|for|while|import|from)\b",
        # Common operators
        r"[{}();=<>!&|]",
        # File extensions in paths
        r"\.(py|js|java|cpp|html|css|sql|json|xml|yaml|yml)\b",
        # Common code patterns
        r"print\(|console\.log\(|System\.out\.|std::",
        # Indentation patterns (multiple spaces/tabs)
        r"^[ \t]{2,}",
        # Shebang lines
        r"^#!/",
    ]

    # Count how many indicators are present
    indicator_count = 0
    for pattern in code_indicators:
        if re.search(pattern, text, re.MULTILINE):
            indicator_count += 1

    # If we have multiple indicators, likely code
    return indicator_count >= 2


def analyze_extracted_content(
    extracted_data: Dict[str, Any],
    enable_cascading: bool = True,
    cascade_depth: int = 1,
) -> Dict[str, Any]:
    """
    Analyze extracted content for additional content types and cascade analysis

    Args:
        extracted_data: Data from lens extraction
        enable_cascading: Whether to enable cascading analysis
        cascade_depth: Maximum depth for cascading analysis

    Returns:
        Enhanced data with cascading analysis results
    """
    if not enable_cascading or cascade_depth <= 0:
        return extracted_data

    enhanced_data = extracted_data.copy()

    # Get text content to analyze
    text_content = _extract_text_from_data(extracted_data)
    if not text_content:
        return enhanced_data

    # Detect and analyze code content
    if detect_code_in_text(text_content):
        code_analysis = _analyze_code_content(text_content)
        if code_analysis:
            enhanced_data["cascading_analysis"] = enhanced_data.get(
                "cascading_analysis", {}
            )
            enhanced_data["cascading_analysis"]["code_detection"] = {
                "detected": True,
                "analysis": code_analysis,
            }

    return enhanced_data


def _extract_text_from_data(data: Dict[str, Any]) -> Optional[str]:
    """Extract text content from various data structures"""
    # Try different possible text fields
    text_fields = [
        "raw_content",
        "slide_text",
        "extracted_text",
        "transcript",
        "content",
    ]

    for field in text_fields:
        if field in data and isinstance(data[field], str) and data[field].strip():
            return data[field]

    # Check nested structures (like slides_content)
    if "slides_content" in data and isinstance(data["slides_content"], list):
        all_text = []
        for slide in data["slides_content"]:
            if isinstance(slide, dict) and "slide_text" in slide:
                all_text.append(slide["slide_text"])
        if all_text:
            return "\n\n".join(all_text)

    return None


def _analyze_code_content(text: str) -> Optional[Dict[str, Any]]:
    """Analyze detected code content using code lens"""
    try:
        from .code_lens import CodeLens

        # Create a temporary file-like object for analysis
        import io
        from pathlib import Path

        # Try to detect language and create appropriate file extension
        language = _detect_code_language(text)
        if language:
            # Create a temporary file path with appropriate extension
            temp_path = Path(f"temp_code.{_get_extension_for_language(language)}")

            # Extract code lens
            lens = CodeLens()
            # We'll need to modify this to work with text content directly
            # For now, return basic analysis
            return {
                "language": language,
                "confidence": "high" if language else "medium",
                "note": "Code detected in extracted content - full analysis requires file-based processing",
            }

    except Exception as e:
        return {"error": f"Code analysis failed: {str(e)}", "language": "unknown"}

    return None


def _detect_code_language(text: str) -> Optional[str]:
    """Simple language detection based on keywords and patterns"""
    text_lower = text.lower()

    # Language detection patterns
    patterns = {
        "python": [r"\bdef\b", r"\bimport\b", r"\bclass\b", r"\bif __name__"],
        "javascript": [
            r"\bfunction\b",
            r"\bvar\b",
            r"\bconst\b",
            r"\blet\b",
            r"console\.",
        ],
        "java": [r"\bpublic class\b", r"\bSystem\.out\b", r"\bimport java\b"],
        "cpp": [r"\b#include\b", r"\bint main\b", r"\bcout\b", r"\bcin\b"],
        "html": [r"<html>", r"<body>", r"<div>", r"<script>"],
        "css": [r"\{[^}]*\}", r"\.class\s*\{", r"#id\s*\{"],
        "sql": [r"\bSELECT\b", r"\bFROM\b", r"\bWHERE\b", r"\bINSERT\b"],
        "json": [r"\{.*\}", r'".*":', r"\[.*\]"],
    }

    scores = {}
    for lang, lang_patterns in patterns.items():
        score = 0
        for pattern in lang_patterns:
            if re.search(pattern, text_lower):
                score += 1
        if score > 0:
            scores[lang] = score

    if scores:
        return max(scores, key=lambda k: scores[k])

    return None


def _get_extension_for_language(language: str) -> str:
    """Get file extension for detected language"""
    extensions = {
        "python": "py",
        "javascript": "js",
        "java": "java",
        "cpp": "cpp",
        "html": "html",
        "css": "css",
        "sql": "sql",
        "json": "json",
    }
    return extensions.get(language, "txt")
