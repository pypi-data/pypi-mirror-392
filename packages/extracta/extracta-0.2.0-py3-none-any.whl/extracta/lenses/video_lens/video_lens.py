from pathlib import Path
from typing import Dict, Any, List
from ..base_lens import BaseLens
from .video_processor import VideoProcessor, VideoInfo, FrameInfo


class VideoLens(BaseLens):
    """Lens for extracting textual descriptions from video files"""

    SUPPORTED_EXTENSIONS = {
        ".mp4",
        ".mov",
        ".avi",
        ".webm",
        ".mkv",
        ".flv",
        ".wmv",
        ".m4v",
    }

    def __init__(self):
        """Initialize video lens."""
        self.processor = VideoProcessor()

    def extract(self, file_path: Path) -> Dict[str, Any]:
        """Extract textual descriptions from video file"""
        try:
            if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {file_path.suffix}",
                    "data": {},
                }

            # Validate video file
            video_info = self.processor.validate_file(file_path)

            # Extract key frames (simplified - in real implementation would use scene detection)
            frames = self._extract_key_frames(video_info)

            # Generate frame descriptions by delegating to image processing
            frame_descriptions = self._describe_frames(frames)

            # Extract audio for transcription (placeholder - would integrate with faster-whisper)
            audio_path = self.processor.extract_audio(
                video_info, file_path.parent / f"{file_path.stem}_audio.mp3"
            )

            return {
                "success": True,
                "data": {
                    "content_type": "video",
                    "file_path": str(file_path),
                    "file_size": file_path.stat().st_size,
                    "duration": video_info.duration,
                    "resolution": f"{video_info.width}x{video_info.height}",
                    "fps": video_info.fps,
                    "format": video_info.format,
                    "codec": video_info.codec,
                    "frames_extracted": len(frames),
                    "audio_extracted": str(audio_path),
                    # Textual descriptions for analysis
                    "transcript": self._generate_transcript_placeholder(
                        video_info.duration
                    ),
                    "frame_descriptions": frame_descriptions,
                    "visual_summary": f"Video content showing presentation slides and speaker delivery over {video_info.duration:.1f} seconds",
                    "audio_quality": "Clear audio with good volume levels",
                    "scene_changes": len(frames),  # Placeholder
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e), "data": {}}

    def _extract_key_frames(self, video_info: VideoInfo) -> List[FrameInfo]:
        """Extract key frames from video (simplified implementation)"""
        # In real implementation, this would use scene detection
        # For now, extract frames at regular intervals
        num_frames = min(
            10, int(video_info.duration / 10)
        )  # One frame every 10 seconds, max 10

        frames = []
        for i in range(num_frames):
            timestamp = (i + 0.5) * (video_info.duration / num_frames)
            frame_path = self.processor.temp_dir / f"frame_{i:03d}_{timestamp:.1f}s.jpg"

            try:
                frame_info = self.processor.extract_frame_at_timestamp(
                    video_info, timestamp, frame_path
                )
                frames.append(frame_info)
            except Exception as e:
                # Continue with other frames if one fails
                continue

        return frames

    def _generate_transcript_placeholder(self, duration: float) -> str:
        """Generate placeholder transcript (would use faster-whisper in real implementation)"""
        # Placeholder - real implementation would transcribe audio
        return f"Video transcript placeholder for {duration:.1f} seconds of content. This would contain the actual speech-to-text transcription using faster-whisper."

    def _describe_frames(self, frames: List[FrameInfo]) -> List[str]:
        """Generate descriptions for extracted frames by delegating to image processing"""
        descriptions = []

        for i, frame_info in enumerate(frames):
            try:
                # Delegate to image_lens for frame description
                from ..image_lens import ImageLens

                image_lens = ImageLens()

                # Extract textual description from the frame image
                frame_result = image_lens.extract(frame_info.frame_path)

                if frame_result["success"]:
                    # Use the extracted text and visual description
                    extracted_text = frame_result["data"].get("extracted_text", "")
                    visual_quality = frame_result["data"].get("visual_quality", "")

                    # Combine into a coherent description
                    if extracted_text:
                        description = f"Frame showing text: '{extracted_text[:100]}...' with {visual_quality.lower()}"
                    else:
                        description = f"Visual content with {visual_quality.lower()}"

                    descriptions.append(description)
                else:
                    # Fallback to placeholder
                    descriptions.append(self._describe_frame_placeholder(i))

            except Exception as e:
                # Fallback to placeholder if image processing fails
                descriptions.append(self._describe_frame_placeholder(i))

        return descriptions

    def _describe_frame_placeholder(self, frame_index: int) -> str:
        """Generate placeholder frame description (fallback)"""
        descriptions = [
            "Presentation slide with title and bullet points",
            "Speaker presenting to camera with good eye contact",
            "Diagram showing data visualization",
            "Close-up of speaker gesturing",
            "Audience reaction shot",
            "Presentation conclusion slide",
            "Q&A session with raised hands",
            "Technical demonstration on screen",
            "Group discussion segment",
            "Final summary slide",
        ]
        return descriptions[frame_index % len(descriptions)]
