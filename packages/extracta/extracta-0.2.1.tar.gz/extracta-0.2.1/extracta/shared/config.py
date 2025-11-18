"""Configuration system for extracta."""

import os
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel, Field


class ProcessingConfig(BaseModel):
    """Configuration for content processing."""

    max_video_size_mb: int = Field(
        default=500, description="Maximum video file size in MB"
    )
    max_image_size_mb: int = Field(
        default=50, description="Maximum image file size in MB"
    )
    supported_video_formats: list[str] = Field(
        default=["mp4", "mov", "avi", "webm", "mkv", "flv", "wmv", "m4v"],
        description="Supported video formats",
    )
    supported_image_formats: list[str] = Field(
        default=["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"],
        description="Supported image formats",
    )
    supported_document_formats: list[str] = Field(
        default=["txt", "md", "rst"], description="Supported document formats"
    )
    temp_dir: str = Field(
        default="/tmp/extracta", description="Temporary directory for processing"
    )
    cleanup_temp_files: bool = Field(
        default=True, description="Clean up temporary files after processing"
    )


class AnalysisConfig(BaseModel):
    """Configuration for content analysis."""

    target_wpm_range: tuple[int, int] = Field(
        default=(120, 180), description="Target words per minute range"
    )
    confidence_threshold: float = Field(
        default=0.7, description="Confidence threshold for analysis"
    )
    ocr_confidence_threshold: float = Field(
        default=30.0, description="OCR confidence threshold"
    )
    ocr_text_min_length: int = Field(default=1, description="Minimum OCR text length")
    ocr_languages: list[str] = Field(default=["eng"], description="OCR languages")
    enable_ocr: bool = Field(default=True, description="Enable OCR processing")


class OutputConfig(BaseModel):
    """Configuration for output generation."""

    frame_quality: int = Field(
        default=80, description="Frame extraction quality (1-100)"
    )
    max_frame_width: int | None = Field(
        default=None, description="Maximum frame width for scaling"
    )


class ExtractaConfig(BaseModel):
    """Main configuration for extracta."""

    app_name: str = Field(default="Extracta", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")

    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)


def get_config() -> ExtractaConfig:
    """Get the default configuration."""
    return ExtractaConfig()


def load_config(config_file: Path | str | None = None) -> ExtractaConfig:
    """Load configuration from file or environment."""
    config = ExtractaConfig()

    # Override with environment variables if present
    if os.getenv("EXTRACTA_DEBUG"):
        config.debug = os.getenv("EXTRACTA_DEBUG").lower() in ("true", "1", "yes")

    if os.getenv("EXTRACTA_MAX_VIDEO_SIZE_MB"):
        config.processing.max_video_size_mb = int(
            os.getenv("EXTRACTA_MAX_VIDEO_SIZE_MB")
        )

    return config
