"""OpenRouter LLM provider implementation."""

from typing import Dict, Any
import time

from .base import LLMProvider, LLMConfig, LLMResponse, registry


class OpenRouterProvider(LLMProvider):
    """OpenRouter LLM provider (unified API for multiple models)."""

    @property
    def provider_name(self) -> str:
        return "openrouter"

    def initialize_client(self) -> None:
        """Initialize the OpenRouter client (uses OpenAI-compatible API)."""
        try:
            from openai import OpenAI

            self._client = OpenAI(
                api_key=self.config.api_key, base_url="https://openrouter.ai/api/v1"
            )
        except ImportError:
            raise ImportError("openai package is required for OpenRouter provider")

    def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response using OpenRouter."""
        if not self._client:
            self.initialize_client()

        # Prepare messages
        messages = [{"role": "user", "content": prompt}]

        # Retry logic
        last_error = None
        for attempt in range(self.config.retry_attempts):
            try:
                response = self._client.chat.completions.create(
                    model=self.config.model or "anthropic/claude-3-haiku",
                    messages=messages,
                    temperature=kwargs.get("temperature", self.config.temperature),
                    max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                    timeout=self.config.timeout,
                )

                return LLMResponse(
                    text=response.choices[0].message.content,
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens
                        if response.usage
                        else 0,
                        "completion_tokens": response.usage.completion_tokens
                        if response.usage
                        else 0,
                        "total_tokens": response.usage.total_tokens
                        if response.usage
                        else 0,
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
        """Check if OpenRouter is available."""
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=self.config.api_key, base_url="https://openrouter.ai/api/v1"
            )
            # Try a simple API call
            client.chat.completions.create(
                model="anthropic/claude-3-haiku",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5,
            )
            return True
        except Exception:
            return False


# Register the provider
registry.register("openrouter", OpenRouterProvider)
