# ai-cache

A lightweight Python library for automatic caching of LLM API responses. Reduce costs and improve response times by caching repeated API calls to OpenAI, Anthropic, Google Gemini, and other LLM providers.

## Overview

ai-cache transparently intercepts LLM API calls and caches responses locally using SQLite. When the same request is made again, the cached response is returned instantly without making an actual API call. This saves time, reduces costs, and enables offline development.

## Features

- **Automatic caching** - No code changes required, works with existing applications
- **Multi-provider support** - Compatible with OpenAI, Anthropic, and Google Gemini APIs
- **Local storage** - All data stored in SQLite database on your machine
- **Zero dependencies** - Built using Python standard library only
- **Configurable expiration** - Optional TTL (time-to-live) for cache entries
- **Cache management** - Clear, invalidate, and monitor cache statistics
- **Privacy-focused** - No data leaves your machine

## Installation

```bash
pip install ai-cache
```

## Quick Start

```python
import ai_cache

# Enable caching globally
ai_cache.enable()

# Use any supported LLM API as normal
import openai

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What is Python?"}]
)

# Subsequent identical calls return instantly from cache
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What is Python?"}]
)
```

## Configuration

### Basic Usage

```python
import ai_cache

# Enable with default settings (cache stored in ~/.ai-cache/)
ai_cache.enable()

# Enable with custom cache directory
ai_cache.enable(cache_dir="./my_cache")

# Enable with TTL (cache expires after 1 hour)
ai_cache.enable(ttl=3600)

# Combine options
ai_cache.enable(cache_dir="./cache", ttl=7200)
```

### Cache Management

```python
# Check if caching is enabled
is_active = ai_cache.is_enabled()

# Get cache statistics
stats = ai_cache.get_stats()
print(f"Cache hits: {stats['hits']}")
print(f"Cache misses: {stats['misses']}")
print(f"Hit rate: {stats['hit_rate']}")
print(f"Total entries: {stats['total_entries']}")

# Clear all cached entries
ai_cache.clear()

# Invalidate cache by provider
ai_cache.invalidate(provider="openai")

# Invalidate cache by model
ai_cache.invalidate(model="gpt-4")

# Invalidate specific provider and model combination
ai_cache.invalidate(provider="openai", model="gpt-4")

# Disable caching
ai_cache.disable()
```

## Supported Providers

### OpenAI

Compatible with both legacy and modern OpenAI API versions.

```python
import ai_cache
import openai

ai_cache.enable()

# Legacy API (openai < 1.0.0)
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)

# Modern API (openai >= 1.0.0)
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Anthropic (Claude)

```python
import ai_cache
from anthropic import Anthropic

ai_cache.enable()

client = Anthropic(api_key="your-api-key")
message = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Google Gemini

```python
import ai_cache
import google.generativeai as genai

ai_cache.enable()

genai.configure(api_key="your-api-key")
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("What is machine learning?")
```

## How It Works

### Cache Key Generation

Each API request is fingerprinted using SHA256 hashing of:
- Provider name (e.g., "openai", "anthropic")
- Model identifier (e.g., "gpt-4", "claude-3")
- Request parameters (messages, temperature, max_tokens, etc.)

Two requests are considered identical only if all components match exactly.

### Cache Storage

- **Database**: SQLite database stored locally
- **Default location**: `~/.ai-cache/cache.db`
- **Schema**: Indexed table with fingerprint, provider, model, response, and timestamps
- **Thread safety**: SQLite handles concurrent access automatically

### Cache Expiration

When TTL is configured:
- Entries expire after specified number of seconds
- Expired entries are deleted automatically on access
- No background cleanup processes

Without TTL:
- Entries never expire automatically
- Manual invalidation or clearing required

### API Interception

The library uses monkey patching to intercept API client methods:
- Original methods are preserved and restored on disable
- Interception happens transparently without modifying your code
- If a provider library is not installed, its interceptor is silently skipped

## Use Cases

- **Development and Testing**: Speed up development by avoiding repeated API calls during testing
- **Prompt Engineering**: Iterate on prompts without incurring costs for unchanged requests
- **Batch Processing**: Run evaluations or benchmarks with automatic caching
- **Offline Development**: Work with cached responses when internet is unavailable
- **Cost Optimization**: Reduce API costs in production for frequently repeated queries
- **Demo Applications**: Build demos that work reliably without exhausting API quotas

## Performance

- **Cache hits**: Sub-millisecond response times (SQLite lookup)
- **Cache misses**: Original API latency + minimal overhead (~1ms for fingerprinting and storage)
- **Storage**: Minimal disk usage, approximately 1-10KB per cached response
- **Memory**: No in-memory cache, all data persisted to disk

## Limitations

- **Streaming responses**: Currently not supported
- **Non-deterministic APIs**: Temperature > 0 will generate different responses but use same cache key
- **Parameter sensitivity**: Small changes in parameters create new cache entries
- **Binary responses**: Image generation and similar APIs may not cache correctly

## API Reference

### `ai_cache.enable(cache_dir=None, ttl=None)`

Enable LLM response caching.

**Parameters:**
- `cache_dir` (str, optional): Directory for cache database. Default: `~/.ai-cache/`
- `ttl` (int, optional): Time-to-live in seconds for cache entries. Default: `None` (no expiration)

**Returns:** None

### `ai_cache.disable()`

Disable LLM response caching and restore original API methods.

**Returns:** None

### `ai_cache.clear()`

Clear all cached responses from the database.

**Raises:** `RuntimeError` if cache is not enabled.

**Returns:** None

### `ai_cache.get_stats()`

Get cache statistics.

**Returns:** Dictionary containing:
- `hits` (int): Number of cache hits
- `misses` (int): Number of cache misses
- `hit_rate` (str): Hit rate as percentage
- `total_entries` (int): Total cached entries in database

**Raises:** `RuntimeError` if cache is not enabled.

### `ai_cache.is_enabled()`

Check if caching is currently enabled.

**Returns:** `bool` - True if enabled, False otherwise

### `ai_cache.invalidate(provider=None, model=None)`

Invalidate cache entries by provider and/or model.

**Parameters:**
- `provider` (str, optional): Provider name (e.g., 'openai', 'anthropic')
- `model` (str, optional): Model name (e.g., 'gpt-4', 'claude-3')

**Raises:** `RuntimeError` if cache is not enabled.

**Returns:** None

## Troubleshooting

**Issue**: Cache not working
- Ensure `ai_cache.enable()` is called before making API calls
- Verify the provider library is installed (e.g., `pip install openai`)

**Issue**: Different responses on cache hit
- Cache returns exact stored response, check if request parameters match exactly
- Temperature and random seed affect cache keys

**Issue**: Disk space concerns
- Monitor cache size: `ls -lh ~/.ai-cache/cache.db`
- Clear periodically: `ai_cache.clear()`
- Configure TTL to auto-expire old entries

**Issue**: Permission errors
- Ensure write permissions on cache directory
- Use custom directory: `ai_cache.enable(cache_dir="./cache")`

## Contributing

Contributions are welcome. Please submit issues and pull requests on GitHub.

## License

MIT License - see LICENSE file for details.

## Links

- **GitHub**: https://github.com/Abdur-Rafay-AR/ai-cache
- **PyPI**: https://pypi.org/project/ai-cache/
- **Issues**: https://github.com/Abdur-Rafay-AR/ai-cache/issues
