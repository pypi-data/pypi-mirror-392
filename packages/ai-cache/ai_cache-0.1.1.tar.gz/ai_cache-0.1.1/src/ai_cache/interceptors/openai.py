"""
OpenAI API interceptor
"""

import sys
from typing import Any, Dict
from . import BaseInterceptor


class OpenAIInterceptor(BaseInterceptor):
    """Interceptor for OpenAI API calls"""

    def get_provider_name(self) -> str:
        return "openai"

    def activate(self):
        """Patch OpenAI client methods"""
        try:
            import openai
        except ImportError:
            # OpenAI not installed, skip
            return

        # Store original methods
        if hasattr(openai, "ChatCompletion"):
            # Old OpenAI API (< 1.0.0)
            self._patch_legacy_api(openai)
        elif hasattr(openai, "OpenAI"):
            # New OpenAI API (>= 1.0.0)
            self._patch_new_api(openai)

    def _patch_legacy_api(self, openai):
        """Patch legacy OpenAI API (< 1.0.0)"""
        if hasattr(openai.ChatCompletion, "create"):
            original_create = openai.ChatCompletion.create
            self._original_methods["chat_completion_create"] = original_create

            def cached_create(*args, **kwargs):
                # Extract model and messages
                model = kwargs.get("model", "unknown")
                request_data = {
                    "messages": kwargs.get("messages", []),
                    "temperature": kwargs.get("temperature"),
                    "max_tokens": kwargs.get("max_tokens"),
                    "top_p": kwargs.get("top_p"),
                }

                # Try to get from cache
                cached = self.cache_engine.get(
                    self.get_provider_name(), model, request_data
                )
                if cached is not None:
                    return self._reconstruct_response(cached)

                # Call original API
                response = original_create(*args, **kwargs)

                # Cache the response
                response_dict = self._serialize_response(response)
                self.cache_engine.set(
                    self.get_provider_name(), model, request_data, response_dict
                )

                return response

            openai.ChatCompletion.create = cached_create

    def _patch_new_api(self, openai):
        """Patch new OpenAI API (>= 1.0.0)"""
        try:
            original_init = openai.OpenAI.__init__
            self._original_methods["openai_init"] = original_init

            def patched_init(self, *args, **kwargs):
                original_init(self, *args, **kwargs)
                self._patch_client_methods(self)

            openai.OpenAI.__init__ = patched_init

            # Also patch existing clients if any
            if hasattr(openai, "_default_client") and openai._default_client:
                self._patch_client_methods(openai._default_client)

        except Exception:
            pass  # Silently fail if patching doesn't work

    def _patch_client_methods(self, client):
        """Patch methods on an OpenAI client instance"""
        if hasattr(client, "chat") and hasattr(client.chat, "completions"):
            original_create = client.chat.completions.create
            self._original_methods["client_chat_create"] = original_create

            def cached_create(*args, **kwargs):
                model = kwargs.get("model", "unknown")
                request_data = {
                    "messages": kwargs.get("messages", []),
                    "temperature": kwargs.get("temperature"),
                    "max_tokens": kwargs.get("max_tokens"),
                    "top_p": kwargs.get("top_p"),
                }

                cached = self.cache_engine.get(
                    self.get_provider_name(), model, request_data
                )
                if cached is not None:
                    return self._reconstruct_response(cached)

                response = original_create(*args, **kwargs)
                response_dict = self._serialize_response(response)
                self.cache_engine.set(
                    self.get_provider_name(), model, request_data, response_dict
                )

                return response

            client.chat.completions.create = cached_create

    def deactivate(self):
        """Restore original OpenAI methods"""
        try:
            import openai
        except ImportError:
            return

        # Restore legacy API
        if "chat_completion_create" in self._original_methods:
            openai.ChatCompletion.create = self._original_methods["chat_completion_create"]

        # Note: Restoring new API requires more complex logic
        # For now, we keep it simple
        self._original_methods.clear()

    def _serialize_response(self, response) -> Dict[str, Any]:
        """Convert OpenAI response to dict for caching"""
        if hasattr(response, "model_dump"):
            # New API (Pydantic model)
            return response.model_dump()
        elif hasattr(response, "to_dict"):
            # Legacy API
            return response.to_dict()
        else:
            # Fallback: try to convert to dict
            return dict(response)

    def _reconstruct_response(self, cached_dict: Dict[str, Any]):
        """Reconstruct OpenAI response object from cached dict"""
        try:
            import openai
            
            # Try to reconstruct proper response object
            if hasattr(openai, "OpenAI"):
                # New API - return dict-like object
                # In practice, most code works with the dict representation
                return type("CachedResponse", (), cached_dict)()
            else:
                # Legacy API
                return type("CachedResponse", (), cached_dict)()
        except Exception:
            # Fallback to dict
            return cached_dict
