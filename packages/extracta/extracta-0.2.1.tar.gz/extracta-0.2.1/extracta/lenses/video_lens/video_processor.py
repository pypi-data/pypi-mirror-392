"""Video processing pipeline for extracta."""

import logging
import os
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import ffmpeg
from pydantic import BaseModel

from .exceptions import (
    ErrorCode,
    FileValidationError,
    FrameExtractionError,
    VideoProcessingError,
    handle_ffmpeg_error,
)
from ...shared.config import get_config

logger = logging.getLogger(__name__)


class VideoInfo(BaseModel):
    """Video metadata information."""

    file_path: Path
    duration: float
    width: int
    height: int
    fps: float
    format: str
    size_mb: float
    codec: str


class FrameInfo(BaseModel):
    """Frame extraction metadata."""

    frame_path: Path
    timestamp: float
    scene_number: int
    width: int
    height: int
    size_kb: float
    format: str = "jpg"


class VideoProcessor:
    """Main video processing class with file validation and format support."""

    def __init__(self):
        """Initialize VideoProcessor with configuration."""
        self.config = config or get_config()
        self.supported_formats = self.config.processing.supported_video_formats
        self.max_video_size_mb = self.config.processing.max_video_size_mb
        self.temp_dir = Path(self.config.processing.temp_dir) / "video"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"VideoProcessor initialized with formats: {self.supported_formats}"
        )

    def validate_file(self, file_path: Path | str) -> VideoInfo:
        """
        Validate video file format, size, and accessibility.

        Args:
            file_path: Path to video file

        Returns:
            VideoInfo object with file metadata

        Raises:
            FileValidationError: For all file validation issues
        """
        file_path = Path(file_path)

        try:
            # Check if file exists
            if not file_path.exists():
                raise FileValidationError(
                    message=f"Video file not found: {file_path.name}",
                    file_path=file_path,
                    error_code=ErrorCode.FILE_NOT_FOUND,
                )

            # Check file extension
            file_extension = file_path.suffix.lower().lstrip(".")
            if file_extension not in self.supported_formats:
                raise FileValidationError(
                    message=f"Unsupported video format '.{file_extension}'",
                    file_path=file_path,
                    error_code=ErrorCode.INVALID_FORMAT,
                    details={
                        "detected_format": file_extension,
                        "supported_formats": self.supported_formats,
                    },
                )

            # Check file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.max_video_size_mb:
                raise FileValidationError(
                    message=f"Video file is too large ({file_size_mb:.1f}MB)",
                    file_path=file_path,
                    error_code=ErrorCode.FILE_TOO_LARGE,
                    details={
                        "file_size_mb": file_size_mb,
                        "max_size_mb": self.max_video_size_mb,
                    },
                )

            # Probe video file with ffmpeg
            try:
                probe = ffmpeg.probe(str(file_path))
            except ffmpeg.Error as e:
                raise handle_ffmpeg_error(e, "probe", file_path) from e

            # Validate probe results
            if not probe or "streams" not in probe:
                raise FileValidationError(
                    message=f"Invalid video file structure: {file_path.name}",
                    file_path=file_path,
                    error_code=ErrorCode.FILE_CORRUPTED,
                )

            # Find video stream
            video_stream = None
            for stream in probe["streams"]:
                if stream["codec_type"] == "video":
                    video_stream = stream
                    break

            if not video_stream:
                raise FileValidationError(
                    message=f"No video stream found in file: {file_path.name}",
                    file_path=file_path,
                    error_code=ErrorCode.NO_VIDEO_STREAM,
                )

            # Extract metadata
            duration = float(probe["format"]["duration"])
            width = int(video_stream["width"])
            height = int(video_stream["height"])

            # Calculate FPS
            fps_str = video_stream.get("r_frame_rate", "0/1")
            if "/" in fps_str:
                num, den = fps_str.split("/")
                fps = float(num) / float(den) if float(den) != 0 else 0
            else:
                fps = float(fps_str)

            format_name = probe["format"]["format_name"]
            codec = video_stream["codec_name"]

            logger.info(
                f"Video validated: {file_path.name} ({duration:.1f}s, {width}x{height}, {fps:.1f}fps)"
            )

            return VideoInfo(
                file_path=file_path,
                duration=duration,
                width=width,
                height=height,
                fps=fps,
                format=format_name,
                size_mb=file_size_mb,
                codec=codec,
            )

        except VideoProcessingError:
            raise
        except Exception as e:
            raise VideoProcessingError(
                message=f"Unexpected error validating video file: {file_path.name}",
                error_code=ErrorCode.UNKNOWN_ERROR,
                file_path=file_path,
                cause=e,
            ) from e

    def extract_frame_at_timestamp(
        self,
        video_info: VideoInfo,
        timestamp: float,
        output_path: Path,
        quality: int = 80,
    ) -> FrameInfo:
        """
        Extract a frame at a specific timestamp.

        Args:
            video_info: VideoInfo object from validated video file
            timestamp: Time in seconds to extract frame
            output_path: Path to save the extracted frame
            quality: JPEG quality (1-100)

        Returns:
            FrameInfo object with extracted frame metadata

        Raises:
            FrameExtractionError: If frame extraction fails
        """
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Build ffmpeg command
            stream = ffmpeg.input(str(video_info.file_path), ss=timestamp)
            stream = ffmpeg.output(
                stream,
                str(output_path),
                vframes=1,
                **{"q:v": quality},  # Quality setting
                f="image2",
            )
            stream = ffmpeg.overwrite_output(stream)

            # Execute extraction
            ffmpeg.run(stream, quiet=True, capture_stdout=True, capture_stderr=True)

            # Verify output file
            if not output_path.exists():
                raise FrameExtractionError(
                    message="Frame extraction completed but output file not found",
                    timestamp=timestamp,
                    file_path=video_info.file_path,
                )

            file_size_kb = output_path.stat().st_size / 1024

            return FrameInfo(
                frame_path=output_path,
                timestamp=timestamp,
                scene_number=0,  # Not scene-based
                width=video_info.width,
                height=video_info.height,
                size_kb=file_size_kb,
                format="jpg",
            )

        except ffmpeg.Error as e:
            raise handle_ffmpeg_error(
                e, "frame extraction", video_info.file_path
            ) from e
        except Exception as e:
            raise FrameExtractionError(
                message=f"Unexpected error during frame extraction: {str(e)}",
                timestamp=timestamp,
                file_path=video_info.file_path,
                cause=e,
            ) from e

    def extract_audio(
        self,
        video_info: VideoInfo,
        output_path: Path,
    ) -> Path:
        """
        Extract audio from video file.

        Args:
            video_info: VideoInfo object from validated video file
            output_path: Path to save the extracted audio

        Returns:
            Path to the extracted audio file

        Raises:
            AudioProcessingError: If audio extraction fails
        """
        from .exceptions import AudioProcessingError

        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Extract audio using ffmpeg
            stream = ffmpeg.input(str(video_info.file_path))
            stream = ffmpeg.output(
                stream,
                str(output_path),
                acodec="mp3",  # Convert to MP3
                ab="128k",  # 128kbps bitrate
                f="mp3",
            )
            stream = ffmpeg.overwrite_output(stream)

            # Execute extraction
            ffmpeg.run(stream, quiet=True, capture_stdout=True, capture_stderr=True)

            if not output_path.exists():
                raise AudioProcessingError(
                    message="Audio extraction completed but output file not found",
                    file_path=video_info.file_path,
                )

            return output_path

        except ffmpeg.Error as e:
            from .exceptions import handle_ffmpeg_error

            raise handle_ffmpeg_error(
                e, "audio extraction", video_info.file_path
            ) from e
        except Exception as e:
            raise AudioProcessingError(
                message=f"Unexpected error during audio extraction: {str(e)}",
                file_path=video_info.file_path,
                cause=e,
            ) from e

    def is_format_supported(self, file_path: Path | str) -> bool:
        """Check if video file format is supported."""
        file_path = Path(file_path)
        file_extension = file_path.suffix.lower().lstrip(".")
        return file_extension in self.supported_formats

    def get_supported_formats(self) -> list[str]:
        """Get list of supported video formats."""
        return self.supported_formats.copy()
