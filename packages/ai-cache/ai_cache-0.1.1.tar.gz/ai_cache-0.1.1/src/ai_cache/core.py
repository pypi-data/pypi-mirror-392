"""
Core API for enabling/disabling cache
"""

from typing import Optional
from .cache_engine import CacheEngine
from .interceptors import (
    OpenAIInterceptor,
    AnthropicInterceptor,
    GeminiInterceptor,
)

# Global state
_cache_engine: Optional[CacheEngine] = None
_interceptors = []
_enabled = False


def enable(cache_dir: Optional[str] = None, ttl: Optional[int] = None):
    """
    Enable LLM response caching

    Args:
        cache_dir: Directory for cache database (default: ~/.ai-cache/)
        ttl: Time-to-live in seconds for cache entries (None = no expiration)

    Example:
        >>> import ai_cache
        >>> ai_cache.enable()
        >>> # Now all LLM API calls are automatically cached
    """
    global _cache_engine, _interceptors, _enabled

    if _enabled:
        return  # Already enabled

    # Initialize cache engine
    _cache_engine = CacheEngine(cache_dir=cache_dir, ttl=ttl)

    # Activate interceptors for each provider
    _interceptors = [
        OpenAIInterceptor(_cache_engine),
        AnthropicInterceptor(_cache_engine),
        GeminiInterceptor(_cache_engine),
    ]

    for interceptor in _interceptors:
        interceptor.activate()

    _enabled = True


def disable():
    """
    Disable LLM response caching

    Example:
        >>> import ai_cache
        >>> ai_cache.disable()
    """
    global _cache_engine, _interceptors, _enabled

    if not _enabled:
        return

    # Deactivate all interceptors
    for interceptor in _interceptors:
        interceptor.deactivate()

    _interceptors = []
    _cache_engine = None
    _enabled = False


def clear():
    """
    Clear all cached responses

    Example:
        >>> import ai_cache
        >>> ai_cache.clear()
    """
    if _cache_engine is None:
        raise RuntimeError("Cache is not enabled. Call ai_cache.enable() first.")

    _cache_engine.clear()


def get_stats():
    """
    Get cache statistics

    Returns:
        Dictionary with hits, misses, hit rate, and total entries

    Example:
        >>> import ai_cache
        >>> stats = ai_cache.get_stats()
        >>> print(f"Cache hits: {stats['hits']}")
    """
    if _cache_engine is None:
        raise RuntimeError("Cache is not enabled. Call ai_cache.enable() first.")

    return _cache_engine.get_stats()


def is_enabled() -> bool:
    """
    Check if caching is currently enabled

    Returns:
        True if caching is active, False otherwise

    Example:
        >>> import ai_cache
        >>> if ai_cache.is_enabled():
        ...     print("Caching is active")
    """
    return _enabled


def invalidate(provider: Optional[str] = None, model: Optional[str] = None):
    """
    Invalidate cache entries by provider/model

    Args:
        provider: Filter by provider (e.g., 'openai', 'anthropic')
        model: Filter by model (e.g., 'gpt-4', 'claude-3')

    Example:
        >>> import ai_cache
        >>> # Clear all OpenAI cache entries
        >>> ai_cache.invalidate(provider='openai')
        >>> # Clear all GPT-4 entries
        >>> ai_cache.invalidate(model='gpt-4')
    """
    if _cache_engine is None:
        raise RuntimeError("Cache is not enabled. Call ai_cache.enable() first.")

    _cache_engine.invalidate(provider=provider, model=model)
