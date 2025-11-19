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

### Basic Usage

```python
from pcompresslr import Pcompresslr

# Initialize compressor
compressor = Pcompresslr(
    model="gpt-4",
    api_key="your-api-key"  # Or set PCOMPRESLR_API_KEY env var
)

# Compress a prompt
compressed_prompt = compressor.compress("Your long prompt with repeated text here...")

# Send to your LLM...
# model_response = your_llm_client.complete(compressed_prompt)

# Get compression statistics
stats = compressor.get_compression_stats()
print(f"Token savings: {stats['token_savings']} tokens ({stats['token_savings_percent']:.1f}%)")
```

### With Output Compression

```python
from pcompresslr import Pcompresslr

# Enable output compression
compressor = Pcompresslr(
    model="gpt-4",
    compress_output=True,  # Enable output compression
    api_key="your-api-key"
)

# Compress prompt (includes output compression instructions)
compressed_prompt = compressor.compress("Your prompt here...")

# Send to LLM
model_response = your_llm_client.complete(compressed_prompt)

# Decompress the model's compressed output
decompressed_output = compressor.decompress_output(model_response)
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

- `compress(prompt, model=None, use_optimal=None, compress_output=None)`: Compress a prompt and return the compressed prompt ready to send to the LLM
- `get_compressed_prompt()`: Returns the compressed prompt from the last `compress()` call
- `decompress_output(model_response)`: Decompresses the model's compressed output (requires `compress_output=True`)
- `get_compression_stats()`: Returns dictionary with compression statistics from the last `compress()` call
- `get_input_size_increase()`: Returns tuple of (additional_tokens, additional_chars) for output compression instructions
- `complete(prompt, ...)`: Complete a prompt with compression, LLM call, and decompression in one request

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

### Example 1: Basic Compression

```python
from pcompresslr import Pcompresslr

prompt = """
Write a story about a cat. The cat is very friendly. 
Write a story about a dog. The dog is very friendly.
Write a story about a bird. The bird is very friendly.
"""

compressor = Pcompresslr(model="gpt-4", api_key="your-key")
compressed = compressor.compress(prompt)
stats = compressor.get_compression_stats()

print(f"Original tokens: {stats['original_tokens']}")
print(f"Compressed tokens: {stats['compressed_tokens']}")
print(f"Savings: {stats['token_savings']} tokens ({stats['token_savings_percent']:.1f}%)")
```

### Example 2: Output Compression

```python
from pcompresslr import Pcompresslr

compressor = Pcompresslr(
    model="gpt-4",
    compress_output=True,
    api_key="your-key"
)

# Compress and send to LLM
compressed_prompt = compressor.compress("Generate a long report with repeated sections...")
response = llm_client.complete(compressed_prompt)

# Decompress the response
decompressed = compressor.decompress_output(response)
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
