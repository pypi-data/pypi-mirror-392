"""Gemini LLM provider implementation."""

from typing import Dict, Any
import time

from .base import LLMProvider, LLMConfig, LLMResponse, registry
from ..error_handling import APIError, ConfigurationError


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider."""

    @property
    def provider_name(self) -> str:
        return "gemini"

    def initialize_client(self) -> None:
        """Initialize the Gemini client."""
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.config.api_key)
            self._client = genai.GenerativeModel(self.config.model or "gemini-pro")
        except ImportError:
            raise ConfigurationError(
                "Google Generative AI package is required for Gemini provider",
                details={
                    "provider": "gemini",
                    "missing_package": "google-generativeai",
                },
                suggestions=["Install with: pip install google-generativeai"],
            )

    def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response using Gemini."""
        if not self._client:
            self.initialize_client()

        # Prepare generation config
        generation_config = {
            "temperature": kwargs.get("temperature", self.config.temperature),
            "top_p": kwargs.get("top_p", 0.8),
            "top_k": kwargs.get("top_k", 40),
            "max_output_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }

        # Retry logic
        last_error = None
        for attempt in range(self.config.retry_attempts):
            try:
                response = self._client.generate_content(
                    prompt, generation_config=generation_config
                )

                return LLMResponse(
                    text=response.text,
                    usage=getattr(response, "usage_metadata", None),
                    model=self.config.model,
                    finish_reason=getattr(response, "candidates", [{}])[0].get(
                        "finish_reason"
                    ),
                )

            except Exception as e:
                last_error = e
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(
                        self.config.retry_delay * (2**attempt)
                    )  # Exponential backoff

        raise last_error

    def is_available(self) -> bool:
        """Check if Gemini is available."""
        try:
            import google.generativeai as genai

            # Try to configure with the API key
            genai.configure(api_key=self.config.api_key)
            # Try a simple model list call
            genai.list_models()
            return True
        except Exception:
            return False


# Register the provider
registry.register("gemini", GeminiProvider)
