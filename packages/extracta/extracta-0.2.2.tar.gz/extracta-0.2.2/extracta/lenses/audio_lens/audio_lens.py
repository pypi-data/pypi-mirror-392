"""Audio processing lens for extracta."""

import logging
from pathlib import Path
from typing import Dict, Any

import ffmpeg

from ..base_lens import BaseLens
from ...shared.config import get_config

logger = logging.getLogger(__name__)


class AudioInfo:
    """Audio metadata information."""

    def __init__(
        self,
        file_path: Path,
        duration: float,
        sample_rate: int,
        channels: int,
        format: str,
        size_mb: float,
    ):
        self.file_path = file_path
        self.duration = duration
        self.sample_rate = sample_rate
        self.channels = channels
        self.format = format
        self.size_mb = size_mb


class AudioLens(BaseLens):
    """Lens for extracting and processing audio files."""

    SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"}

    def __init__(self):
        """Initialize audio lens."""
        self.config = get_config()

    def extract(self, file_path: Path) -> Dict[str, Any]:
        """Extract audio information and prepare for analysis."""
        try:
            if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                return {
                    "success": False,
                    "error": f"Unsupported audio format: {file_path.suffix}",
                    "data": {},
                }

            # Get audio info
            audio_info = self._get_audio_info(file_path)

            return {
                "success": True,
                "data": {
                    "content_type": "audio",
                    "file_path": str(file_path),
                    "file_size": file_path.stat().st_size,
                    "audio_info": {
                        "duration": audio_info.duration,
                        "sample_rate": audio_info.sample_rate,
                        "channels": audio_info.channels,
                        "format": audio_info.format,
                    },
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e), "data": {}}

    def _get_audio_info(self, file_path: Path) -> AudioInfo:
        """Get audio file information using ffmpeg."""
        try:
            probe = ffmpeg.probe(str(file_path))

            # Find audio stream
            audio_stream = None
            for stream in probe["streams"]:
                if stream["codec_type"] == "audio":
                    audio_stream = stream
                    break

            if not audio_stream:
                raise ValueError("No audio stream found")

            duration = float(probe["format"]["duration"])
            sample_rate = int(audio_stream["sample_rate"])
            channels = int(audio_stream.get("channels", 1))
            format_name = probe["format"]["format_name"]
            size_mb = file_path.stat().st_size / (1024 * 1024)

            return AudioInfo(
                file_path, duration, sample_rate, channels, format_name, size_mb
            )

        except ffmpeg.Error as e:
            raise RuntimeError(f"Failed to probe audio file: {e}") from e

    def prepare_audio_for_transcription(
        self, audio_path: Path, output_path: Path
    ) -> Path:
        """Prepare audio file for transcription (convert to optimal format)."""
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to WAV for better transcription compatibility
            stream = ffmpeg.input(str(audio_path))
            stream = ffmpeg.output(
                stream,
                str(output_path),
                acodec="pcm_s16le",  # 16-bit PCM
                ar="16000",  # 16kHz sample rate (good for speech)
                ac=1,  # Mono
                f="wav",
            )
            stream = ffmpeg.overwrite_output(stream)

            # Execute conversion
            ffmpeg.run(stream, quiet=True, capture_stdout=True, capture_stderr=True)

            if not output_path.exists():
                raise RuntimeError("Audio preparation failed - output file not created")

            return output_path

        except ffmpeg.Error as e:
            raise RuntimeError(f"Audio preparation failed: {e}") from e

    def prepare_for_transcription(self, audio_path: Path, output_path: Path) -> Path:
        """Prepare audio file for transcription (convert to WAV format)."""
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to WAV for better transcription compatibility
            stream = ffmpeg.input(str(audio_path))
            stream = ffmpeg.output(
                stream,
                str(output_path),
                acodec="pcm_s16le",  # 16-bit PCM
                ar="16000",  # 16kHz sample rate (good for speech)
                ac=1,  # Mono
                f="wav",
            )
            stream = ffmpeg.overwrite_output(stream)

            # Execute conversion
            ffmpeg.run(stream, quiet=True, capture_stdout=True, capture_stderr=True)

            if not output_path.exists():
                raise RuntimeError("Audio preparation failed - output file not created")

            return output_path

        except ffmpeg.Error as e:
            raise RuntimeError(f"Audio preparation failed: {e}") from e
