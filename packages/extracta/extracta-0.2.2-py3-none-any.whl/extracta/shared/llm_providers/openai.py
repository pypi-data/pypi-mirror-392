"""OpenAI LLM provider implementation."""

from typing import Dict, Any
import time

from .base import LLMProvider, LLMConfig, LLMResponse, registry


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""

    @property
    def provider_name(self) -> str:
        return "openai"

    def initialize_client(self) -> None:
        """Initialize the OpenAI client."""
        try:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.config.api_key)
        except ImportError:
            raise ImportError("openai package is required for OpenAI provider")

    def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response using OpenAI."""
        if not self._client:
            self.initialize_client()

        # Prepare messages
        messages = [{"role": "user", "content": prompt}]

        # Retry logic
        last_error = None
        for attempt in range(self.config.retry_attempts):
            try:
                response = self._client.chat.completions.create(
                    model=self.config.model or "gpt-3.5-turbo",
                    messages=messages,
                    temperature=kwargs.get("temperature", self.config.temperature),
                    max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                    timeout=self.config.timeout,
                )

                return LLMResponse(
                    text=response.choices[0].message.content,
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    },
                    model=response.model,
                    finish_reason=response.choices[0].finish_reason,
                )

            except Exception as e:
                last_error = e
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(
                        self.config.retry_delay * (2**attempt)
                    )  # Exponential backoff

        raise last_error

    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.config.api_key)
            # Try a simple API call
            client.models.list()
            return True
        except Exception:
            return False


# Register the provider
registry.register("openai", OpenAIProvider)
