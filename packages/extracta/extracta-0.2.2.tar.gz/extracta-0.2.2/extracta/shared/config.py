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


class LLMConfig(BaseModel):
    """Configuration for LLM providers."""

    provider: str = Field(default="gemini", description="LLM provider to use")
    api_key: str = Field(default="", description="API key for the LLM provider")
    model: str = Field(default="gemini-pro", description="Model to use")
    temperature: float = Field(default=0.1, description="Temperature for generation")
    max_tokens: int = Field(default=200, description="Maximum tokens to generate")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    retry_delay: float = Field(default=1.0, description="Delay between retries")


class ExtractaConfig(BaseModel):
    """Main configuration for extracta."""

    app_name: str = Field(default="Extracta", description="Application name")
    version: str = Field(default="0.2.1", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")

    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)


def get_config() -> ExtractaConfig:
    """Get the default configuration."""
    return ExtractaConfig()


def load_config(
    config_file: Path | str | None = None, env_prefix: str = "EXTRACTA"
) -> ExtractaConfig:
    """Load configuration from file, environment, or both.

    Args:
        config_file: Path to TOML/JSON/YAML config file
        env_prefix: Environment variable prefix (default: EXTRACTA)

    Returns:
        ExtractaConfig: Loaded and validated configuration
    """
    config = ExtractaConfig()

    # Load from file if specified
    if config_file:
        config = _load_config_from_file(config_file, config)

    # Override with environment variables
    config = _load_config_from_env(config, env_prefix)

    # Validate configuration
    _validate_config(config)

    return config


def _load_config_from_file(
    config_file: Path | str, base_config: ExtractaConfig
) -> ExtractaConfig:
    """Load configuration from file."""
    import tomllib
    import json
    import yaml

    config_path = Path(config_file)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    try:
        if config_path.suffix.lower() == ".toml":
            with open(config_path, "rb") as f:
                file_data = tomllib.load(f)
        elif config_path.suffix.lower() in [".yaml", ".yml"]:
            try:
                import yaml

                with open(config_path, "r", encoding="utf-8") as f:
                    file_data = yaml.safe_load(f)
            except ImportError:
                raise ImportError("PyYAML required for YAML config files")
        elif config_path.suffix.lower() == ".json":
            with open(config_path, "r", encoding="utf-8") as f:
                file_data = json.load(f)
        else:
            raise ValueError(f"Unsupported config file format: {config_path.suffix}")

        # Merge file config with base config
        return _merge_config_dict(base_config, file_data)

    except Exception as e:
        raise ValueError(f"Failed to load config file {config_file}: {e}")


def _load_config_from_env(base_config: ExtractaConfig, prefix: str) -> ExtractaConfig:
    """Load configuration from environment variables."""
    # App-level settings
    if os.getenv(f"{prefix}_DEBUG"):
        base_config.debug = _parse_bool_env(os.getenv(f"{prefix}_DEBUG"))

    # Processing settings
    max_video_size = os.getenv(f"{prefix}_MAX_VIDEO_SIZE_MB")
    if max_video_size:
        base_config.processing.max_video_size_mb = int(max_video_size)

    max_image_size = os.getenv(f"{prefix}_MAX_IMAGE_SIZE_MB")
    if max_image_size:
        # Note: AnalysisConfig doesn't have max_image_size_mb, skipping
        pass

    # Analysis settings
    confidence_threshold = os.getenv(f"{prefix}_CONFIDENCE_THRESHOLD")
    if confidence_threshold:
        base_config.analysis.confidence_threshold = float(confidence_threshold)

    ocr_languages = os.getenv(f"{prefix}_OCR_LANGUAGES")
    if ocr_languages:
        base_config.analysis.ocr_languages = ocr_languages.split(",")

    # LLM settings
    llm_provider = os.getenv(f"{prefix}_LLM_PROVIDER")
    if llm_provider:
        base_config.llm.provider = llm_provider

    llm_api_key = os.getenv(f"{prefix}_LLM_API_KEY")
    if llm_api_key:
        base_config.llm.api_key = llm_api_key

    llm_model = os.getenv(f"{prefix}_LLM_MODEL")
    if llm_model:
        base_config.llm.model = llm_model

    llm_temp = os.getenv(f"{prefix}_LLM_TEMPERATURE")
    if llm_temp:
        base_config.llm.temperature = float(llm_temp)

    llm_max_tokens = os.getenv(f"{prefix}_LLM_MAX_TOKENS")
    if llm_max_tokens:
        base_config.llm.max_tokens = int(llm_max_tokens)

    llm_timeout = os.getenv(f"{prefix}_LLM_TIMEOUT")
    if llm_timeout:
        base_config.llm.timeout = int(llm_timeout)

    llm_retry_attempts = os.getenv(f"{prefix}_LLM_RETRY_ATTEMPTS")
    if llm_retry_attempts:
        base_config.llm.retry_attempts = int(llm_retry_attempts)

    llm_retry_delay = os.getenv(f"{prefix}_LLM_RETRY_DELAY")
    if llm_retry_delay:
        base_config.llm.retry_delay = float(llm_retry_delay)

    if os.getenv(f"{prefix}_LLM_RETRY_DELAY"):
        base_config.llm.retry_delay = float(os.getenv(f"{prefix}_LLM_RETRY_DELAY"))

    return base_config


def _merge_config_dict(base_config: ExtractaConfig, file_data: dict) -> ExtractaConfig:
    """Merge dictionary config with base ExtractaConfig."""
    # This is a simplified merge - in production you'd want a more comprehensive merger
    # For now, we'll just handle the LLM section as an example

    if "llm" in file_data:
        llm_data = file_data["llm"]
        for key, value in llm_data.items():
            if hasattr(base_config.llm, key):
                setattr(base_config.llm, key, value)

    return base_config


def _validate_config(config: ExtractaConfig) -> None:
    """Validate configuration values."""
    from .error_handling import ConfigurationError

    errors = []

    # Validate LLM configuration
    if config.llm.provider and config.llm.provider not in [
        "gemini",
        "openai",
        "claude",
        "openrouter",
    ]:
        errors.append(f"Invalid LLM provider: {config.llm.provider}")

    if config.llm.temperature < 0.0 or config.llm.temperature > 2.0:
        errors.append(
            f"LLM temperature must be between 0.0 and 2.0, got {config.llm.temperature}"
        )

    if config.llm.max_tokens < 1 or config.llm.max_tokens > 32768:
        errors.append(
            f"LLM max_tokens must be between 1 and 32768, got {config.llm.max_tokens}"
        )

    if config.llm.timeout < 1:
        errors.append(
            f"LLM timeout must be at least 1 second, got {config.llm.timeout}"
        )

    # Validate processing limits
    if config.processing.max_video_size_mb < 1:
        errors.append(
            f"Max video size must be at least 1 MB, got {config.processing.max_video_size_mb}"
        )

    if (
        config.analysis.confidence_threshold < 0.0
        or config.analysis.confidence_threshold > 1.0
    ):
        errors.append(
            f"Confidence threshold must be between 0.0 and 1.0, got {config.analysis.confidence_threshold}"
        )

    if errors:
        raise ConfigurationError(
            f"Configuration validation failed: {'; '.join(errors)}",
            details={"validation_errors": errors},
        )


def _parse_bool_env(value: str | None) -> bool:
    """Parse boolean environment variable."""
    if not value:
        return False
    return value.lower() in ("true", "1", "yes", "on")


def save_config(config: ExtractaConfig, config_file: Path | str) -> None:
    """Save configuration to file."""
    import tomllib
    import json

    config_path = Path(config_file)

    # Convert config to dict
    config_dict = {
        "app_name": config.app_name,
        "version": config.version,
        "debug": config.debug,
        "processing": config.processing.model_dump(),
        "analysis": config.analysis.model_dump(),
        "output": config.output.model_dump(),
        "llm": config.llm.model_dump(),
    }

    try:
        if config_path.suffix.lower() == ".toml":
            # For TOML, we'd need tomli_w, but let's use JSON for now
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=2)
        else:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=2)

    except Exception as e:
        raise ValueError(f"Failed to save config to {config_file}: {e}")


def create_default_config_file(config_file: Path | str) -> None:
    """Create a default configuration file."""
    default_config = ExtractaConfig()
    save_config(default_config, config_file)
