"""
Anthropic API interceptor
"""

from typing import Any, Dict
from . import BaseInterceptor


class AnthropicInterceptor(BaseInterceptor):
    """Interceptor for Anthropic (Claude) API calls"""

    def get_provider_name(self) -> str:
        return "anthropic"

    def activate(self):
        """Patch Anthropic client methods"""
        try:
            import anthropic
        except ImportError:
            # Anthropic not installed, skip
            return

        try:
            # Patch the Messages.create method
            original_create = anthropic.Anthropic.messages.create
            self._original_methods["messages_create"] = original_create

            cache_engine = self.cache_engine
            provider_name = self.get_provider_name()
            serialize_fn = self._serialize_response
            reconstruct_fn = self._reconstruct_response

            def cached_create(self, *args, **kwargs):
                model = kwargs.get("model", "unknown")
                request_data = {
                    "messages": kwargs.get("messages", []),
                    "max_tokens": kwargs.get("max_tokens"),
                    "temperature": kwargs.get("temperature"),
                    "system": kwargs.get("system"),
                }

                cached = cache_engine.get(provider_name, model, request_data)
                if cached is not None:
                    return reconstruct_fn(cached)

                response = original_create(self, *args, **kwargs)
                response_dict = serialize_fn(response)
                cache_engine.set(provider_name, model, request_data, response_dict)

                return response

            # Monkey patch the create method
            anthropic.resources.messages.Messages.create = cached_create

        except Exception:
            pass  # Silently fail if structure is different

    def deactivate(self):
        """Restore original Anthropic methods"""
        try:
            import anthropic
        except ImportError:
            return

        if "messages_create" in self._original_methods:
            anthropic.resources.messages.Messages.create = self._original_methods[
                "messages_create"
            ]

        self._original_methods.clear()

    def _serialize_response(self, response) -> Dict[str, Any]:
        """Convert Anthropic response to dict for caching"""
        if hasattr(response, "model_dump"):
            return response.model_dump()
        elif hasattr(response, "to_dict"):
            return response.to_dict()
        else:
            return dict(response)

    def _reconstruct_response(self, cached_dict: Dict[str, Any]):
        """Reconstruct Anthropic response object from cached dict"""
        return type("CachedResponse", (), cached_dict)()
