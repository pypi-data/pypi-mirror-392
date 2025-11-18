class OpenRouterError(Exception):
    """Base exception for OpenRouter errors."""
    pass


class InvalidKeyError(OpenRouterError):
    """Raised when an API key is invalid."""
    pass


class RateLimitError(OpenRouterError):
    """Raised when rate limit is exceeded."""
    pass


class AllKeysExhausted(OpenRouterError):
    """Raised when all API keys have reached their limits."""
    pass


class ModelNotFoundError(OpenRouterError):
    """Raised when specified model is not available."""
    pass
