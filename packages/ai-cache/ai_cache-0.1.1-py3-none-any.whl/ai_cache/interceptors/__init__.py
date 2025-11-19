"""
Base interceptor class and provider exports
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseInterceptor(ABC):
    """Base class for LLM provider interceptors"""

    def __init__(self, cache_engine):
        self.cache_engine = cache_engine
        self._original_methods = {}

    @abstractmethod
    def activate(self):
        """Activate the interceptor by patching provider methods"""
        pass

    @abstractmethod
    def deactivate(self):
        """Deactivate the interceptor by restoring original methods"""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name for cache identification"""
        pass


# Import specific interceptors
from .openai import OpenAIInterceptor
from .anthropic import AnthropicInterceptor
from .gemini import GeminiInterceptor

__all__ = ["BaseInterceptor", "OpenAIInterceptor", "AnthropicInterceptor", "GeminiInterceptor"]
