"""Anthropic Claude LLM provider implementation."""

from typing import Dict, Any
import time

from .base import LLMProvider, LLMConfig, LLMResponse, registry


class ClaudeProvider(LLMProvider):
    """Anthropic Claude LLM provider."""

    @property
    def provider_name(self) -> str:
        return "claude"

    def initialize_client(self) -> None:
        """Initialize the Anthropic client."""
        try:
            import anthropic

            self._client = anthropic.Anthropic(api_key=self.config.api_key)
        except ImportError:
            raise ImportError("anthropic package is required for Claude provider")

    def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response using Claude."""
        if not self._client:
            self.initialize_client()

        # Prepare messages for Claude
        messages = [{"role": "user", "content": prompt}]

        # Retry logic
        last_error = None
        for attempt in range(self.config.retry_attempts):
            try:
                response = self._client.messages.create(
                    model=self.config.model or "claude-3-sonnet-20240229",
                    messages=messages,
                    temperature=kwargs.get("temperature", self.config.temperature),
                    max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                    timeout=self.config.timeout,
                )

                return LLMResponse(
                    text=response.content[0].text,
                    usage={
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens,
                        "total_tokens": response.usage.input_tokens
                        + response.usage.output_tokens,
                    },
                    model=response.model,
                    finish_reason=response.stop_reason,
                )

            except Exception as e:
                last_error = e
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(
                        self.config.retry_delay * (2**attempt)
                    )  # Exponential backoff

        raise last_error

    def is_available(self) -> bool:
        """Check if Claude is available."""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.config.api_key)
            # Try a simple API call
            client.messages.create(
                model="claude-3-haiku-20240307",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10,
            )
            return True
        except Exception:
            return False


# Register the provider
registry.register("claude", ClaudeProvider)
