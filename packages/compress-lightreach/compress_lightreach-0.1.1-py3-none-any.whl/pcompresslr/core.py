"""
Core Pcompresslr class for compressing prompts and optionally model outputs.
"""

from typing import Dict, Tuple, Optional

from .api_client import PcompresslrAPIClient, APIKeyError, RateLimitError, APIRequestError


class Pcompresslr:
    """
    Main interface for prompt compression with optional output compression.
    
    Usage:
        # Basic compression
        compressor = Pcompresslr(model="gpt-4", api_key="your-key")
        compressed_prompt = compressor.compress("Your prompt here")
        
        # With output compression
        compressor = Pcompresslr(model="gpt-4", api_key="your-key", compress_output=True)
        compressed_prompt = compressor.compress("Your prompt here")
        # ... send to model ...
        decompressed_output = compressor.decompress_output(model_response)
    """
    
    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        compress_output: bool = False,
        use_optimal: bool = False,
        llm_provider: Optional[str] = None,
        llm_api_key: Optional[str] = None
    ):
        """
        Initialize the compressor.
        
        Args:
            model: LLM model name for tokenization (e.g., 'gpt-4', 'gpt-3.5-turbo')
            api_key: API key for authentication. If not provided, checks PCOMPRESLR_API_KEY env var.
            compress_output: If True, instruct the model to output in compressed format
            use_optimal: If True, use optimal DP algorithm, else use fast greedy
            llm_provider: LLM provider ('openai' or 'anthropic') - for caching LLM API key
            llm_api_key: LLM provider API key - cached for use with complete() method
        
        Note:
            When compress_output=True, the input prompt size will increase due to
            compression instructions. The benefit is that the model's output will
            also be compressed, potentially saving tokens on the response.
        
        Raises:
            APIKeyError: If API key is not provided and not found in environment
        """
        self.model = model
        self.compress_output = compress_output
        self.use_optimal = use_optimal
        
        # Cache LLM provider and API key for complete() method
        self.llm_provider = llm_provider
        self.llm_api_key = llm_api_key
        
        # Initialize API client (uses production URL by default, can be overridden via PCOMPRESLR_API_URL env var)
        self.api_client = PcompresslrAPIClient(api_key=api_key)
        
        # Compression state - set after compress() is called
        self.original_prompt = None
        self.compressed_text = None
        self.decompression_dict = None
        self.compression_ratio = None
        self.llm_format = None
        self.processing_time_ms = None
        self.output_instruction = None
        self.final_prompt = None
    
    def compress(
        self,
        prompt: str,
        model: Optional[str] = None,
        use_optimal: Optional[bool] = None,
        compress_output: Optional[bool] = None
    ) -> str:
        """
        Compress a prompt.
        
        Args:
            prompt: The prompt text to compress
            model: LLM model name. If None, uses the model from constructor.
            use_optimal: Whether to use optimal algorithm. If None, uses constructor setting.
            compress_output: Whether to enable output compression. If None, uses constructor setting.
        
        Returns:
            The compressed prompt ready to send to the LLM
        
        Raises:
            APIKeyError: If API key is invalid
            RateLimitError: If rate limit is exceeded
            APIRequestError: For other API errors
        """
        # Use provided parameters or fall back to constructor settings
        model_to_use = model if model is not None else self.model
        use_optimal_to_use = use_optimal if use_optimal is not None else self.use_optimal
        compress_output_to_use = compress_output if compress_output is not None else self.compress_output
        
        # Store prompt
        self.original_prompt = prompt
        
        # Compress the input prompt via API
        algorithm = "optimal" if use_optimal_to_use else "greedy"
        try:
            result = self.api_client.compress(
                prompt=prompt,
                model=model_to_use,
                algorithm=algorithm
            )
        except APIKeyError as e:
            raise APIKeyError(
                f"{str(e)}\n\n"
                "To get an API key, visit https://compress.lightreach.io or "
                "set the PCOMPRESLR_API_KEY environment variable."
            ) from e
        except RateLimitError as e:
            raise RateLimitError(
                f"{str(e)}\n\n"
                "You've exceeded your rate limit. Please wait before making more requests, "
                "or upgrade your subscription plan."
            ) from e
        except APIRequestError as e:
            raise APIRequestError(
                f"{str(e)}\n\n"
                "If this problem persists, please check https://compress.lightreach.io/status "
                "or contact support."
            ) from e
        
        # Extract results from API response
        self.compressed_text = result["compressed"]
        self.decompression_dict = result["dictionary"]
        self.compression_ratio = result["compression_ratio"]
        self.llm_format = result["llm_format"]
        self.processing_time_ms = result["processing_time_ms"]
        
        # If output compression is enabled, add instructions to the prompt
        if compress_output_to_use:
            self.output_instruction = self._generate_output_instruction()
            self.final_prompt = self._build_prompt_with_output_compression()
        else:
            self.output_instruction = None
            self.final_prompt = self.llm_format
        
        return self.final_prompt
    
    def _generate_output_instruction(self) -> str:
        """
        Generate a concise instruction telling the model to compress its output.
        This instruction is optimized to be as short as possible while being clear.
        
        The instruction uses the same compression format as the input, making it
        easy for the model to understand and follow.
        
        Returns:
            A string instruction for the model
        """
        # Ultra-concise instruction optimized for minimal token usage
        # Format: DICT:key=value;key2=value2|PROMPT:compressed_text
        # This instruction is designed to be:
        # 1. As short as possible (minimize input size increase)
        # 2. Clear and unambiguous
        # 3. Uses the same format as input (familiar to model)
        
        # Minimal instruction - tested to work well with GPT-4, Claude, etc.
        # Using brackets and concise language to minimize tokens
        # The model sees the input format, so it understands the pattern
        instruction = (
            "\n\n[Output: DICT:k=v|PROMPT:text. Compress repeats.]"
        )
        
        return instruction
    
    def _build_prompt_with_output_compression(self) -> str:
        """
        Build the final prompt that includes both compressed input and output instructions.
        
        Returns:
            The complete prompt ready to send to the model
        """
        return self.llm_format + self.output_instruction
    
    def get_compressed_prompt(self) -> str:
        """
        Get the compressed prompt ready to send to the LLM.
        
        Returns:
            The compressed prompt (with dictionary and optional output instructions)
        
        Raises:
            ValueError: If compress() has not been called yet
        """
        if self.final_prompt is None:
            raise ValueError(
                "No compressed prompt available. Call compress() first."
            )
        return self.final_prompt
    
    def get_input_size_increase(self) -> Tuple[int, float]:
        """
        Calculate how much the input size increased due to output compression instructions.
        Only meaningful when compress_output=True.
        
        Returns:
            Tuple of (additional_tokens, additional_chars)
        """
        if not self.compress_output:
            return 0, 0
        
        # Estimate tokens using tiktoken if available, otherwise approximate
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model)
            instruction_tokens = len(encoding.encode(self.output_instruction))
        except:
            # Fallback: approximate 1 token = 4 chars
            instruction_tokens = len(self.output_instruction) // 4
        
        instruction_chars = len(self.output_instruction)
        
        return instruction_tokens, instruction_chars
    
    def decompress_output(self, model_response: str) -> str:
        """
        Decompress the model's compressed output.
        
        Args:
            model_response: The compressed response from the model
        
        Returns:
            The decompressed response
        
        Raises:
            ValueError: If compress_output was False
            APIRequestError: If decompression API call fails
        """
        if not self.compress_output:
            raise ValueError(
                "compress_output was False. Cannot decompress output. "
                "Set compress_output=True when initializing Pcompresslr."
            )
        
        # Decompress using the API
        try:
            result = self.api_client.decompress(model_response)
            return result["decompressed"]
        except APIRequestError as e:
            # If decompression fails, return original (model might not have followed format)
            # But log a warning
            import warnings
            warnings.warn(
                f"Failed to decompress model output via API. The model may not have followed "
                f"the compression format. Error: {e}. Returning original response.",
                UserWarning
            )
            return model_response
    
    def get_compression_stats(self) -> Dict:
        """
        Get statistics about the compression.
        
        Returns:
            Dictionary with compression statistics
        
        Raises:
            ValueError: If compress() has not been called yet
        """
        if self.original_prompt is None or self.final_prompt is None:
            raise ValueError(
                "No compression data available. Call compress() first."
            )
        
        # Estimate tokens using tiktoken if available, otherwise approximate
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model)
            original_tokens = len(encoding.encode(self.original_prompt))
            compressed_tokens = len(encoding.encode(self.final_prompt))
        except:
            # Fallback: approximate 1 token = 4 chars
            original_tokens = len(self.original_prompt) // 4
            compressed_tokens = len(self.final_prompt) // 4
        
        stats = {
            "original_size_chars": len(self.original_prompt),
            "compressed_size_chars": len(self.final_prompt),
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "compression_ratio": self.compression_ratio,
            "token_savings": original_tokens - compressed_tokens,
            "token_savings_percent": (1 - compressed_tokens / original_tokens) * 100 if original_tokens > 0 else 0,
            "processing_time_ms": getattr(self, 'processing_time_ms', None),
        }
        
        if self.compress_output:
            instruction_tokens, instruction_chars = self.get_input_size_increase()
            stats["output_compression_enabled"] = True
            stats["instruction_tokens"] = instruction_tokens
            stats["instruction_chars"] = instruction_chars
        else:
            stats["output_compression_enabled"] = False
        
        return stats
    
    def set_llm_key(self, provider: str, api_key: str):
        """
        Set LLM provider API key for use with complete() method.
        
        Args:
            provider: LLM provider ('openai' or 'anthropic')
            api_key: LLM provider API key
        """
        if provider not in ["openai", "anthropic"]:
            raise ValueError(f"Unsupported provider: {provider}. Must be 'openai' or 'anthropic'")
        self.llm_provider = provider
        self.llm_api_key = api_key
    
    def clear_llm_key(self):
        """Clear cached LLM provider API key."""
        self.llm_provider = None
        self.llm_api_key = None
    
    def has_llm_key(self) -> bool:
        """Check if LLM API key is set."""
        return self.llm_provider is not None and self.llm_api_key is not None
    
    def complete(
        self,
        prompt: Optional[str] = None,
        model: Optional[str] = None,
        llm_provider: Optional[str] = None,
        llm_api_key: Optional[str] = None,
        compress: bool = True,
        compress_output: bool = False,
        use_optimal: Optional[bool] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict:
        """
        Complete a prompt with compression, LLM call, and decompression in one request.
        
        Args:
            prompt: The prompt to complete. If None, uses the prompt from constructor.
            model: LLM model name. If None, uses the model from constructor.
            llm_provider: LLM provider ('openai' or 'anthropic'). If None, uses cached provider or requires it.
            llm_api_key: LLM provider API key. If None, uses cached key or requires it.
            compress: Whether to compress the prompt (default: True)
            compress_output: Whether to request compressed output from LLM (default: False)
            use_optimal: Whether to use optimal algorithm. If None, uses constructor setting.
            temperature: LLM temperature setting (optional)
            max_tokens: Maximum tokens to generate (optional)
        
        Returns:
            Dictionary containing:
                - decompressed_response: Final decompressed response
                - compressed_prompt: Compressed prompt sent to LLM (if compression enabled)
                - raw_llm_response: Raw LLM response before decompression (if output compression enabled)
                - compression_stats: Input compression statistics
                - llm_stats: LLM usage statistics
                - warnings: Any warnings
        
        Raises:
            ValueError: If LLM provider/key not provided and not cached
            APIKeyError: If API key is invalid
            RateLimitError: If rate limit is exceeded
            APIRequestError: For other API errors
        """
        # Prompt is required for complete()
        if prompt is None:
            raise ValueError(
                "prompt is required for complete(). Provide it as a parameter."
            )
        prompt_to_use = prompt
        
        # Use model from parameter or constructor
        model_to_use = model if model is not None else self.model
        
        # Get LLM provider - from parameter, cached, or error
        provider_to_use = llm_provider or self.llm_provider
        if not provider_to_use:
            raise ValueError(
                "LLM provider is required. Provide it as a parameter or set it in constructor/set_llm_key()."
            )
        
        # Get LLM API key - from parameter, cached, or error
        key_to_use = llm_api_key or self.llm_api_key
        if not key_to_use:
            raise ValueError(
                "LLM API key is required. Provide it as a parameter or set it in constructor/set_llm_key()."
            )
        
        # Cache the provider and key if provided
        if llm_provider and llm_api_key:
            self.llm_provider = llm_provider
            self.llm_api_key = llm_api_key
        
        # Determine algorithm
        algorithm = "optimal" if (use_optimal if use_optimal is not None else self.use_optimal) else "greedy"
        
        # Make the complete request
        try:
            result = self.api_client.complete(
                prompt=prompt_to_use,
                model=model_to_use,
                llm_provider=provider_to_use,
                llm_api_key=key_to_use,
                compress=compress,
                compress_output=compress_output,
                algorithm=algorithm,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except APIKeyError as e:
            raise APIKeyError(
                f"{str(e)}\n\n"
                "To get an API key, visit https://compress.lightreach.io or "
                "set the PCOMPRESLR_API_KEY environment variable."
            ) from e
        except RateLimitError as e:
            raise RateLimitError(
                f"{str(e)}\n\n"
                "You've exceeded your rate limit. Please wait before making more requests, "
                "or upgrade your subscription plan."
            ) from e
        except APIRequestError as e:
            raise APIRequestError(
                f"{str(e)}\n\n"
                "If this problem persists, please check https://compress.lightreach.io/status "
                "or contact support."
            ) from e
        
        return result

