# Compress Light Reach

**Intelligent compression algorithms for LLM prompts that reduce token usage**

[![PyPI version](https://badge.fury.io/py/compress-lightreach.svg)](https://badge.fury.io/py/compress-lightreach)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Compress Light Reach is a Python library that intelligently compresses LLM prompts by replacing repeated substrings with shorter placeholders, significantly reducing token usage and costs while maintaining perfect decompression.

## Features

- **Token-aware compression**: Only replaces substrings >1 token with 1-token placeholders
- **Dual algorithms**: 
  - Fast greedy (~99% optimal) for daily use
  - Optimal DP (O(n²)) for critical prompts
- **Lossless**: Perfect decompression guaranteed
- **Output compression**: Optional model output compression support
- **Cloud API**: Uses Light Reach's cloud service for compression
- **Model-aware**: Optimized for GPT-4, GPT-3.5-turbo, Claude, and more

## Installation

```bash
pip install compress-lightreach
```

## Quick Start

> **Note:** Most users should use `complete()`. Use `compress()` only if you need to integrate with a custom LLM client or want more control over the LLM call.

### Recommended: Complete Method (All-in-One)

The easiest way to use Compress Light Reach is with the `complete()` method, which handles compression, LLM call, and decompression in one request:

```python
from pcompresslr import Pcompresslr

# Initialize compressor with LLM provider credentials
compressor = Pcompresslr(
    model="gpt-4",
    api_key="your-compress-api-key",  # Or set PCOMPRESLR_API_KEY env var
    llm_provider="openai",  # or "anthropic"
    llm_api_key="your-llm-api-key"  # OpenAI or Anthropic API key
)

# Complete a prompt (compresses, calls LLM, decompresses)
result = compressor.complete("Your long prompt with repeated text here...")

# Get the final decompressed response
print(result["decompressed_response"])

# View compression statistics
print(f"Token savings: {result['compression_stats']['token_savings']} tokens")
print(f"Compression ratio: {result['compression_stats']['compression_ratio']:.2%}")
```

### With Output Compression

```python
from pcompresslr import Pcompresslr

compressor = Pcompresslr(
    model="gpt-4",
    api_key="your-api-key",
    llm_provider="openai",
    llm_api_key="your-llm-api-key",
    compress_output=True  # Enable output compression
)

# Complete with output compression enabled
result = compressor.complete("Generate a long report with repeated sections...")

# Response is automatically decompressed
print(result["decompressed_response"])
```

### Advanced: Manual Compression (For Custom LLM Workflows)

> **When to use:** Only use `compress()` if you need to integrate with a custom LLM client or want more control over the LLM call. Most users should use `complete()` instead.

If you need more control over the LLM call, you can compress manually and send to your own LLM client:

```python
from pcompresslr import Pcompresslr

# Initialize compressor
compressor = Pcompresslr(
    model="gpt-4",
    api_key="your-api-key"  # Or set PCOMPRESLR_API_KEY env var
)

# Compress a prompt (returns compressed prompt ready to send to LLM)
compressed_prompt = compressor.compress("Your long prompt with repeated text here...")

# Send to your LLM client
# model_response = your_llm_client.complete(compressed_prompt)

# Get compression statistics
stats = compressor.get_compression_stats()
print(f"Token savings: {stats['token_savings']} tokens ({stats['token_savings_percent']:.1f}%)")
```

### Manual Compression with Output Compression

```python
from pcompresslr import Pcompresslr

compressor = Pcompresslr(
    model="gpt-4",
    compress_output=True,  # Enable output compression
    api_key="your-api-key"
)

# Compress prompt (includes output compression instructions)
compressed_prompt = compressor.compress("Your prompt here...")

# Send to your LLM client
# model_response = your_llm_client.complete(compressed_prompt)

# Decompress the model's compressed output
# decompressed_output = compressor.decompress_output(model_response)
```

### Using the API Client Directly

```python
from pcompresslr import PcompresslrAPIClient

client = PcompresslrAPIClient(api_key="your-api-key")

# Compress a prompt
result = client.compress(
    prompt="Your prompt here...",
    model="gpt-4",
    algorithm="greedy"  # or "optimal"
)

print(f"Compressed: {result['compressed']}")
print(f"LLM format: {result['llm_format']}")
print(f"Compression ratio: {result['compression_ratio']:.2%}")

# Decompress
decompressed = client.decompress(result['llm_format'])
print(f"Decompressed: {decompressed['decompressed']}")
```

### Command Line Interface

```bash
# Set your API key
export PCOMPRESLR_API_KEY=your-api-key

# Compress a prompt
pcompresslr "Your prompt with repeated text here..."

# Use optimal algorithm only
pcompresslr "Your prompt here" --optimal-only

# Use greedy algorithm only
pcompresslr "Your prompt here" --greedy-only
```

## API Reference

### `Pcompresslr`

Main interface class for prompt compression.

#### Parameters

- `model` (str): LLM model name for tokenization (default: `"gpt-4"`)
- `api_key` (str, optional): API key for authentication. If not provided, checks `PCOMPRESLR_API_KEY` env var.
- `compress_output` (bool): If True, instruct the model to output in compressed format (default: `False`)
- `use_optimal` (bool): If True, use optimal DP algorithm, else use fast greedy (default: `False`)
- `llm_provider` (str, optional): LLM provider ('openai' or 'anthropic') for caching API key
- `llm_api_key` (str, optional): LLM provider API key for use with `complete()` method

#### Methods

- `complete(prompt, model=None, llm_provider=None, llm_api_key=None, compress=True, compress_output=False, use_optimal=None, temperature=None, max_tokens=None)`: **Recommended** - Complete a prompt with compression, LLM call, and decompression in one request. Returns a dictionary with `decompressed_response`, `compression_stats`, `llm_stats`, and more.
- `compress(prompt, model=None, use_optimal=None, compress_output=None)`: Compress a prompt and return the compressed prompt ready to send to your LLM client. Use this for custom LLM workflows where you want to handle the LLM call yourself.
- `get_compressed_prompt()`: Returns the compressed prompt from the last `compress()` call
- `decompress_output(model_response)`: Decompresses the model's compressed output (requires `compress_output=True`). Only needed when using manual compression with output compression enabled.
- `get_compression_stats()`: Returns dictionary with compression statistics from the last `compress()` call
- `get_input_size_increase()`: Returns tuple of (additional_tokens, additional_chars) for output compression instructions
- `set_llm_key(provider, api_key)`: Cache LLM provider API key for use with `complete()` method
- `clear_llm_key()`: Clear cached LLM API key
- `has_llm_key()`: Check if LLM API key is cached

### `PcompresslrAPIClient`

Low-level API client for direct interaction with the compression service.

#### Methods

- `compress(prompt, model, algorithm)`: Compress a prompt
- `decompress(llm_format)`: Decompress an LLM-formatted compressed prompt
- `health_check()`: Check API health status

### Exceptions

- `APIKeyError`: Raised when API key is invalid or missing
- `RateLimitError`: Raised when rate limit is exceeded
- `APIRequestError`: Raised for general API errors

## How It Works

Compress Light Reach uses intelligent algorithms to identify repeated substrings in your prompts and replace them with shorter placeholders.

The library:
1. Identifies repeated substrings using efficient suffix array algorithms
2. Calculates token savings for each potential replacement
3. Selects optimal replacements that reduce total token count
4. Formats the result for easy LLM consumption
5. Provides perfect decompression

## Examples

### Example 1: Using Complete Method (Recommended)

```python
from pcompresslr import Pcompresslr

compressor = Pcompresslr(
    model="gpt-4",
    api_key="your-compress-api-key",
    llm_provider="openai",
    llm_api_key="your-openai-key"
)

prompt = """
Write a story about a cat. The cat is very friendly. 
Write a story about a dog. The dog is very friendly.
Write a story about a bird. The bird is very friendly.
"""

# One call handles compression, LLM request, and decompression
result = compressor.complete(prompt)

print(result["decompressed_response"])
print(f"Token savings: {result['compression_stats']['token_savings']} tokens")
print(f"Compression ratio: {result['compression_stats']['compression_ratio']:.2%}")
```

### Example 2: Manual Compression (Advanced)

```python
from pcompresslr import Pcompresslr

compressor = Pcompresslr(model="gpt-4", api_key="your-key")

prompt = """
Write a story about a cat. The cat is very friendly. 
Write a story about a dog. The dog is very friendly.
Write a story about a bird. The bird is very friendly.
"""

# Compress manually
compressed = compressor.compress(prompt)
stats = compressor.get_compression_stats()

print(f"Original tokens: {stats['original_tokens']}")
print(f"Compressed tokens: {stats['compressed_tokens']}")
print(f"Savings: {stats['token_savings']} tokens ({stats['token_savings_percent']:.1f}%)")

# Send compressed_prompt to your LLM client...
```

### Example 3: Complete with Output Compression

```python
from pcompresslr import Pcompresslr

compressor = Pcompresslr(
    model="gpt-4",
    api_key="your-compress-api-key",
    llm_provider="openai",
    llm_api_key="your-openai-key",
    compress_output=True
)

# Complete with output compression - response is automatically decompressed
result = compressor.complete("Generate a long report with repeated sections...")
print(result["decompressed_response"])
```

## Getting an API Key

To use Compress Light Reach, you need an API key from [compress.lightreach.io](https://compress.lightreach.io).

1. Visit [compress.lightreach.io](https://compress.lightreach.io)
2. Sign up for an account
3. Get your API key from the dashboard
4. Set it as an environment variable: `export PCOMPRESLR_API_KEY=your-key`

## Requirements

- Python 3.8+
- tiktoken >= 0.5.0
- requests >= 2.31.0
- urllib3 >= 2.0.0

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- Documentation: [compress.lightreach.io/docs](https://compress.lightreach.io/docs)
- Issues: [GitHub Issues](https://github.com/lightreach/compress-lightreach/issues)
- Email: jonathankt@lightreach.io

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
