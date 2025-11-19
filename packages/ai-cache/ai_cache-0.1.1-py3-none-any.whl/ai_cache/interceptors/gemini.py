"""
Google Gemini API interceptor
"""

from typing import Any, Dict
from . import BaseInterceptor


class GeminiInterceptor(BaseInterceptor):
    """Interceptor for Google Gemini API calls"""

    def get_provider_name(self) -> str:
        return "gemini"

    def activate(self):
        """Patch Gemini client methods"""
        try:
            import google.generativeai as genai
        except ImportError:
            # Gemini not installed, skip
            return

        try:
            # Patch GenerativeModel.generate_content
            from google.generativeai.generative_models import GenerativeModel

            original_generate = GenerativeModel.generate_content
            self._original_methods["generate_content"] = original_generate

            cache_engine = self.cache_engine
            provider_name = self.get_provider_name()
            serialize_fn = self._serialize_response
            reconstruct_fn = self._reconstruct_response

            def cached_generate(self, *args, **kwargs):
                # Extract model name and content
                model = self.model_name if hasattr(self, "model_name") else "unknown"
                
                # Get the prompt/content
                if args:
                    content = args[0]
                else:
                    content = kwargs.get("contents", kwargs.get("prompt", ""))

                request_data = {
                    "content": str(content),
                    "generation_config": str(kwargs.get("generation_config")),
                    "safety_settings": str(kwargs.get("safety_settings")),
                }

                cached = cache_engine.get(provider_name, model, request_data)
                if cached is not None:
                    return reconstruct_fn(cached)

                response = original_generate(self, *args, **kwargs)
                response_dict = serialize_fn(response)
                cache_engine.set(provider_name, model, request_data, response_dict)

                return response

            GenerativeModel.generate_content = cached_generate

        except Exception:
            pass  # Silently fail

    def deactivate(self):
        """Restore original Gemini methods"""
        try:
            from google.generativeai.generative_models import GenerativeModel
        except ImportError:
            return

        if "generate_content" in self._original_methods:
            GenerativeModel.generate_content = self._original_methods["generate_content"]

        self._original_methods.clear()

    def _serialize_response(self, response) -> Dict[str, Any]:
        """Convert Gemini response to dict for caching"""
        try:
            # Gemini responses have a text property
            return {
                "text": response.text if hasattr(response, "text") else str(response),
                "candidates": str(response.candidates) if hasattr(response, "candidates") else None,
            }
        except Exception:
            return {"text": str(response)}

    def _reconstruct_response(self, cached_dict: Dict[str, Any]):
        """Reconstruct Gemini response object from cached dict"""
        return type("CachedResponse", (), cached_dict)()
