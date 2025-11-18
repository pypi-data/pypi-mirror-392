"""Direct Chat Endpoint Provider - Production-Ready Implementation.

This provider uses raw HTTP requests to call any OpenAI-compatible chat completion
endpoint directly, bypassing the OpenAI SDK. This is useful for custom endpoints,
self-hosted models, or any API that follows the OpenAI chat completions format.

Features:
- Direct HTTP POST requests to any endpoint
- No OpenAI SDK dependency for API calls
- Full control over request headers and payload
- Automatic retry with exponential backoff and jitter
- Comprehensive error handling and logging
- Production-ready with circuit breaker support

Limitations:
- Does NOT support streaming (non-streaming only)
- Assumes OpenAI-compatible request/response format
- Tool calling support depends on endpoint compatibility

Author: OmniGen Team
License: MIT
"""

import time
import random
from typing import List, Dict, Optional, Any, Tuple, Union
from omnigen.core.base import BaseLLMProvider
from omnigen.core.types import Message
from omnigen.core.exceptions import (
    ProviderError, APIError, RateLimitError, AuthenticationError,
    TimeoutError, NetworkError, ServerError
)
from omnigen.utils.logger import setup_logger

# Try to import requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

logger = setup_logger()


class DirectChatEndpointProvider(BaseLLMProvider):
    """
    Production-ready provider for direct chat completion endpoints.
    
    This provider makes raw HTTP requests to any OpenAI-compatible chat completion
    endpoint without using the OpenAI SDK. Perfect for custom endpoints, self-hosted
    models, or when you need complete control over the HTTP request.
    
    Configuration:
        Required:
        - endpoint_url: Full URL to the chat completions endpoint
        - model: Model name to use in requests
        
        Optional:
        - api_key: API key for authentication (sent in Authorization: Bearer header)
        - temperature: Sampling temperature (default: 0.7)
        - max_tokens: Maximum tokens to generate (default: 4096)
        - headers: Additional HTTP headers as dict (e.g., custom auth, tracking)
        - timeout: Request timeout in seconds (default: 60)
        - max_retries: Maximum retry attempts for transient errors (default: 3)
        - retry_delay: Base retry delay in seconds (default: 2)
        - use_streaming: Must be False (streaming not supported, default: False)
    
    Example configuration:
        ```yaml
        providers:
          assistant_response:
            name: direct_chat_endpoint
            endpoint_url: "https://api.example.com/v1/chat/completions"
            api_key: ${MY_API_KEY}
            model: "my-custom-model"
            temperature: 0.7
            max_tokens: 8192
            timeout: 90
            headers:
              X-Custom-Header: "my-value"
              HTTP-Referer: "https://myapp.com"
            use_streaming: false
        ```
    
    Endpoint Requirements:
        The endpoint must accept POST requests with JSON body:
        ```json
        {
            "model": "model-name",
            "messages": [{"role": "user", "content": "..."}],
            "temperature": 0.7,
            "max_tokens": 4096,
            "stream": false
        }
        ```
        
        And return OpenAI-compatible JSON response:
        ```json
        {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "...",
                    "tool_calls": [...]  // optional
                }
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        ```
    
    Error Handling:
        - 429: Rate limit - automatically retries with exponential backoff
        - 401/403: Authentication error - fails immediately
        - 500/502/503: Server error - retries with backoff
        - Timeout: Connection timeout - retries with backoff
        - Network errors: Connection errors - retries with backoff
    
    Note: Streaming is NOT supported. Always set use_streaming=False.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize direct chat endpoint provider.
        
        Args:
            config: Provider configuration dictionary
            
        Raises:
            ImportError: If requests library is not installed
            ProviderError: If streaming is enabled
            ValueError: If required configuration is missing
        """
        try:
            super().__init__(config)
            
            # Check requests library availability
            if not REQUESTS_AVAILABLE:
                raise ImportError(
                    "requests library is required for direct_chat_endpoint provider. "
                    "Install with: pip install requests"
                )
            
            # Validate streaming is disabled
            if self.use_streaming:
                raise ProviderError(
                    "direct_chat_endpoint provider does not support streaming. "
                    "Set use_streaming=False in provider configuration."
                )
            
            # Validate required configuration
            self.endpoint_url = config.get('endpoint_url')
            if not self.endpoint_url:
                raise ValueError(
                    "endpoint_url is required for direct_chat_endpoint provider. "
                    "Specify the full URL: https://api.example.com/v1/chat/completions"
                )
            
            self.model = config.get('model')
            if not self.model:
                raise ValueError(
                    "model is required for direct_chat_endpoint provider. "
                    "Specify the model name to use in requests."
                )
            
            # Optional configuration with defaults
            self.api_key = config.get('api_key')  # Optional - some endpoints don't need auth
            self.timeout = config.get('timeout', 60)
            self.max_retries = config.get('max_retries', 3)
            self.retry_delay = config.get('retry_delay', 2)
            
            # Validate timeout
            if self.timeout <= 0:
                logger.warning(f"Invalid timeout {self.timeout}, using default 60s")
                self.timeout = 60
            
            # Build headers
            self.headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }
            
            # Add authorization if API key provided
            if self.api_key:
                self.headers['Authorization'] = f'Bearer {self.api_key}'
            
            # Add custom headers if provided
            custom_headers = config.get('headers', {})
            if custom_headers and isinstance(custom_headers, dict):
                self.headers.update(custom_headers)
            elif custom_headers:
                logger.warning(f"Invalid headers configuration (not a dict): {type(custom_headers)}")
            
            logger.info(
                f"Direct chat endpoint provider initialized successfully: "
                f"{self.endpoint_url} (model: {self.model}, timeout: {self.timeout}s)"
            )
            
        except (ValueError, ProviderError, ImportError):
            # Re-raise these specific errors
            raise
        except Exception as e:
            # Catch any unexpected initialization errors
            logger.critical(
                f"Critical error initializing direct_chat_endpoint provider: {e}",
                exc_info=True
            )
            raise ProviderError(f"Failed to initialize direct_chat_endpoint provider: {e}")
    
    def chat_completion(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        return_usage: bool = False,
        **kwargs
    ) -> Union[str, Tuple[str, Dict], Dict, Tuple[Dict, Dict]]:
        """
        Generate chat completion via direct HTTP POST request.
        
        Args:
            messages: List of conversation messages
            model: Model name override (uses config model if not specified)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            return_usage: If True, return tuple of (content, usage_dict)
            **kwargs: Additional parameters to include in request payload
            
        Returns:
            - str: Generated text content (if return_usage=False and no tool calls)
            - Dict: Message dict with tool_calls (if tool calls present)
            - Tuple[str, Dict]: (content, usage) if return_usage=True
            - Tuple[Dict, Dict]: (message_dict, usage) if return_usage=True and tool calls
            
        Raises:
            RateLimitError: Rate limit exceeded after retries
            TimeoutError: Request timeout after retries
            AuthenticationError: Authentication failed (401/403)
            ServerError: Server error after retries (500/502/503)
            NetworkError: Network/connection error after retries
            APIError: Other API errors
            
        Example:
            >>> provider = DirectChatEndpointProvider(config)
            >>> messages = [{"role": "user", "content": "Hello"}]
            >>> response = provider.chat_completion(messages)
            >>> print(response)
            "Hello! How can I help you?"
        """
        try:
            model = model or self.model
            formatted_messages = self._prepare_messages(messages)
            
            # Build request payload (OpenAI-compatible format)
            payload = {
                'model': model,
                'messages': formatted_messages,
                'temperature': temperature,
                'stream': False,  # Explicitly disable streaming
            }
            
            # Add max_tokens if specified
            if max_tokens is not None:
                payload['max_tokens'] = max_tokens
            
            # Add any additional kwargs to payload
            # These could be provider-specific parameters like top_p, frequency_penalty, etc.
            if kwargs:
                payload.update(kwargs)
            
            # Retry loop with exponential backoff
            last_exception = None
            for attempt in range(self.max_retries):
                try:
                    # Make HTTP POST request
                    logger.debug(
                        f"Sending request to {self.endpoint_url} "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    
                    response = requests.post(
                        self.endpoint_url,
                        headers=self.headers,
                        json=payload,
                        timeout=self.timeout
                    )
                    
                    # Handle HTTP error status codes
                    if response.status_code == 429:
                        # Rate limit - retry with exponential backoff and jitter
                        if attempt < self.max_retries - 1:
                            wait_time = self.retry_delay * (2 ** attempt)
                            jitter = random.uniform(0, wait_time * 0.1)
                            wait_time += jitter
                            logger.warning(
                                f"Rate limit hit (429), waiting {wait_time:.1f}s before retry "
                                f"(attempt {attempt + 1}/{self.max_retries})"
                            )
                            time.sleep(wait_time)
                            continue
                        raise RateLimitError(
                            f"Rate limit exceeded after {self.max_retries} attempts: {response.text}"
                        )
                    
                    elif response.status_code in [401, 403]:
                        # Authentication error - don't retry, fail immediately
                        error_detail = response.text[:500] if response.text else "No error details"
                        raise AuthenticationError(
                            f"Authentication failed (HTTP {response.status_code}): {error_detail}"
                        )
                    
                    elif response.status_code >= 500:
                        # Server error - retry with backoff
                        if attempt < self.max_retries - 1:
                            wait_time = self.retry_delay * (attempt + 1)
                            logger.warning(
                                f"Server error {response.status_code}, retrying in {wait_time}s "
                                f"(attempt {attempt + 1}/{self.max_retries})"
                            )
                            time.sleep(wait_time)
                            continue
                        error_detail = response.text[:500] if response.text else "No error details"
                        raise ServerError(
                            f"Server error {response.status_code} after {self.max_retries} attempts: "
                            f"{error_detail}"
                        )
                    
                    elif response.status_code != 200:
                        # Other HTTP error - don't retry
                        error_detail = response.text[:500] if response.text else "No error details"
                        raise APIError(
                            f"API error (HTTP {response.status_code}): {error_detail}"
                        )
                    
                    # Parse JSON response
                    try:
                        response_data = response.json()
                    except Exception as e:
                        raise APIError(f"Failed to parse JSON response: {e}. Response: {response.text[:200]}")
                    
                    # Validate response structure (OpenAI-compatible)
                    if 'choices' not in response_data:
                        raise APIError(f"Invalid response: missing 'choices' field. Response: {response_data}")
                    
                    if not response_data['choices']:
                        raise APIError(f"Invalid response: empty 'choices' array. Response: {response_data}")
                    
                    # Extract message from first choice
                    choice = response_data['choices'][0]
                    message = choice.get('message', {})
                    
                    if not message:
                        raise APIError(f"Invalid response: missing 'message' in choice. Response: {response_data}")
                    
                    # Extract content and tool_calls
                    content = message.get('content', '').strip() if message.get('content') else ''
                    tool_calls = message.get('tool_calls')
                    
                    # Extract token usage if available
                    usage = {}
                    if 'usage' in response_data:
                        usage_data = response_data['usage']
                        usage = {
                            'input_tokens': usage_data.get('prompt_tokens', 0),
                            'output_tokens': usage_data.get('completion_tokens', 0),
                            'total_tokens': usage_data.get('total_tokens', 0)
                        }
                    
                    # Handle different response types
                    if tool_calls:
                        # Tool calling response - return full message dict
                        if return_usage:
                            return message, usage
                        return message
                    
                    elif content:
                        # Regular text response
                        if return_usage:
                            return content, usage
                        return content
                    
                    else:
                        # Empty response - this might be valid for some use cases
                        logger.warning(f"Empty response from endpoint (no content or tool_calls)")
                        if return_usage:
                            return "", usage
                        return ""
                    
                except requests.exceptions.Timeout:
                    # Connection timeout - retry
                    last_exception = TimeoutError("Request timeout")
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (attempt + 1)
                        logger.warning(
                            f"Request timeout, retrying in {wait_time}s "
                            f"(attempt {attempt + 1}/{self.max_retries})"
                        )
                        time.sleep(wait_time)
                        continue
                    raise TimeoutError(f"Request timeout after {self.max_retries} attempts")
                
                except requests.exceptions.ConnectionError as e:
                    # Network/connection error - retry
                    last_exception = NetworkError(f"Connection error: {e}")
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (attempt + 1)
                        logger.warning(
                            f"Connection error, retrying in {wait_time}s "
                            f"(attempt {attempt + 1}/{self.max_retries}): {e}"
                        )
                        time.sleep(wait_time)
                        continue
                    raise NetworkError(f"Connection error after {self.max_retries} attempts: {e}")
                
                except (RateLimitError, AuthenticationError, ServerError, APIError):
                    # Re-raise these specific errors
                    raise
                
                except Exception as e:
                    # Unexpected error - log and retry once
                    last_exception = APIError(f"Unexpected error: {e}")
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (attempt + 1)
                        logger.warning(
                            f"Unexpected error, retrying in {wait_time}s "
                            f"(attempt {attempt + 1}/{self.max_retries}): {e}",
                            exc_info=True
                        )
                        time.sleep(wait_time)
                        continue
                    raise APIError(f"Unexpected error after {self.max_retries} attempts: {e}")
            
            # If we get here, all retries failed
            if last_exception:
                raise last_exception
            raise APIError(f"Max retries ({self.max_retries}) exceeded")
            
        except (RateLimitError, TimeoutError, AuthenticationError, ServerError, NetworkError, APIError):
            # Re-raise expected errors
            raise
        except Exception as e:
            # Catch any unexpected errors
            logger.critical(f"Unexpected error in chat_completion: {e}", exc_info=True)
            raise APIError(f"Unexpected error: {e}")
    
    def validate_config(self) -> bool:
        """
        Validate provider configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.endpoint_url:
            raise ValueError("endpoint_url is required")
        
        if not self.model:
            raise ValueError("model is required")
        
        if self.use_streaming:
            raise ValueError("direct_chat_endpoint provider does not support streaming")
        
        if self.timeout <= 0:
            raise ValueError(f"Invalid timeout: {self.timeout} (must be > 0)")
        
        if self.max_retries < 0:
            raise ValueError(f"Invalid max_retries: {self.max_retries} (must be >= 0)")
        
        return True
