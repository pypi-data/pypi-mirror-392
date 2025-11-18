"""LLM provider abstractions for conversation analysis."""

import abc
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Standardized response from LLM providers."""

    text: str
    usage: Optional[Dict[str, Any]] = None
    model: Optional[str] = None
    finish_reason: Optional[str] = None


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""

    api_key: str
    model: str = "default"
    temperature: float = 0.1
    max_tokens: int = 200
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0


class LLMProvider(abc.ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None

    @abc.abstractmethod
    def initialize_client(self) -> None:
        """Initialize the LLM client."""
        pass

    @abc.abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response from the LLM."""
        pass

    @abc.abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and properly configured."""
        pass

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass

    def cleanup(self) -> None:
        """Clean up resources if needed."""
        pass


class LLMProviderRegistry:
    """Registry for LLM providers."""

    def __init__(self):
        self._providers: Dict[str, type[LLMProvider]] = {}

    def register(self, name: str, provider_class: type[LLMProvider]) -> None:
        """Register a provider class."""
        self._providers[name] = provider_class

    def get_provider_class(self, name: str) -> Optional[type[LLMProvider]]:
        """Get a provider class by name."""
        return self._providers.get(name)

    def list_providers(self) -> List[str]:
        """List all registered provider names."""
        return list(self._providers.keys())

    def create_provider(self, name: str, config: LLMConfig) -> Optional[LLMProvider]:
        """Create a provider instance."""
        provider_class = self.get_provider_class(name)
        if provider_class:
            return provider_class(config)
        return None


# Global registry instance
registry = LLMProviderRegistry()
