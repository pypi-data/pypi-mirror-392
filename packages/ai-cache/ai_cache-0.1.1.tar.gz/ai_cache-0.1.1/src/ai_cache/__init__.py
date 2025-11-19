"""
ai-cache: Lightweight automatic caching for LLM API responses

Save time, tokens, and API costs by preventing repeated calls for the same prompt.
"""

from .core import enable, disable, clear, get_stats, is_enabled

__version__ = "0.1.1"
__all__ = ["enable", "disable", "clear", "get_stats", "is_enabled"]
